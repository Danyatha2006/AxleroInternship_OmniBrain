from enum import Enum
import json
from pathlib import Path
from threading import Lock


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Persistent status file.
# It is stored inside backend/data/.
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
STATUS_FILE = DATA_DIR / "document_status.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

_status_lock = Lock()


def _load_status_store() -> dict[str, str]:
    """
    Load document statuses from the persistent JSON file.
    """
    if not STATUS_FILE.exists():
        return {}

    try:
        with STATUS_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {}

        return {
            str(document_id): str(status)
            for document_id, status in data.items()
        }

    except (OSError, json.JSONDecodeError):
        return {}


def _save_status_store(
    store: dict[str, str],
) -> None:
    """
    Save document statuses to the persistent JSON file.
    """
    temporary_file = STATUS_FILE.with_suffix(".tmp")

    with temporary_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            store,
            file,
            indent=2,
        )

    temporary_file.replace(STATUS_FILE)


def set_document_status(
    document_id: str,
    status: DocumentStatus,
) -> None:
    """
    Persist the status of a document.
    """
    with _status_lock:
        store = _load_status_store()

        store[document_id] = status.value

        _save_status_store(store)


def get_document_status(
    document_id: str,
) -> DocumentStatus | None:
    """
    Retrieve the persisted status of a document.
    """
    with _status_lock:
        store = _load_status_store()

        value = store.get(document_id)

        if value is None:
            return None

        try:
            return DocumentStatus(value)

        except ValueError:
            return None