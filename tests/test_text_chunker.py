from ingestion.text_chunker import (
    clean_text,
    chunk_text,
    create_chunks,
)


def test_clean_text():
    text = "  Hello    world   \n\n   This is a test.  "

    result = clean_text(text)

    assert result == "Hello world\n\nThis is a test."


def test_chunk_text():
    text = "one two three four five six seven eight nine ten"

    chunks = chunk_text(
        text,
        chunk_size=5,
        overlap=2
    )

    assert len(chunks) == 3
    assert chunks[0] == "one two three four five"
    assert chunks[1] == "four five six seven eight"
    assert chunks[2] == "seven eight nine ten"


def test_create_chunks():
    pages = [
        {
            "document": "sample.pdf",
            "page": 1,
            "text": "This is some sample text for testing."
        }
    ]

    chunks = create_chunks(
        pages,
        chunk_size=10,
        overlap=2
    )

    assert len(chunks) == 1

    assert chunks[0]["metadata"]["document"] == "sample.pdf"
    assert chunks[0]["metadata"]["page"] == 1
    assert chunks[0]["chunk_id"] == "sample.pdf_page_1_chunk_1"


def test_empty_text():
    assert clean_text("") == ""
    assert chunk_text("") == []
    assert create_chunks([]) == []


def test_invalid_chunk_parameters():
    text = "This is some text."

    try:
        chunk_text(text, chunk_size=10, overlap=10)
        assert False
    except ValueError:
        assert True