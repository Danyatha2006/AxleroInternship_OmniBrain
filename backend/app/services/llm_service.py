from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


MODEL_NAME = "google/flan-t5-base"

MAX_INPUT_TOKENS = 512
MAX_OUTPUT_TOKENS = 200


_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_answer(
    context: str,
    question: str,
) -> str:
    """
    Generate a grounded answer using only the retrieved document context.
    """

    context = context.strip()
    question = question.strip()

    if not context:
        return "I could not find relevant information in the document."

    if not question:
        return "Please provide a question."

    prompt = (
        "You are OmniBrain, a document question-answering assistant.\n\n"
        "Use ONLY the provided document context to answer the question.\n"
        "Do not use outside knowledge.\n"
        "Do not invent facts.\n"
        "If the answer cannot be found in the context, respond exactly with:\n"
        "I could not find this information in the document.\n"
        "Give a direct and concise answer.\n\n"
        f"Document Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )

    inputs = _tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_INPUT_TOKENS,
    )

    outputs = _model.generate(
        **inputs,
        max_new_tokens=MAX_OUTPUT_TOKENS,
        num_beams=4,
        no_repeat_ngram_size=3,
        early_stopping=True,
    )

    answer = _tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    ).strip()

    if not answer:
        return "I could not find this information in the document."

    return answer