
"""Generate purchase predictions and store their history in MongoDB."""
from src.feature_service import get_customer_features
from datetime import datetime, timezone
from typing import Mapping, Any

from src.mongodb import get_database
from src.predictor import predict_purchase


def predict_and_save_purchase(
    customer_id: str,
    features: Mapping[str, Any],
    feature_snapshot_date=None,
) -> dict:
    """
    Generate a purchase prediction and persist it in MongoDB.

    Returns the prediction result along with its database record ID.
    """

    if not isinstance(customer_id, str) or not customer_id.strip():
        raise ValueError("A valid customer ID is required.")

    customer_id = customer_id.strip()

    if len(customer_id) > 50:
        raise ValueError("Customer ID cannot exceed 50 characters.")

    # Generate the prediction using the saved model.
    prediction = predict_purchase(
        features=features,
        customer_id=customer_id,
    )

    # Prepare a MongoDB document.
    created_at = datetime.now(timezone.utc)

    document = {
        "customer_id": customer_id,
        "purchase_probability": prediction["purchase_probability"],
        "predicted_purchase": prediction["predicted_purchase"],
        "threshold": prediction["threshold"],
        "model_name": prediction["model_name"],
        "model_version": prediction["model_version"],
        "history_days": prediction["history_days"],
        "target_days": prediction["target_days"],
        "features": prediction["features"],
        "created_at": created_at,
        "feature_snapshot_date": feature_snapshot_date,
    }

    # Store the result in MongoDB Atlas.
    collection = get_database()["prediction_history"]
    result = collection.insert_one(document)

    return {
        **prediction,
        "prediction_id": str(result.inserted_id),
        "created_at": created_at.isoformat(),
    }


def get_prediction_history(
    customer_id: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Retrieve recent prediction records, optionally by customer."""

    if (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or not 1 <= limit <= 100
    ):
        raise ValueError("Limit must be an integer between 1 and 100.")

    query = {}

    if customer_id is not None:
        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ValueError("Customer ID must be a non-empty string.")

        query["customer_id"] = customer_id.strip()

    collection = get_database()["prediction_history"]

    return list(
        collection.find(query, {"_id": 0})
        .sort("created_at", -1)
        .limit(limit)
    )

def predict_customer_by_id(customer_id: str) -> dict:
    """
    Retrieve a customer's latest available feature snapshot,
    generate a purchase prediction, and save it to MongoDB.
    """

    customer_data = get_customer_features(customer_id)

    if customer_data is None:
        raise LookupError(
            f"No purchase feature history found for customer "
            f"'{customer_id}'."
        )

    result = predict_and_save_purchase(
        customer_id=customer_data["customer_id"],
        features=customer_data["features"],
        feature_snapshot_date=customer_data["snapshot_date"],
    )

    result["feature_snapshot_date"] = (
        customer_data["snapshot_date"].isoformat()
        if customer_data["snapshot_date"] is not None
        else None
    )

    return result