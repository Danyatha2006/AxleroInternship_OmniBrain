from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Configuration
# --------------------------------------------------

QDRANT_PATH = "multimodal_qdrant_data"
COLLECTION_NAME = "omnibrain_multimodal"


# --------------------------------------------------
# Load text embedding model
# --------------------------------------------------

print("Loading text embedding model...")

text_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Model loaded successfully!")


# --------------------------------------------------
# Connect to Qdrant
# --------------------------------------------------

client = QdrantClient(path=QDRANT_PATH)


# --------------------------------------------------
# Text similarity search
# --------------------------------------------------

query = "What is OmniBrain and what problem does it solve?"

query_vector = text_model.encode(query).tolist()


results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    using="text",
    limit=3
)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n" + "=" * 60)
print("REAL TEXT RETRIEVAL TEST")
print("=" * 60)

print("Query:", query)

for i, result in enumerate(results.points, start=1):

    print(f"\nResult {i}")
    print("-" * 40)

    print("Score:", result.score)
    print("Document:", result.payload.get("document"))
    print("Page:", result.payload.get("page"))
    print("Chunk ID:", result.payload.get("chunk_id"))

    print("\nRetrieved text:")
    print(result.payload.get("text"))