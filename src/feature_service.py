
"""Retrieve and validate customer purchase features from MongoDB."""
import re

from src.customer_service import get_customer
from src.mongodb import get_database
from src.predictor import EXPECTED_FEATURES, validate_features


def get_feature_collection():
    """Return the collection containing customer feature snapshots."""
    return get_database()["customer_features"]


def get_customer_features(customer_id: str | int) -> dict | None:
    """
    Retrieve the latest available feature snapshot for a customer.

    Returns None when no feature record exists for the customer.
    """

    if isinstance(customer_id, bool) or customer_id is None:
        raise ValueError("A valid customer ID is required.")

    customer_id = str(customer_id).strip()

    if not customer_id or len(customer_id) > 50:
        raise ValueError("Customer ID must contain 1–50 characters.")

    # Fetch the latest available snapshot for this customer.
    projection = {
        "_id": 0,
        "customer_id": 1,
        "snapshot_date": 1,
    }

    for feature_name in EXPECTED_FEATURES:
        projection[feature_name] = 1

    document = get_feature_collection().find_one(
        {"customer_id": customer_id},
        projection,
        sort=[("snapshot_date", -1)],
    )

    if document is None:
        return None

    # Check that the document contains all required model inputs.
    missing_features = [
        name
        for name in EXPECTED_FEATURES
        if name not in document or document[name] is None
    ]

    if missing_features:
        raise ValueError(
            f"Customer {customer_id} has an incomplete feature record: "
            f"{missing_features}"
        )

    # Reuse the validation rules from the prediction module.
    features = validate_features({
        name: document[name]
        for name in EXPECTED_FEATURES
    })

    return {
        "customer_id": document["customer_id"],
        "snapshot_date": document.get("snapshot_date"),
        "features": features,
    }


def get_customer_prediction_status(customer_id: str | int) -> dict:
    """
    Check whether a customer has a profile and usable purchase features.

    A customer can be predicted only when a valid feature snapshot exists.
    A profile record alone is not sufficient.
    """

    customer_id = str(customer_id).strip()

    if not customer_id or len(customer_id) > 50:
        raise ValueError("Customer ID must contain 1–50 characters.")

    profile = get_customer(customer_id)
    feature_snapshot = get_customer_features(customer_id)

    profile_exists = profile is not None
    has_history = feature_snapshot is not None

    if has_history and profile_exists:
        message = "Customer profile and purchase history are available."
    elif has_history:
        message = (
            "Purchase history is available, but no customer profile "
            "has been registered."
        )
    elif profile_exists:
        message = (
            "Customer profile exists, but no usable purchase history "
            "is available. Prediction cannot be performed."
        )
    else:
        message = (
            "No customer profile or usable purchase history was found."
        )

    return {
        "customer_id": customer_id,
        "profile_exists": profile_exists,
        "has_purchase_history": has_history,
        "can_predict": has_history,
        "snapshot_date": (
            feature_snapshot["snapshot_date"]
            if has_history
            else None
        ),
        "message": message,
    }


def list_prediction_ready_customers(
    search_text: str = "",
    limit: int = 100,
) -> list[dict]:
    """
    List distinct customers with available feature snapshots.

    Results are ordered by the latest available snapshot date.
    The limit is capped at 100 records.
    """

    if not isinstance(search_text, str):
        raise ValueError("Search text must be a string.")

    search_text = search_text.strip()

    if len(search_text) > 100:
        raise ValueError("Search text cannot exceed 100 characters.")

    if (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or not 1 <= limit <= 100
    ):
        raise ValueError("Limit must be an integer between 1 and 100.")

    pipeline = []

    if search_text:
        pipeline.append({
            "$match": {
                "customer_id": {
                    "$regex": re.escape(search_text),
                    "$options": "i",
                }
            }
        })

    pipeline.extend([
        {"$sort": {"snapshot_date": -1}},
        {
            "$group": {
                "_id": "$customer_id",
                "snapshot_date": {"$first": "$snapshot_date"},
            }
        },
        {"$sort": {"snapshot_date": -1, "_id": 1}},
        {"$limit": limit},
        {
            "$project": {
                "_id": 0,
                "customer_id": "$_id",
                "snapshot_date": 1,
            }
        },
    ])

    return list(
        get_feature_collection().aggregate(pipeline)
    )
