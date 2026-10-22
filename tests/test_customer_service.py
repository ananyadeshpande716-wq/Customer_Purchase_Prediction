
"""Manual integration check for customer CRUD operations."""

from uuid import uuid4

from src.customer_service import (
    create_customer,
    delete_customer,
    get_customer,
    initialize_customer_collection,
    list_customers,
    update_customer,
)


def main():
    test_id = f"CRUD-TEST-{uuid4().hex[:12]}"

    # Create the unique index before inserting records.
    initialize_customer_collection()

    try:
        # CREATE
        document_id = create_customer(
            customer_id=test_id,
            customer_name="Demo Customer",
            country="India",
            notes="Temporary integration test",
        )
        print("CREATE passed:", bool(document_id))

        # READ ONE
        customer = get_customer(test_id)
        assert customer is not None
        assert customer["customer_name"] == "Demo Customer"
        print("READ ONE passed")

        # READ MULTIPLE
        customers = list_customers(limit=100)
        assert any(c["customer_id"] == test_id for c in customers)
        print("READ MULTIPLE passed")

        # UPDATE
        updated = update_customer(
            test_id,
            customer_name="Updated Demo Customer",
            notes="Update test passed",
        )
        assert updated is True

        changed_customer = get_customer(test_id)
        assert changed_customer["customer_name"] == "Updated Demo Customer"
        print("UPDATE passed")

        # DELETE
        deleted = delete_customer(test_id)
        assert deleted is True
        assert get_customer(test_id) is None
        print("DELETE passed")

        # VALIDATION CHECK
        try:
            create_customer(
                customer_id=" ",
                customer_name="Invalid Customer",
                country="India",
            )
            raise AssertionError("Empty customer ID was accepted.")
        except ValueError:
            print("VALIDATION passed")

        print("\nAll customer CRUD checks passed.")

    finally:
        # Ensure this temporary test record is removed.
        delete_customer(test_id)


if __name__ == "__main__":
    main()
