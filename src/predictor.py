
"""Load the trained purchase model and generate predictions."""

import math
from pathlib import Path
from typing import Mapping

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "purchase_prediction_model.joblib"

EXPECTED_FEATURES = [
    "recency_days",
    "orders_last_90d",
    "spend_last_90d",
    "quantity_last_90d",
    "unique_products_last_90d",
    "avg_order_value_90d",
]

_model_artifact = None


def load_model_artifact() -> dict:
    """Load and validate the saved model artifact once."""

    global _model_artifact

    if _model_artifact is not None:
        return _model_artifact

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Trained model not found at {MODEL_PATH}. "
            "Copy the model artifact exported from Google Colab "
            "into the project's models folder."
        )

    artifact = joblib.load(MODEL_PATH)

    if not isinstance(artifact, dict):
        raise ValueError("Unexpected model artifact format.")

    model = artifact.get("model")
    features = artifact.get("features")
    threshold = artifact.get("threshold")

    if model is None or not hasattr(model, "predict_proba"):
        raise ValueError("Artifact does not contain a probability-capable model.")

    if features != EXPECTED_FEATURES:
        raise ValueError(
            "The model's feature names or order do not match "
            "the expected application inputs."
        )

    if not isinstance(threshold, (int, float)):
        raise ValueError("Model decision threshold is missing or invalid.")

    if not 0 <= threshold <= 1:
        raise ValueError("Model decision threshold must be between 0 and 1.")

    if 1 not in list(model.classes_):
        raise ValueError("The trained model does not contain purchase class 1.")

    _model_artifact = artifact
    return _model_artifact


def validate_features(features: Mapping) -> dict:
    """Validate historical customer features before inference."""

    if not isinstance(features, Mapping):
        raise ValueError("Features must be supplied as a dictionary.")

    missing = [
        name for name in EXPECTED_FEATURES
        if name not in features
    ]

    if missing:
        raise ValueError(f"Missing required features: {missing}")

    values = {}

    for name in EXPECTED_FEATURES:
        value = features[name]

        if isinstance(value, bool):
            raise ValueError(f"{name} must be numeric, not boolean.")

        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be numeric.") from None

        if not math.isfinite(number):
            raise ValueError(f"{name} must be a finite number.")

        values[name] = number

    # The model was trained on customers with purchase activity
    # in the preceding 90-day history window.
    if not 0 <= values["recency_days"] <= 90:
        raise ValueError("recency_days must be between 0 and 90.")

    for name in (
        "orders_last_90d",
        "quantity_last_90d",
        "unique_products_last_90d",
    ):
        number = values[name]

        if number < 1 or not number.is_integer():
            raise ValueError(f"{name} must be a positive whole number.")

    for name in ("spend_last_90d", "avg_order_value_90d"):
        if values[name] <= 0:
            raise ValueError(f"{name} must be greater than zero.")

    return values


def predict_purchase(
    features: Mapping,
    customer_id: str | None = None,
) -> dict:
    """
    Predict purchase probability for a customer's 90-day history.

    The positive prediction means the model estimates a purchase
    during the next 30-day target window.
    """

    artifact = load_model_artifact()
    values = validate_features(features)

    # Preserve the exact feature names and training order.
    input_df = pd.DataFrame(
        [values],
        columns=artifact["features"],
    )

    model = artifact["model"]
    classes = list(model.classes_)
    purchase_class_index = classes.index(1)

    probabilities = model.predict_proba(input_df)[0]
    purchase_probability = float(
        probabilities[purchase_class_index]
    )

    threshold = float(artifact["threshold"])
    predicted_purchase = int(purchase_probability >= threshold)

    return {
        "customer_id": (
            str(customer_id).strip()
            if customer_id is not None
            else None
        ),
        "purchase_probability": purchase_probability,
        "predicted_purchase": predicted_purchase,
        "threshold": threshold,
        "model_name": artifact.get("model_name", "Unknown"),
        "model_version": artifact.get("model_version", "Unknown"),
        "history_days": artifact.get("history_days", 90),
        "target_days": artifact.get("target_days", 30),
        "features": values,
    }
