_document_text_store: dict[str, str] = {}

_document_chunks_store: dict[str, list[str]] = {}

_document_embeddings_store: dict[str, list[list[float]]] = {}


def set_document_text(document_id: str, text: str) -> None:
    _document_text_store[document_id] = text


def get_document_text(document_id: str) -> str | None:
    return _document_text_store.get(document_id)


def set_document_chunks(document_id: str, chunks: list[str]) -> None:
    _document_chunks_store[document_id] = chunks


def get_document_chunks(document_id: str) -> list[str] | None:
    return _document_chunks_store.get(document_id)


def set_document_embeddings(
    document_id: str,
    embeddings: list[list[float]],
) -> None:
    _document_embeddings_store[document_id] = embeddings


def get_document_embeddings(
    document_id: str,
) -> list[list[float]] | None:
    return _document_embeddings_store.get(document_id)