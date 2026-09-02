from typing import Any


class VisionAgent:
    """
    Vision Agent responsible for analyzing visual
    document content such as rendered PDF pages.
    """

    def run(
        self,
        image_reference: str,
        query: str,
    ) -> dict[str, Any]:
        """
        Analyze a document image for the given query.

        Args:
            image_reference: Reference/path to the extracted image.
            query: User's question.

        Returns:
            Structured vision result.
        """

        if not image_reference:
            return {
                "image_reference": None,
                "query": query,
                "answer": "",
            }

        return {
            "image_reference": image_reference,
            "query": query,
            "answer": "",
        }