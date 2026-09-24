import torch
import clip
from PIL import Image
from qdrant_client import QdrantClient


# --------------------------------------------------
# Configuration
# --------------------------------------------------

QDRANT_PATH = "multimodal_qdrant_data"
COLLECTION_NAME = "omnibrain_multimodal"

IMAGE_PATH = "data/extracted_images/page_1_image_1.jpeg"


# --------------------------------------------------
# Load CLIP
# --------------------------------------------------

print("Loading CLIP model...")

device = "cuda" if torch.cuda.is_available() else "cpu"

image_model, preprocess = clip.load(
    "ViT-B/32",
    device=device
)

print("CLIP loaded successfully!")


# --------------------------------------------------
# Create query image embedding
# --------------------------------------------------

image = Image.open(IMAGE_PATH).convert("RGB")

image_input = preprocess(image).unsqueeze(0).to(device)

with torch.no_grad():
    image_embedding = image_model.encode_image(image_input)

image_vector = (
    image_embedding[0]
    .cpu()
    .numpy()
    .tolist()
)


# --------------------------------------------------
# Connect to Qdrant
# --------------------------------------------------

client = QdrantClient(path=QDRANT_PATH)


# --------------------------------------------------
# Search Qdrant
# --------------------------------------------------

results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=image_vector,
    using="image",
    limit=3
)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n" + "=" * 60)
print("REAL IMAGE RETRIEVAL TEST")
print("=" * 60)

print("Query image:", IMAGE_PATH)

for i, result in enumerate(results.points, start=1):

    print(f"\nResult {i}")
    print("-" * 40)

    print("Score:", result.score)
    print("Document:", result.payload.get("document"))
    print("Page:", result.payload.get("page"))
    print("Image ID:", result.payload.get("image_id"))
    print("Image path:", result.payload.get("image_path"))