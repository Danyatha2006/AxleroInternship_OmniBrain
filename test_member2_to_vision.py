from vision_agent import vision_agent


retrieved_image = {
    "image_path": "member2_page_1.png",
    "document": "Member2 document",
    "page": 1,
    "image_id": 1,
    "score": 0.92,
}

question = (
    "Describe the important visual information "
    "in this image."
)

result = vision_agent(
    image_result=retrieved_image,
    question=question,
)

print("\n" + "=" * 60)
print("MEMBER 2 IMAGE → LLAVA VISION AGENT TEST")
print("=" * 60)

print("\nAnswer:")
print(result["answer"])

print("\nSource:")
print(result["source"])

print("\nAnalysis Type:")
print(result["analysis_type"])

assert "answer" in result
assert "source" in result
assert result["source"]["page"] == 1
assert result["source"]["image_path"] == "member2_page_1.png"
assert result["analysis_type"] == "vision"

print("\n✓ Member 2 image → Vision Agent integration passed!")