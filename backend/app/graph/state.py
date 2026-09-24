from typing import Any, TypedDict


class OmniBrainState(TypedDict, total=False):
    # Original user query
    query: str

    # Query used for the latest retrieval
    rewritten_query: str

    document_id: str | None
    top_k: int

    # Retrieval results
    search_results: list[dict[str, Any]]

    # Self-RAG information
    retrieval_attempt: int
    retrieval_relevant: bool

    # Vision
    vision_results: list[dict[str, Any]]

    # Final context and answer
    context: str
    final_answer: str