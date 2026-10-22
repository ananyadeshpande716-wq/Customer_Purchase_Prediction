
"""Customer CRUD operations for the purchase prediction application."""
import re
from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from src.mongodb import get_database


def get_customers_collection() -> Collection:
    """Return the customers collection."""
    return get_database()["customers"]


def initialize_customer_collection() -> None:
    """Create a unique index for customer IDs."""
    get_customers_collection().create_index(
        [("customer_id", ASCENDING)],
        unique=True,
        name="customer_id_unique",
    )

def _validate_customer_id(customer_id: Any) -> str:
    """Convert a customer ID to a validated string."""
    if customer_id is None:
        raise ValueError("Customer ID is required.")

    customer_id = str(customer_id).strip()

    if not customer_id or len(customer_id) > 50:
        raise ValueError("Customer ID must contain 1–50 characters.")

    return customer_id


def _validate_text(
    value: Any,
    field_name: str,
    max_length: int,
) -> str:
    """Validate a required text field."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text.")

    value = value.strip()

    if not value:
        raise ValueError(f"{field_name} is required.")

    if len(value) > max_length:
        raise ValueError(
            f"{field_name} cannot exceed {max_length} characters."
        )

    return value


def create_customer(
    customer_id: str,
    customer_name: str,
    country: str,
    notes: str = "",
) -> str:
    """Create a customer and return its MongoDB document ID."""
    customer_id = _validate_customer_id(customer_id)
    customer_name = _validate_text(
        customer_name, "Customer name", 100
    )
    country = _validate_text(country, "Country", 100)

    if not isinstance(notes, str) or len(notes.strip()) > 500:
        raise ValueError("Notes must be text of at most 500 characters.")

    now = datetime.now(timezone.utc)

    document = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "country": country,
        "notes": notes.strip(),
        "created_at": now,
        "updated_at": now,
    }

    try:
        result = get_customers_collection().insert_one(document)
        return str(result.inserted_id)

    except DuplicateKeyError as exc:
        raise ValueError(
            f"Customer ID '{customer_id}' already exists."
        ) from exc


def get_customer(customer_id: str) -> dict | None:
    """Retrieve one customer by customer ID."""
    customer_id = _validate_customer_id(customer_id)

    return get_customers_collection().find_one(
        {"customer_id": customer_id},
        {"_id": 0},
    )


def list_customers(limit: int = 50) -> list[dict]:
    """Retrieve customer records, most recently updated first."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ValueError("Limit must be an integer.")

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100.")

    return list(
        get_customers_collection()
        .find({}, {"_id": 0})
        .sort("updated_at", -1)
        .limit(limit)
    )

def search_customers(
    search_text: str = "",
    country: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    Search customers by ID or name, optionally filter by country,
    and return one page of results with pagination metadata.
    """

    # Validate pagination inputs
    if (
        not isinstance(page, int)
        or isinstance(page, bool)
        or page < 1
    ):
        raise ValueError("Page must be a positive integer.")

    if (
        not isinstance(page_size, int)
        or isinstance(page_size, bool)
        or not 1 <= page_size <= 100
    ):
        raise ValueError("Page size must be between 1 and 100.")

    # Validate search text
    if not isinstance(search_text, str):
        raise ValueError("Search text must be a string.")

    search_text = search_text.strip()

    if len(search_text) > 100:
        raise ValueError("Search text cannot exceed 100 characters.")

    # Build MongoDB query filters
    filters = {}

    if search_text:
        pattern = re.escape(search_text)

        filters["$or"] = [
            {
                "customer_id": {
                    "$regex": pattern,
                    "$options": "i",
                }
            },
            {
                "customer_name": {
                    "$regex": pattern,
                    "$options": "i",
                }
            },
        ]

    if country is not None:
        if not isinstance(country, str):
            raise ValueError("Country must be a string.")

        country = country.strip()

        if not country or len(country) > 100:
            raise ValueError("Provide a valid country name.")

        filters["country"] = {
            "$regex": f"^{re.escape(country)}$",
            "$options": "i",
        }

    collection = get_customers_collection()

    # Count all records matching the filters
    total = collection.count_documents(filters)

    # Fetch only the requested page
    skip_count = (page - 1) * page_size

    records = list(
        collection.find(filters, {"_id": 0})
        .sort("updated_at", -1)
        .skip(skip_count)
        .limit(page_size)
    )

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": records,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

def update_customer(
    customer_id: str,
    customer_name: str | None = None,
    country: str | None = None,
    notes: str | None = None,
) -> bool:
    """Update provided fields. Return False if the customer is absent."""
    customer_id = _validate_customer_id(customer_id)
    updates = {}

    if customer_name is not None:
        updates["customer_name"] = _validate_text(
            customer_name, "Customer name", 100
        )

    if country is not None:
        updates["country"] = _validate_text(
            country, "Country", 100
        )

    if notes is not None:
        if not isinstance(notes, str) or len(notes.strip()) > 500:
            raise ValueError(
                "Notes must be text of at most 500 characters."
            )
        updates["notes"] = notes.strip()

    if not updates:
        raise ValueError("Provide at least one field to update.")

    updates["updated_at"] = datetime.now(timezone.utc)

    result = get_customers_collection().update_one(
        {"customer_id": customer_id},
        {"$set": updates},
    )

    return result.matched_count == 1


def delete_customer(customer_id: str) -> bool:
    """Delete one customer. Return False if no customer was found."""
    customer_id = _validate_customer_id(customer_id)

    result = get_customers_collection().delete_one(
        {"customer_id": customer_id}
    )

    return result.deleted_count == 1
