from app.services.document_text import get_document_chunks
from app.services.embedding_service import generate_embeddings
from app.services.vector_store import search_vectors


MAX_TOP_K = 10
MINIMUM_SCORE = 0.20


def search_document(
    document_id: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieve the most relevant document chunks for a query.

    Results are cleaned, validated, ranked by relevance,
    and weak matches are filtered out.
    """

    query = query.strip()

    if not query:
        return []

    top_k = max(1, min(top_k, MAX_TOP_K))

    chunks = get_document_chunks(document_id)

    if not chunks:
        return []

    query_embedding = generate_embeddings([query])[0]

    vector_results = search_vectors(
        document_id=document_id,
        query_embedding=query_embedding,
        top_k=top_k,
    )

    if not vector_results:
        return []

    results = []
    seen_indexes = set()

    for index, score in vector_results:
        if not isinstance(index, int):
            continue

        if index < 0 or index >= len(chunks):
            continue

        if index in seen_indexes:
            continue

        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            continue

        text = str(chunks[index]).strip()

        if not text:
            continue

        if numeric_score < MINIMUM_SCORE:
            continue

        results.append(
            {
                "chunk_index": index,
                "score": numeric_score,
                "text": text,
            }
        )

        seen_indexes.add(index)

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]