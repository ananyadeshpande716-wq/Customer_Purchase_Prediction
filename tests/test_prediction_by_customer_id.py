"""Integration test for prediction using a customer ID."""

from bson import ObjectId

from src.mongodb import get_database
from src.prediction_service import predict_customer_by_id


def main():
    result = None

    try:
        # Customer 12347 exists in our feature collection.
        result = predict_customer_by_id("12347")

        print("Customer ID:", result["customer_id"])
        print("Feature snapshot:", result["feature_snapshot_date"])
        print(
            "Purchase probability:",
            f'{result["purchase_probability"]:.2%}',
        )
        print("Predicted class:", result["predicted_purchase"])
        print("Model:", result["model_name"])
        print("Saved prediction ID:", result["prediction_id"])

        assert 0 <= result["purchase_probability"] <= 1
        assert result["predicted_purchase"] in (0, 1)
        assert result["prediction_id"]

        print("\nCustomer ID prediction test passed.")

    finally:
        # Remove only the prediction created by this test.
        if result is not None and result.get("prediction_id"):
            get_database()["prediction_history"].delete_one(
                {"_id": ObjectId(result["prediction_id"])}
            )


if __name__ == "__main__":
    main()