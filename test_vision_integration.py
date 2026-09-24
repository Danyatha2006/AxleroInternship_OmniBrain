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


# Validate Vision Agent output structure
assert "answer" in result
assert "source" in result
assert "analysis_type" in result

assert result["source"]["document"] == "sample.pdf"
assert result["source"]["page"] == 1
assert result["source"]["image_id"] == 1

assert result["analysis_type"] == "vision"

print("\n✓ Search → Vision interface validation passed!")