from typing import Any, TypedDict


class OmniBrainState(TypedDict, total=False):
    query: str
    document_id: str | None
    top_k: int

    search_results: list[dict[str, Any]]
    vision_results: list[dict[str, Any]]

    context: str
    final_answer: str