from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import clip
import torch
from PIL import Image


# --------------------------------------------------
# 1. Load models
# --------------------------------------------------

text_model = SentenceTransformer("all-MiniLM-L6-v2")

device = "cuda" if torch.cuda.is_available() else "cpu"
image_model, preprocess = clip.load("ViT-B/32", device=device)

print("Models loaded successfully!")


# --------------------------------------------------
# 2. Connect to our multimodal Qdrant database
# --------------------------------------------------

client = QdrantClient(path="multimodal_qdrant_data")

collection_name = "omnibrain_multimodal"


# --------------------------------------------------
# 3. Create a sample text embedding
# --------------------------------------------------

text = "The company's revenue increased by 15 percent in 2025."

text_vector = text_model.encode(text).tolist()

print("Text embedding created!")
print("Text vector size:", len(text_vector))


# --------------------------------------------------
# 4. Create a sample image
# --------------------------------------------------

image = Image.new("RGB", (224, 224), "white")

image_input = preprocess(image).unsqueeze(0).to(device)

with torch.no_grad():
    image_embedding = image_model.encode_image(image_input)

image_vector = image_embedding[0].cpu().numpy().tolist()

print("Image embedding created!")
print("Image vector size:", len(image_vector))


# --------------------------------------------------
# 5. Store text vector in Qdrant
# --------------------------------------------------

client.upsert(
    collection_name=collection_name,
    points=[
        PointStruct(
            id=1,
            vector={
                "text": text_vector
            },
            payload={
                "content_type": "text",
                "text": text,
                "page": 1,
                "document": "sample_financial_report.pdf"
            }
        )
    ]
)

print("Text vector stored in Qdrant!")


# --------------------------------------------------
# 6. Store image vector in Qdrant
# --------------------------------------------------

client.upsert(
    collection_name=collection_name,
    points=[
        PointStruct(
            id=2,
            vector={
                "image": image_vector
            },
            payload={
                "content_type": "image",
                "image_id": "sample_image_1",
                "page": 2,
                "document": "sample_financial_report.pdf"
            }
        )
    ]
)

print("Image vector stored in Qdrant!")


print("\nMultimodal data stored successfully!")

# --------------------------------------------------
# 7. Search for similar text
# --------------------------------------------------

query = "How much did the revenue increase?"

query_vector = text_model.encode(query).tolist()

text_results = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    using="text",
    limit=1
)

print("\nText Search Result:")
print(text_results.points[0].payload)
print("Similarity Score:", text_results.points[0].score)

# --------------------------------------------------
# 8. Search for similar images
# --------------------------------------------------

image_query = Image.new("RGB", (224, 224), "white")

image_query_input = preprocess(image_query).unsqueeze(0).to(device)

with torch.no_grad():
    image_query_embedding = image_model.encode_image(image_query_input)

image_query_vector = image_query_embedding[0].cpu().numpy().tolist()

image_results = client.query_points(
    collection_name=collection_name,
    query=image_query_vector,
    using="image",
    limit=1
)

print("\nImage Search Result:")
print(image_results.points[0].payload)
print("Similarity Score:", image_results.points[0].score)