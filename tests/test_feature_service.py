
"""Read-only integration tests for customer feature retrieval."""

from src.mongodb import get_database
from src.feature_service import get_customer_features


def main():
    collection = get_database()["customer_features"]

    # Inspect how many snapshots are actually stored.
    print("Total feature records:", collection.count_documents({}))

    snapshot_counts = list(
        collection.aggregate([
            {
                "$group": {
                    "_id": "$snapshot_date",
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ])
    )

    print("\nSnapshot dates in MongoDB:")
    for item in snapshot_counts:
        print(f"  {item['_id']}: {item['count']} records")

    # Retrieve the known customer from the earlier inspection.
    customer = get_customer_features("12347")

    assert customer is not None, (
        "Customer 12347 was not found in customer_features."
    )

    assert customer["snapshot_date"] is not None

    print("\nCustomer features retrieved successfully.")
    print("Customer ID:", customer["customer_id"])
    print("Snapshot date:", customer["snapshot_date"])
    print("Model input features:")

    for name, value in customer["features"].items():
        print(f"  {name}: {value}")

    assert len(customer["features"]) == 6

    print("\nFeature retrieval test passed.")


if __name__ == "__main__":
    main()
