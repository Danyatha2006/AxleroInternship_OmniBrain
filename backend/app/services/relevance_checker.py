from typing import Any


DEFAULT_RELEVANCE_THRESHOLD = 0.40


def is_relevant(
    results: list[dict[str, Any]],
    threshold: float = DEFAULT_RELEVANCE_THRESHOLD,
) -> bool:
    """
    Check whether retrieved results are relevant enough.

    A result is considered relevant when:
    - at least one result exists, and
    - the best similarity score meets the threshold.
    """

    if not results:
        return False

    best_score = max(
        float(result.get("score", 0.0))
        for result in results
    )

    return best_score >= threshold
