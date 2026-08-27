from typing import Dict, List


_chat_history: Dict[str, List[dict]] = {}


def add_message(
    document_id: str,
    question: str,
    answer: str,
) -> None:
    if document_id not in _chat_history:
        _chat_history[document_id] = []

    _chat_history[document_id].append(
        {
            "question": question,
            "answer": answer,
        }
    )


def get_history(document_id: str) -> List[dict]:
    return _chat_history.get(document_id, [])