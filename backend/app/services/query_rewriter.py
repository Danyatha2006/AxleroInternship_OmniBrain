from app.services.llm_service import _model, _tokenizer, MAX_OUTPUT_TOKENS


def rewrite_query(query: str) -> str:
    """
    Rewrite a query to improve document retrieval.
    """

    query = query.strip()

    if not query:
        return ""

    prompt = (
        "Rewrite the following question to make it clearer "
        "and more suitable for searching a document.\n"
        "Keep the same meaning. Return only the rewritten "
        "question.\n\n"
        f"Question: {query}\n"
        "Rewritten question:"
    )

    inputs = _tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )

    outputs = _model.generate(
        **inputs,
        max_new_tokens=MAX_OUTPUT_TOKENS,
        num_beams=4,
        do_sample=False,
    )

    rewritten = _tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    ).strip()

    return rewritten or query
