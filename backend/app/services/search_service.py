from app.services.qdrant_search import search_qdrant


MAX_TOP_K = 10


def search_document(
    document_id: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Search document content using Qdrant.
    """

    query = query.strip()

    if not query:
        return []

    top_k = max(1, min(top_k, MAX_TOP_K))

    return search_qdrant(
        query=query,
        top_k=top_k,
        document_id=document_id,
    )