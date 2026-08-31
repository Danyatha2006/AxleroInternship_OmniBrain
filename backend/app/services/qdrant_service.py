from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


# ============================================================
# PROJECT PATHS
# ============================================================

# Project root:
# OmniBrain/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Local Qdrant database storage:
QDRANT_PATH = PROJECT_ROOT / "qdrant_storage"


# ============================================================
# QDRANT COLLECTION CONFIGURATION
# ============================================================

# Collection for text/document embeddings.
TEXT_COLLECTION_NAME = "omnibrain_text"

# all-MiniLM-L6-v2 produces 384-dimensional embeddings.
DEFAULT_VECTOR_SIZE = 384


# ============================================================
# QDRANT CLIENT
# ============================================================

def get_qdrant_client() -> QdrantClient:
    """
    Create and return a local Qdrant client.

    Qdrant stores its local database inside:
        OmniBrain/qdrant_storage/
    """

    # Make sure the storage directory exists.
    QDRANT_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    return QdrantClient(
        path=str(QDRANT_PATH),
    )


# ============================================================
# COLLECTION MANAGEMENT
# ============================================================

def create_text_collection(
    vector_size: int = DEFAULT_VECTOR_SIZE,
) -> None:
    """
    Create the OmniBrain text collection if it does not already exist.

    Parameters
    ----------
    vector_size:
        Dimension of the embedding vectors.
        all-MiniLM-L6-v2 uses 384 dimensions.
    """

    client = get_qdrant_client()

    # Get existing collections.
    existing_collections = client.get_collections()

    collection_names = {
        collection.name
        for collection in existing_collections.collections
    }

    # Do not recreate the collection if it already exists.
    if TEXT_COLLECTION_NAME in collection_names:
        return

    # Create the collection.
    client.create_collection(
        collection_name=TEXT_COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )


def collection_exists() -> bool:
    """
    Check whether the OmniBrain text collection exists.

    Returns
    -------
    bool
        True if the collection exists, otherwise False.
    """

    client = get_qdrant_client()

    existing_collections = client.get_collections()

    collection_names = {
        collection.name
        for collection in existing_collections.collections
    }

    return TEXT_COLLECTION_NAME in collection_names


# ============================================================
# COLLECTION INFORMATION
# ============================================================

def get_collection_info():
    """
    Return information about the OmniBrain text collection.

    The collection must already exist.
    """

    if not collection_exists():
        return None

    client = get_qdrant_client()

    return client.get_collection(
        collection_name=TEXT_COLLECTION_NAME,
    )