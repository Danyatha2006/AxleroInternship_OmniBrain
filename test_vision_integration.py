from vision_agent import vision_agent


# Simulated result that would normally come from
# the Search Agent / Qdrant.
retrieved_image = {
    "image_path": "test_chart_crop.png",
    "document": "sample.pdf",
    "page": 1,
    "image_id": 1,
    "score": 0.95
}

question = "What information is shown in this image?"


result = vision_agent(
    image_result=retrieved_image,
    question=question
)


print("\n" + "=" * 60)
print("SEARCH AGENT → VISION AGENT INTEGRATION TEST")
print("=" * 60)

print("\nAnswer:")
print(result["answer"])

print("\nSource:")
print(result["source"])

print("\nAnalysis Type:")
print(result["analysis_type"])
