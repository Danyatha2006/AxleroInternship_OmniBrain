from app.services.search_service import search_document
from app.services.llm_service import generate_answer


def retrieve_context(
    document_id: str,
    query: str,
    top_k: int = 5,
) -> tuple[str, list[dict]]:
    results = search_document(
        document_id=document_id,
        query=query,
        top_k=top_k,
    )

    if not results:
        return "", []

    context_parts = []

    for result in results:
        text = result.get("text", "").strip()

        if text:
            context_parts.append(text)

    if not context_parts:
        return "", []

    return "\n\n".join(context_parts), results


def answer_question(
    document_id: str,
    question: str,
    top_k: int = 5,
    conversation_history: list[dict] | None = None,
) -> tuple[str, list[dict]]:
    question = question.strip()

    if not question:
        return "Please provide a question.", []

    conversation_history = conversation_history or []

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

    history_context = ""

    if conversation_history:
        history_parts = []

        for message in conversation_history[-5:]:
            previous_question = message.get("question", "").strip()
            previous_answer = message.get("answer", "").strip()

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

    combined_context = context

    if history_context:
        combined_context += history_context

    answer = generate_answer(
        context=combined_context,
        question=question,
    )

    return answer, sources