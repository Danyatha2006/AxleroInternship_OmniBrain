from typing import Any

from app.services.qdrant_search import search_qdrant


class SearchAgent:
    """
    Search Agent responsible for semantic document retrieval.

    The agent delegates the actual vector search to qdrant_search.py
    and exposes a clean interface for higher-level orchestration.
    """

    def run(
        self,
        query: str,
        top_k: int = 5,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute semantic search.

        Args:
            query: User's search query.
            top_k: Maximum number of results to return.
            document_id: Optional document filter.

        Returns:
            Structured search response containing the query and results.
        """

        if not isinstance(query, str):
            return {
                "query": "",
                "results": [],
            }

        query = query.strip()

        if not query:
            return {
                "query": "",
                "results": [],
            }

        if top_k < 1:
            top_k = 1

        if top_k > 10:
            top_k = 10

        if document_id is not None:
            document_id = document_id.strip()

            if not document_id:
                document_id = None

        results = search_qdrant(
            query=query,
            top_k=top_k,
            document_id=document_id,
        )

        structured_results: list[dict[str, Any]] = []

        for result in results:
            structured_results.append(
                {
                    "score": result.get("score"),
                    "text": result.get("text", ""),
                    "document_id": result.get("document_id"),
                    "document_name": result.get("document_name"),
                    "page_number": result.get("page_number"),
                    "chunk_index": result.get("chunk_index"),
                    "content_type": result.get(
                        "content_type",
                        "text",
                    ),
                    "image_reference": result.get(
                        "image_reference"
                    ),
                }
            )

        return {
            "query": query,
            "results": structured_results,
        }