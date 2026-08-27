"""
Text Chunking Module
--------------------
Member 2 - Week 1

Takes extracted PDF text with page/document metadata,
cleans the text, splits it into overlapping chunks,
and returns structured chunks ready for embedding.
"""

import re
from typing import Any


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text by removing unnecessary
    whitespace and common formatting noise.
    """

    if not text:
        return ""

    # Replace multiple spaces/tabs with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove spaces at the beginning/end of lines
    text = "\n".join(line.strip() for line in text.splitlines())

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[str]:
    """
    Split text into chunks based on words.

    Parameters
    ----------
    text : str
        Cleaned text.

    chunk_size : int
        Approximate number of words in each chunk.

    overlap : int
        Number of words shared between consecutive chunks.

    Returns
    -------
    list[str]
        List of text chunks.
    """

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()

    chunks = []

    step = chunk_size - overlap

    for start in range(0, len(words), step):
        end = start + chunk_size

        chunk = " ".join(words[start:end])

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

    return chunks


def create_chunks(
    extracted_pages: list[dict[str, Any]],
    chunk_size: int = 500,
    overlap: int = 50
) -> list[dict[str, Any]]:
    """
    Convert extracted PDF pages into structured text chunks.

    Expected input format:

    [
        {
            "document": "sample.pdf",
            "page": 1,
            "text": "Extracted text..."
        }
    ]

    Returns:

    [
        {
            "chunk_id": "sample_page_1_chunk_1",
            "text": "...",
            "metadata": {
                "document": "sample.pdf",
                "page": 1
            }
        }
    ]
    """

    all_chunks = []

    for page_data in extracted_pages:

        document = page_data.get("document", "unknown")
        page = page_data.get("page", 0)
        text = page_data.get("text", "")

        cleaned = clean_text(text)

        if not cleaned:
            continue

        chunks = chunk_text(
            cleaned,
            chunk_size=chunk_size,
            overlap=overlap
        )

        for index, chunk in enumerate(chunks, start=1):

            chunk_id = (
                f"{document}_page_{page}_chunk_{index}"
            )

            all_chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": chunk,
                    "metadata": {
                        "document": document,
                        "page": page,
                    },
                }
            )

    return all_chunks


if __name__ == "__main__":

    # Temporary test data.
    # Later this will be replaced by Member 1's PDF processor output.

    sample_data = [
        {
            "document": "sample.pdf",
            "page": 1,
            "text": """
            Artificial Intelligence is a field of computer science.
            It focuses on creating systems that can perform tasks
            that normally require human intelligence.
            Machine learning is an important part of artificial intelligence.
            """
        },
        {
            "document": "sample.pdf",
            "page": 2,
            "text": """
            Machine learning allows computers to learn from data.
            Deep learning uses neural networks with multiple layers.
            These techniques are widely used in computer vision,
            natural language processing and recommendation systems.
            """
        }
    ]

    chunks = create_chunks(
        sample_data,
        chunk_size=50,
        overlap=10
    )

    print(f"Total chunks created: {len(chunks)}")

    for chunk in chunks:
        print("\n-----------------------------")
        print("Chunk ID:", chunk["chunk_id"])
        print("Page:", chunk["metadata"]["page"])
        print("Text:", chunk["text"])