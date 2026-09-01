import re

from app.services.qdrant_search import search_qdrant
from app.services.llm_service import generate_answer


def clean_text(text: str) -> str:
    """
    Clean PDF-extracted text before sending it to the LLM.
    """

    if not text:
        return ""

    # Replace newlines and repeated whitespace with single spaces.
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def retrieve_context(
    document_id: str,
    query: str,
    top_k: int = 5,
) -> tuple[str, list[dict]]:
    """
    Retrieve relevant document chunks from Qdrant.

    The highest-scoring result is used as the primary
    context for answer generation.
    """

    results = search_qdrant(
        query=query,
        top_k=top_k,
        document_id=document_id,
    )

    if not results:
        return "", []

    # Qdrant results are already returned in relevance order.
    best_result = results[0]

    text = best_result.get("text", "")

    if not text:
        return "", []

    context = clean_text(text)

    if not context:
        return "", []

    return context, results


def answer_question(
    document_id: str,
    question: str,
    top_k: int = 5,
    conversation_history: list[dict] | None = None,
) -> tuple[str, list[dict]]:
    """
    Generate an answer using Qdrant-retrieved document context
    and the local LLM.
    """

    question = question.strip()

    if not question:
        return "Please provide a question.", []

    conversation_history = conversation_history or []

    # Retrieve the most relevant document context.
    context, sources = retrieve_context(
        document_id=document_id,
        query=question,
        top_k=top_k,
    )

    if not context:
        return (
            "I could not find this information in the document.",
            [],
        )

    # Add recent conversation history only when available.
    history_context = ""

    if conversation_history:
        history_parts = []

        for message in conversation_history[-5:]:
            previous_question = message.get(
                "question",
                "",
            ).strip()

            previous_answer = message.get(
                "answer",
                "",
            ).strip()

            if previous_question and previous_answer:
                history_parts.append(
                    f"User: {previous_question}\n"
                    f"Assistant: {previous_answer}"
                )

        if history_parts:
            history_context = (
                "\n\nPrevious conversation:\n"
                + "\n\n".join(history_parts)
            )

    # Use the best retrieved chunk as the main document context.
    combined_context = context

    if history_context:
        combined_context += history_context

    answer = generate_answer(
        context=combined_context,
        question=question,
    )

    return answer, sources