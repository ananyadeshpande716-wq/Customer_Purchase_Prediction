
"""Integration test for prediction inference and MongoDB storage."""

from uuid import uuid4

from bson import ObjectId

from src.mongodb import get_database
from src.prediction_service import (
    get_prediction_history,
    predict_and_save_purchase,
)


def main():
    test_customer_id = f"PRED-TEST-{uuid4().hex[:12]}"
    inserted_prediction_id = None

    features = {
        "recency_days": 12.5,
        "orders_last_90d": 2,
        "spend_last_90d": 250.0,
        "quantity_last_90d": 8,
        "unique_products_last_90d": 4,
        "avg_order_value_90d": 125.0,
    }

    try:
        # Generate a prediction and save it.
        result = predict_and_save_purchase(
            customer_id=test_customer_id,
            features=features,
        )

        inserted_prediction_id = result["prediction_id"]

        assert result["prediction_id"]
        assert 0 <= result["purchase_probability"] <= 1
        assert result["predicted_purchase"] in (0, 1)

        print("Prediction generated successfully.")
        print(
            "Purchase probability:",
            f"{result['purchase_probability']:.2%}",
        )
        print("Predicted class:", result["predicted_purchase"])
        print("MongoDB record ID:", inserted_prediction_id)

        # Retrieve the saved prediction.
        history = get_prediction_history(
            customer_id=test_customer_id,
            limit=5,
        )

        assert len(history) == 1
        assert history[0]["customer_id"] == test_customer_id
        assert history[0]["model_version"] == result["model_version"]

        print("Prediction saved and retrieved successfully.")
        print("Prediction service test passed.")

    finally:
        # Remove only the temporary record created by this test.
        if inserted_prediction_id is not None:
            get_database()["prediction_history"].delete_one(
                {"_id": ObjectId(inserted_prediction_id)}
            )


if __name__ == "__main__":
    main()
