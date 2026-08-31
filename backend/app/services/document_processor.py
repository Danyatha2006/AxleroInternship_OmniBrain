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


def process_document(document_id: str, file_path: str) -> str:
    """
    Extract PDF text, create chunks, generate embeddings,
    store the embeddings in both FAISS and Qdrant,
    store document data, and update processing status.
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

        reader = PdfReader(pdf_path)

        extracted_pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                extracted_pages.append(text.strip())

        extracted_text = "\n\n".join(extracted_pages)

        set_document_text(
            document_id,
            extracted_text,
        )

        chunks = chunk_text(extracted_text)

        set_document_chunks(
            document_id,
            chunks,
        )

        embeddings = generate_embeddings(chunks)

        set_document_embeddings(
            document_id,
            embeddings,
        )

        create_vector_index(
            document_id,
            embeddings,
        )

        store_text_embeddings(
            document_id=document_id,
            chunks=chunks,
            embeddings=embeddings,
        )

        print(
            f"Document {document_id}: "
            f"extracted {len(extracted_text)} characters, "
            f"created {len(chunks)} chunks, "
            f"generated {len(embeddings)} embeddings, "
            f"created FAISS index, "
            f"stored embeddings in Qdrant"
        )

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