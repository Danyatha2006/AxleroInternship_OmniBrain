from enum import Enum


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


_document_status_store: dict[str, DocumentStatus] = {}


def set_document_status(
    document_id: str,
    status: DocumentStatus,
) -> None:
    _document_status_store[document_id] = status


def get_document_status(
    document_id: str,
) -> DocumentStatus | None:
    return _document_status_store.get(document_id)