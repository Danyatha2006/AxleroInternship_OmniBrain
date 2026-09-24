import numpy as np
import faiss


_vector_indexes: dict[str, faiss.IndexFlatIP] = {}


def create_vector_index(
    document_id: str,
    embeddings: list[list[float]],
) -> None:
    if not embeddings:
        return

    embedding_array = np.asarray(
        embeddings,
        dtype="float32",
    )

    if embedding_array.ndim != 2 or embedding_array.shape[0] == 0:
        return

    # Normalize document embeddings so inner product behaves
    # as cosine similarity.
    faiss.normalize_L2(embedding_array)

    dimension = embedding_array.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embedding_array)

    _vector_indexes[document_id] = index


def search_vectors(
    document_id: str,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[tuple[int, float]]:
    index = _vector_indexes.get(document_id)

    if index is None or index.ntotal == 0:
        return []

    if top_k < 1:
        return []

    query_array = np.asarray(
        [query_embedding],
        dtype="float32",
    )

    if query_array.ndim != 2 or query_array.shape[1] != index.d:
        return []

    # Normalize query embedding using the same method
    # used for document embeddings.
    faiss.normalize_L2(query_array)

    limit = min(top_k, index.ntotal)

    scores, indexes = index.search(
        query_array,
        limit,
    )

    results = []

    for index_value, score in zip(indexes[0], scores[0]):
        if index_value == -1:
            continue

        results.append(
            (
                int(index_value),
                float(score),
            )
        )

    return results