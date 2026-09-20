from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.services.langfuse_service import langfuse


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

    input_token_count = 0
    output_token_count = 0

    with langfuse.start_as_current_observation(
        as_type="generation",
        name="flan-t5-answer-generation",
        model=MODEL_NAME,
        input={
            "question": question,
            "context": context,
        },
        model_parameters={
            "max_input_tokens": MAX_INPUT_TOKENS,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "num_beams": 4,
            "do_sample": False,
        },
    ) as generation:

        inputs = _tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_INPUT_TOKENS,
        )

        input_token_count = int(
            inputs["input_ids"].shape[-1]
        )

        outputs = _model.generate(
            **inputs,
            max_new_tokens=MAX_OUTPUT_TOKENS,
            num_beams=4,
            do_sample=False,
            no_repeat_ngram_size=3,
            early_stopping=True,
        )

        output_token_count = int(
            outputs.shape[-1]
        )

        answer = _tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
        ).strip()

        if not answer:
            answer = (
                "I could not find this information "
                "in the document."
            )

        generation.update(
            output=answer,
            usage_details={
                "input_tokens": input_token_count,
                "output_tokens": output_token_count,
                "total_tokens": (
                    input_token_count
                    + output_token_count
                ),
            },
        )

    return answer