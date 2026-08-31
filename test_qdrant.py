import sys
from pathlib import Path


# Allow Python to import the backend app package.
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_PATH = PROJECT_ROOT / "backend"

sys.path.insert(
    0,
    str(BACKEND_PATH),
)


from app.services.qdrant_service import (
    TEXT_COLLECTION_NAME,
    collection_exists,
    create_text_collection,
    get_qdrant_client,
)


def main() -> None:
    print("Starting Qdrant test...")

    print("Creating Qdrant collection...")
    create_text_collection()

    print("Checking collection...")
    exists = collection_exists()

    print(f"Collection exists: {exists}")

    client = get_qdrant_client()

    collections = client.get_collections()

    print("\nAvailable collections:")

    for collection in collections.collections:
        print(f"- {collection.name}")

    print(f"\nExpected collection: {TEXT_COLLECTION_NAME}")

    if exists:
        print("\nQdrant Phase 1 setup successful!")
    else:
        print("\nQdrant collection was not created.")


if __name__ == "__main__":
    main()