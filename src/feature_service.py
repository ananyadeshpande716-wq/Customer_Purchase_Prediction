
"""Retrieve and validate customer purchase features from MongoDB."""

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
