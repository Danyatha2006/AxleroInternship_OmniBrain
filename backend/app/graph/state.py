from typing import Any, TypedDict


class OmniBrainState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    query: str
    document_id: str | None
    top_k: int

    search_results: list[dict[str, Any]]

    context: str

    final_answer: str