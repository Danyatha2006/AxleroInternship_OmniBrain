from typing import Any

from app.services.qdrant_search import search_qdrant
from app.services.langfuse_service import langfuse


class SearchAgent:
    """
    Search Agent responsible for semantic document retrieval.
    """

    def run(
        self,
        query: str,
        top_k: int = 5,
        document_id: str | None = None,
    ) -> dict[str, Any]:

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

        with langfuse.start_as_current_observation(
            as_type="retriever",
            name="qdrant-document-retrieval",
            input={
                "query": query,
                "top_k": top_k,
                "document_id": document_id,
            },
        ) as retrieval:

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
                        "document_id": result.get(
                            "document_id"
                        ),
                        "document_name": result.get(
                            "document_name"
                        ),
                        "page_number": result.get(
                            "page_number"
                        ),
                        "chunk_index": result.get(
                            "chunk_index"
                        ),
                        "content_type": result.get(
                            "content_type",
                            "text",
                        ),
                        "image_reference": result.get(
                            "image_reference"
                        ),
                    }
                )

            retrieval.update(
                output={
                    "result_count": len(
                        structured_results
                    ),
                    "results": structured_results,
                },
                metadata={
                    "retrieval_type": "qdrant",
                    "top_k": top_k,
                },
            )

        return {
            "query": query,
            "results": structured_results,
        }