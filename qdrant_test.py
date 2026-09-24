from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# 1. Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Create local Qdrant database
client = QdrantClient(path="qdrant_data")

# 3. Create collection only if it does not already exist
collection_name = "omnibrain_test"

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )
    print("Qdrant collection created!")
else:
    print("Qdrant collection already exists. Using it.")

# 4. Sample text
text = "Revenue increased by 15 percent in 2025."

# 5. Convert text into an embedding
embedding = model.encode(text).tolist()

# 6. Store the embedding in Qdrant
client.upsert(
    collection_name=collection_name,
    points=[
        PointStruct(
            id=1,
            vector=embedding,
            payload={
                "text": text,
                "page": 1,
                "document": "sample_financial_report.pdf"
            }
        )
    ]
)

print("Text embedding stored in Qdrant successfully!")

# 7. Search for similar text
query = "How much did revenue increase?"

query_embedding = model.encode(query).tolist()

results = client.query_points(
    collection_name=collection_name,
    query=query_embedding,
    limit=1
)

print("\nSearch Result:")
print(results.points[0].payload)
print("Similarity Score:", results.points[0].score)