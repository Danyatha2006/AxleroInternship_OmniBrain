from vlm_service import ask_vlm
import os

def vision_agent(image_result, question):
    """
    Analyze an image retrieved by the Search Agent.

    image_result should contain image information such as:
    image_path, document, page, image_id, and score.
    """

    image_path = image_result.get("image_path")
    if not image_path:
        raise ValueError("Image path is missing from image_result.")

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Send the retrieved image and question to LLaVA
    answer = ask_vlm(
        image_path=image_path,
        question=question
    )

    # Return a structured result for LangGraph / other agents
    return {
        "answer": answer,
        "document": image_result.get("document"),
        "page": image_result.get("page"),
        "image_id": image_result.get("image_id"),
        "image_path": image_path,
        "similarity_score": image_result.get("score"),
        "analysis_type": "vision"
    }


if __name__ == "__main__":

    # Simulated result from the Search Agent
    retrieved_image = {
        "image_path": "test_chart_crop.png",
        "document": "test_revenue_chart.png",
        "page": 1,
        "image_id": 1,
        "score": 0.95
    }

    question = (
        "Analyze this chart and identify the revenue "
        "value for 2024. Give the value you can read "
        "from the chart."
    )

    print("\n" + "=" * 60)
    print("VISION AGENT TEST")
    print("=" * 60)

    result = vision_agent(
        image_result=retrieved_image,
        question=question
    )

    print("\nAnswer:")
    print(result["answer"])

    print("\nSource Information:")
    print("Document:", result["document"])
    print("Page:", result["page"])
    print("Image ID:", result["image_id"])
    print("Image Path:", result["image_path"])
    print("Similarity Score:", result["similarity_score"])
    print("Analysis Type:", result["analysis_type"])
