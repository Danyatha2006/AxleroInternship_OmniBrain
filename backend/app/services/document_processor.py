from pathlib import Path

from pypdf import PdfReader

from app.services.document_status import (
    DocumentStatus,
    set_document_status,
)
from app.services.document_text import (
    set_document_text,
    set_document_chunks,
    set_document_embeddings,
)
from app.services.text_chunker import chunk_text
from app.services.embedding_service import generate_embeddings
from app.services.vector_store import create_vector_index
from app.services.qdrant_search import store_text_embeddings
from app.services.document_images import extract_document_images


def process_document(document_id: str, file_path: str) -> str:
    """
    Process an uploaded PDF.

    Processing pipeline:
    1. Mark document as PROCESSING.
    2. Validate the PDF path.
    3. Extract text from the PDF.
    4. Store extracted text.
    5. Split text into chunks.
    6. Generate embeddings.
    7. Store embeddings in FAISS.
    8. Store embeddings in Qdrant.
    9. Extract/render document pages as images.
    10. Mark document as COMPLETED.

    Returns:
        Extracted document text.
    """

    try:
        set_document_status(
            document_id,
            DocumentStatus.PROCESSING,
        )

        pdf_path = Path(file_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"Document not found: {pdf_path}"
            )

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, got: {pdf_path.suffix}"
            )

        # ---------------------------------------------------------
        # 1. Extract PDF text
        # ---------------------------------------------------------

        reader = PdfReader(pdf_path)

        extracted_pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                cleaned_text = text.strip()

                if cleaned_text:
                    extracted_pages.append(cleaned_text)

        extracted_text = "\n\n".join(extracted_pages)

        # ---------------------------------------------------------
        # 2. Store extracted text
        # ---------------------------------------------------------

        set_document_text(
            document_id,
            extracted_text,
        )

        # ---------------------------------------------------------
        # 3. Create text chunks
        # ---------------------------------------------------------

        chunks = chunk_text(extracted_text)

        set_document_chunks(
            document_id,
            chunks,
        )

        # ---------------------------------------------------------
        # 4. Generate embeddings
        # ---------------------------------------------------------

        embeddings = generate_embeddings(chunks)

        set_document_embeddings(
            document_id,
            embeddings,
        )

        # ---------------------------------------------------------
        # 5. Store embeddings in FAISS
        # ---------------------------------------------------------

        create_vector_index(
            document_id,
            embeddings,
        )

        # ---------------------------------------------------------
        # 6. Store embeddings in Qdrant
        # ---------------------------------------------------------

        store_text_embeddings(
            document_id=document_id,
            chunks=chunks,
            embeddings=embeddings,
        )

        # ---------------------------------------------------------
        # 7. Extract/render document pages as images
        # ---------------------------------------------------------

        extracted_images = extract_document_images(
            document_id
        )

        # ---------------------------------------------------------
        # 8. Log processing information
        # ---------------------------------------------------------

        print(
            f"Document {document_id}: "
            f"extracted {len(extracted_text)} characters, "
            f"created {len(chunks)} chunks, "
            f"generated {len(embeddings)} embeddings, "
            f"created FAISS index, "
            f"stored embeddings in Qdrant, "
            f"extracted {len(extracted_images)} document images"
        )

        # ---------------------------------------------------------
        # 9. Mark document as completed
        # ---------------------------------------------------------

        set_document_status(
            document_id,
            DocumentStatus.COMPLETED,
        )

        return extracted_text

    except Exception as exc:
        set_document_status(
            document_id,
            DocumentStatus.FAILED,
        )

        print(
            f"Document {document_id} processing failed: {exc}"
        )

        raise