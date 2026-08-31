from uuid import uuid4

from qdrant_client.models import PointStruct

from app.services.embedding_service import generate_embeddings
from app.services.qdrant_service import (
    TEXT_COLLECTION_NAME,
    get_qdrant_client,
)


MAX_TOP_K = 10
MINIMUM_SCORE = 0.20


def store_text_embeddings(
    document_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
    document_name: str | None = None,
) -> None:
    """
    Store document chunks and embeddings in Qdrant.
    """

    if not chunks or not embeddings:
        return

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks must match number of embeddings."
        )

    client = get_qdrant_client()

    points = []

    for chunk_index, (text, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        point = PointStruct(
            id=str(uuid4()),
            vector=embedding,
            payload={
                "text": str(text),
                "document_id": document_id,
                "document_name": document_name,
                "chunk_index": chunk_index,
                "content_type": "text",
                "page_number": None,
                "image_reference": None,
            },
        )

        points.append(point)

    client.upsert(
        collection_name=TEXT_COLLECTION_NAME,
        points=points,
    )


def search_qdrant(
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Search the Qdrant text collection using a natural-language query.
    """

    query = query.strip()

    if not query:
        return []

    top_k = max(1, min(top_k, MAX_TOP_K))

    query_embedding = generate_embeddings([query])[0]

    client = get_qdrant_client()

    results = client.query_points(
        collection_name=TEXT_COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
        with_payload=True,
    )

    search_results = []

    for point in results.points:
        score = float(point.score)

        if score < MINIMUM_SCORE:
            continue

        payload = point.payload or {}

        search_results.append(
            {
                "score": score,
                "text": payload.get("text", ""),
                "document_id": payload.get("document_id"),
                "chunk_index": payload.get("chunk_index"),
                "content_type": payload.get(
                    "content_type",
                    "text",
                ),
                "document_name": payload.get("document_name"),
                "page_number": payload.get("page_number"),
                "image_reference": payload.get(
                    "image_reference"
                ),
            }
        )

    return search_results