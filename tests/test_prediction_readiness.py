
"""Tests for customer prediction readiness and eligible customer listing."""

from uuid import uuid4

from src.customer_service import (
    create_customer,
    delete_customer,
    initialize_customer_collection,
)
from src.feature_service import (
    get_customer_prediction_status,
    list_prediction_ready_customers,
)


def main():
    initialize_customer_collection()

    # Existing historical customer
    historical = get_customer_prediction_status("12347")

    assert historical["has_purchase_history"] is True
    assert historical["can_predict"] is True

    print("Historical customer readiness passed.")

    # A newly registered profile has no historical feature snapshot.
    test_id = f"NO-HISTORY-{uuid4().hex[:12]}"

    try:
        create_customer(
            customer_id=test_id,
            customer_name="Test Customer",
            country="India",
        )

        status = get_customer_prediction_status(test_id)

        assert status["profile_exists"] is True
        assert status["has_purchase_history"] is False
        assert status["can_predict"] is False

        print("New customer without history handled correctly.")

        # Verify the prediction-ready list can find a known customer.
        ready_customers = list_prediction_ready_customers(
            search_text="12347",
            limit=10,
        )

        assert any(
            item["customer_id"] == "12347"
            for item in ready_customers
        )

        print("Prediction-ready customer search passed.")
        print("\nAll prediction readiness checks passed.")

    finally:
        delete_customer(test_id)


if __name__ == "__main__":
    main()
