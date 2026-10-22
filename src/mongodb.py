
"""MongoDB Atlas connection utilities."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError


# Locate the project root regardless of the terminal's current directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load secrets from the local .env file.
load_dotenv(PROJECT_ROOT / ".env")

MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "customer_purchase_prediction"
).strip()

_client: MongoClient | None = None


def get_client() -> MongoClient:
    """Return a reusable MongoDB client."""

    global _client

    if not MONGODB_URI or MONGODB_URI == (
        "replace_with_your_mongodb_connection_string"
    ):
        raise RuntimeError(
            "MONGODB_URI is missing. Configure it in your local .env file."
        )

    if _client is None:
        _client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            appname="CustomerPurchasePrediction",
        )

    return _client


def get_database() -> Database:
    """Return the project's MongoDB database."""

    if not MONGODB_DATABASE:
        raise RuntimeError("MONGODB_DATABASE cannot be empty.")

    return get_client()[MONGODB_DATABASE]


def check_connection() -> bool:
    """Check whether MongoDB Atlas is reachable."""

    get_client().admin.command("ping")
    return True


def close_connection() -> None:
    """Close the MongoDB client when the application shuts down."""

    global _client

    if _client is not None:
        _client.close()
        _client = None


if __name__ == "__main__":
    try:
        check_connection()
        print("MongoDB connection successful.")
        print(f"Database selected: {MONGODB_DATABASE}")

    except (RuntimeError, PyMongoError) as exc:
        print(
            f"MongoDB connection failed "
            f"({type(exc).__name__}). Check your .env and Atlas settings."
        )
        raise SystemExit(1) from exc

    finally:
        close_connection()
