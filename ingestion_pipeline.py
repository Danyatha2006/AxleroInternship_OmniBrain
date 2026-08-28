import os
import hashlib
import pymupdf
from sentence_transformers import SentenceTransformer
import clip
import torch
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    Distance,
    VectorParams
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PDF_PATH = "data/sample.pdf"

IMAGE_FOLDER = "data/extracted_images"

QDRANT_PATH = "multimodal_qdrant_data"

COLLECTION_NAME = "omnibrain_multimodal"


# --------------------------------------------------
# Load embedding models
# --------------------------------------------------

print("Loading embedding models...")

text_model = SentenceTransformer("all-MiniLM-L6-v2")

device = "cuda" if torch.cuda.is_available() else "cpu"

image_model, preprocess = clip.load(
    "ViT-B/32",
    device=device
)

print("Embedding models loaded successfully!")


# --------------------------------------------------
# PDF text extraction
# --------------------------------------------------

def extract_text_from_pdf(pdf_path):
    """Extract text from every page of the PDF."""

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text").strip()

        if text:
            pages.append({
                "page": page_number,
                "text": text
            })

    document.close()

    return pages


# --------------------------------------------------
# Text chunking
# --------------------------------------------------

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping word-based chunks."""

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


# --------------------------------------------------
# Extract unique images from PDF
# --------------------------------------------------

def extract_images_from_pdf(pdf_path, output_folder):
    """Extract unique embedded images from every PDF page."""

    os.makedirs(output_folder, exist_ok=True)

    document = pymupdf.open(pdf_path)

    images = []

    seen_hashes = set()

    for page_number, page in enumerate(document, start=1):

        page_images = page.get_images(full=True)

        for image_index, image_info in enumerate(page_images, start=1):

            xref = image_info[0]

            image_data = document.extract_image(xref)

            image_bytes = image_data["image"]
            image_ext = image_data["ext"]

            # Create a hash to detect duplicate images
            image_hash = hashlib.md5(image_bytes).hexdigest()

            if image_hash in seen_hashes:

                print(
                    f"  Skipping duplicate image on page {page_number}"
                )

                continue

            seen_hashes.add(image_hash)

            image_filename = (
                f"page_{page_number}_image_{image_index}.{image_ext}"
            )

            image_path = os.path.join(
                output_folder,
                image_filename
            )

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            images.append({
                "page": page_number,
                "image_id": image_index,
                "path": image_path,
                "format": image_ext,
                "hash": image_hash
            })

            print(
                f"  Extracted: {image_filename}"
            )

    document.close()

    return images


# --------------------------------------------------
# Connect to Qdrant
# --------------------------------------------------

client = QdrantClient(path=QDRANT_PATH)


# --------------------------------------------------
# Create multimodal collection if needed
# --------------------------------------------------

def setup_qdrant():
    """Create a fresh multimodal Qdrant collection."""

    existing_collections = [
        collection.name
        for collection in client.get_collections().collections
    ]

    if COLLECTION_NAME in existing_collections:

        print("Removing old Qdrant collection...")

        client.delete_collection(
            collection_name=COLLECTION_NAME
        )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "text": VectorParams(
                size=384,
                distance=Distance.COSINE
            ),
            "image": VectorParams(
                size=512,
                distance=Distance.COSINE
            )
        }
    )

    print("Fresh multimodal Qdrant collection created!")
    
# --------------------------------------------------
# Store text chunks in Qdrant
# --------------------------------------------------

def store_text_chunks(pages):
    """Create text embeddings and store them in Qdrant."""

    points = []

    point_id = 1000

    for page_data in pages:

        page_number = page_data["page"]

        chunks = chunk_text(
            page_data["text"]
        )

        for chunk_index, chunk in enumerate(chunks):

            embedding = text_model.encode(
                chunk
            ).tolist()

            points.append(
                PointStruct(
                    id=point_id,
                    vector={
                        "text": embedding
                    },
                    payload={
                        "content_type": "text",
                        "text": chunk,
                        "page": page_number,
                        "chunk_id": chunk_index,
                        "document": os.path.basename(PDF_PATH)
                    }
                )
            )

            point_id += 1

    if points:

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

    print(
        f"Stored {len(points)} text chunks in Qdrant."
    )

    return points


# --------------------------------------------------
# Store image embeddings in Qdrant
# --------------------------------------------------

def store_image_embeddings(images):
    """Create CLIP embeddings and store images in Qdrant."""

    from PIL import Image

    points = []

    point_id = 2000

    for image_data in images:

        image_path = image_data["path"]

        try:

            pil_image = Image.open(
                image_path
            ).convert("RGB")

            image_input = preprocess(
                pil_image
            ).unsqueeze(0).to(device)

            with torch.no_grad():

                image_embedding = (
                    image_model.encode_image(
                        image_input
                    )
                )

            image_vector = (
                image_embedding[0]
                .cpu()
                .numpy()
                .tolist()
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector={
                        "image": image_vector
                    },
                    payload={
                        "content_type": "image",
                        "image_id": image_data["image_id"],
                        "page": image_data["page"],
                        "document": os.path.basename(PDF_PATH),
                        "image_path": image_path,
                        "image_hash": image_data["hash"]
                    }
                )
            )

            point_id += 1

        except Exception as error:

            print(
                f"Could not process "
                f"{image_path}: {error}"
            )

    if points:

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

    print(
        f"Stored {len(points)} image embeddings in Qdrant."
    )

    return points


# --------------------------------------------------
# Run complete Week 1 pipeline
# --------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("OMNIBRAIN WEEK 1 INGESTION PIPELINE")
    print("=" * 60)


    # Step 1: Extract text

    print(
        "\n[1/5] Extracting PDF text..."
    )

    pages = extract_text_from_pdf(
        PDF_PATH
    )

    print(
        f"Extracted text from "
        f"{len(pages)} pages."
    )


    # Step 2: Extract images

    print(
        "\n[2/5] Extracting PDF images..."
    )

    images = extract_images_from_pdf(
        PDF_PATH,
        IMAGE_FOLDER
    )

    print(
        f"Extracted {len(images)} unique images."
    )


    # Step 3: Setup Qdrant

    print(
        "\n[3/5] Setting up Qdrant..."
    )

    setup_qdrant()


    # Step 4: Text embeddings

    print(
        "\n[4/5] Creating text embeddings..."
    )

    text_points = store_text_chunks(
        pages
    )


    # Step 5: Image embeddings

    print(
        "\n[5/5] Creating image embeddings..."
    )

    image_points = store_image_embeddings(
        images
    )


    # Final summary

    print("\n" + "=" * 60)
    print("WEEK 1 INGESTION COMPLETE!")
    print("=" * 60)

    print(
        f"PDF pages processed : {len(pages)}"
    )

    print(
        f"Images extracted    : {len(images)}"
    )

    print(
        f"Text vectors stored : {len(text_points)}"
    )

    print(
        f"Image vectors stored: {len(image_points)}"
    )

    print(
        "\nMultimodal data is now stored in Qdrant."
    )