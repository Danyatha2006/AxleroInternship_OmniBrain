from pathlib import Path
from typing import Any

import fitz


BASE_DIR = Path(__file__).resolve().parents[2]

UPLOADS_DIR = BASE_DIR / "uploads"
IMAGES_DIR = BASE_DIR / "extracted_images"


def extract_document_images(
    document_id: str,
) -> list[dict[str, Any]]:
    """
    Render every PDF page as an image.

    This captures:
    - embedded images
    - diagrams
    - vector graphics
    - tables
    - other visual PDF content

    Returns metadata for every rendered page.
    """

    document_id = document_id.strip()

    if not document_id:
        return []

    pdf_path = UPLOADS_DIR / f"{document_id}.pdf"

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"Document not found: {pdf_path}"
        )

    document_images_dir = IMAGES_DIR / document_id

    document_images_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    extracted_images: list[dict[str, Any]] = []

    pdf = fitz.open(str(pdf_path))

    try:
        for page_index in range(len(pdf)):
            page = pdf[page_index]

            image_name = (
                f"page_{page_index + 1}.png"
            )

            image_path = (
                document_images_dir / image_name
            )

            # Render PDF page at 150 DPI.
            matrix = fitz.Matrix(150 / 72, 150 / 72)

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False,
            )

            pixmap.save(str(image_path))

            extracted_images.append(
                {
                    "document_id": document_id,
                    "page_number": page_index + 1,
                    "image_index": 1,
                    "image_path": str(image_path),
                    "image_reference": (
                        f"/extracted_images/"
                        f"{document_id}/"
                        f"{image_name}"
                    ),
                    "width": pixmap.width,
                    "height": pixmap.height,
                    "extension": "png",
                }
            )

    finally:
        pdf.close()

    return extracted_images