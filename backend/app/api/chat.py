from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.chat_history import add_message, get_history
from app.services.document_status import (
    DocumentStatus,
    get_document_status,
)
from app.services.langfuse_service import (
    flush_langfuse,
    langfuse,
)
from app.graph.supervisor import search_graph


router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    document_id: str = Field(
        ...,
        min_length=1,
        description="ID of the processed document.",
    )

    question: str = Field(
        ...,
        min_length=1,
        description="Question about the document.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of document chunks to retrieve.",
    )


@router.post("")
async def chat(request: ChatRequest):

    document_id = request.document_id.strip()
    question = request.question.strip()

    if not document_id:
        raise HTTPException(
            status_code=400,
            detail="document_id cannot be empty.",
        )

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    status = get_document_status(document_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=(
                "Document processing is not completed. "
                f"Current status: {status.value}"
            ),
        )

    try:
        conversation_history = get_history(document_id)

        with langfuse.start_as_current_observation(
            as_type="chain",
            name="omnibrain-chat",
            input={
                "document_id": document_id,
                "question": question,
                "top_k": request.top_k,
            },
            metadata={
                "component": "FastAPI",
                "workflow": "Self-RAG",
            },
        ) as trace:

            graph_result = search_graph.invoke(
                {
                    "query": question,
                    "document_id": document_id,
                    "top_k": request.top_k,
                }
            )

            source_results = graph_result.get(
                "search_results",
                [],
            )

            answer = graph_result.get(
                "final_answer",
                (
                    "I could not find this information "
                    "in the document."
                ),
            )

            # Self-RAG execution information
            retrieval_attempt = graph_result.get(
                "retrieval_attempt",
                0,
            )

            retrieval_relevant = graph_result.get(
                "retrieval_relevant",
                False,
            )

            rewritten_query = graph_result.get(
                "rewritten_query",
                "",
            )

            add_message(
                document_id=document_id,
                question=question,
                answer=answer,
            )

            sources = [
                {
                    "chunk_index": result.get(
                        "chunk_index"
                    ),
                    "score": result.get(
                        "score"
                    ),
                    "text": result.get(
                        "text",
                        "",
                    ),
                    "document_name": result.get(
                        "document_name"
                    ),
                    "page_number": result.get(
                        "page_number"
                    ),
                    "content_type": result.get(
                        "content_type",
                        "text",
                    ),
                    "image_reference": result.get(
                        "image_reference"
                    ),
                }
                for result in source_results
            ]

            response = {
                "document_id": document_id,
                "question": question,
                "answer": answer,

                # Self-RAG evaluation information
                "retrieval_attempt": retrieval_attempt,
                "retrieval_relevant": retrieval_relevant,
                "rewritten_query": rewritten_query,

                "sources": sources,
                "history": get_history(
                    document_id
                ),
            }

            trace.update(
                output={
                    "answer": answer,
                    "source_count": len(sources),
                    "retrieval_attempt": retrieval_attempt,
                    "retrieval_relevant": retrieval_relevant,
                    "rewritten_query": rewritten_query,
                },
            )

        flush_langfuse()

        return response

    except Exception as exc:

        print(
            f"Chat processing error for document "
            f"{document_id}: {exc}"
        )

        flush_langfuse()

        raise HTTPException(
            status_code=500,
            detail="Unable to process the question.",
        ) from exc


@router.get("/{document_id}/history")
async def chat_history(
    document_id: str,
):

    document_id = document_id.strip()

    if not document_id:
        raise HTTPException(
            status_code=400,
            detail="document_id cannot be empty.",
        )

    status = get_document_status(
        document_id
    )

    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "document_id": document_id,
        "history": get_history(
            document_id
        ),
    }