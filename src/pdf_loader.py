import os
import pymupdf


def load_pdf(pdf_path):
    # Check if the PDF exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Check file extension
    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError("The input file must be a PDF.")

    # Open the PDF
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        raise RuntimeError(f"Could not open PDF: {e}")

    pages = []
    low_text_pages = []

    # Extract text page by page
    for page_number, page in enumerate(doc):
        text = page.get_text().strip()

        # Check for pages with very little text
        if len(text) < 50:
            low_text_pages.append(page_number + 1)

        # Store page information
        pages.append({
            "page_number": page_number + 1,
            "text": text,
            "character_count": len(text),
            "is_low_text": len(text) < 50
        })

    # Close the PDF
    doc.close()

    print("Pages with less than 50 characters:", low_text_pages)

    return pages