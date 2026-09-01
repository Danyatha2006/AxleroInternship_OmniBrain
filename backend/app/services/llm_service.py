from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "google/flan-t5-base"

MAX_INPUT_TOKENS = 512
MAX_OUTPUT_TOKENS = 80

_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_answer(context: str, question: str) -> str:
    context = context.strip()
    question = question.strip()

    if not context:
        return "I could not find this information in the document."

    if not question:
        return "Please provide a question."

    prompt = (
        "You are a document question-answering assistant.\n\n"
        "Answer the question using ONLY the information in the "
        "document context.\n"
        "Do not use outside knowledge.\n"
        "Give a complete and direct answer.\n"
        "Do not answer with only a keyword or phrase.\n"
        "Use 1 to 3 sentences when appropriate.\n"
        "If the answer is not present in the context, say exactly:\n"
        "I could not find this information in the document.\n\n"
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
        do_sample=False,
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
