import os

from dotenv import load_dotenv
from langfuse import get_client


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
    )
)

ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


langfuse = get_client()


def flush_langfuse() -> None:
    """
    Send pending Langfuse events immediately.
    """
    try:
        langfuse.flush()
    except Exception as exc:
        print(f"Langfuse flush error: {exc}")