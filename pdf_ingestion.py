import pymupdf


PDF_PATH = "data/sample.pdf"


def extract_text_from_pdf(pdf_path):
    """Extract text from every page of a PDF."""
    
    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()

        pages.append({
            "page": page_number,
            "text": text
        })

    document.close()

    return pages


def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks."""

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


if __name__ == "__main__":
    pages = extract_text_from_pdf(PDF_PATH)

    print("PDF parsed successfully!")
    print("Total pages:", len(pages))

    total_chunks = 0

    for page in pages:

        chunks = chunk_text(page["text"])

        print("\n" + "=" * 60)
        print(f"PAGE {page['page']}")
        print("=" * 60)

        print("Number of chunks:", len(chunks))

        for i, chunk in enumerate(chunks[:2], start=1):
            print(f"\nChunk {i}:")
            print(chunk[:500])

        total_chunks += len(chunks)

    print("\n" + "=" * 60)
    print("TOTAL CHUNKS:", total_chunks)
    print("=" * 60)