from vlm_service import ask_vlm


def vision_agent(image_path, question, document=None, page=None, image_id=None):
    """
    Analyze a retrieved image using the LLaVA VLM
    and return the answer with source information.
    """

    # Send image + question to LLaVA
    answer = ask_vlm(
        image_path=image_path,
        question=question
    )

    # Return structured result
    result = {
        "answer": answer,
        "document": document,
        "page": page,
        "image_id": image_id,
        "image_path": image_path
    }

    return result


if __name__ == "__main__":

    image_path = (
        "data/extracted_images/"
        "page_1_image_1.jpeg"
    )

    question = (
        "What is shown in this image? "
        "Describe the important visual information "
        "and any readable text."
    )

    result = vision_agent(
        image_path=image_path,
        question=question,
        document="sample.pdf",
        page=1,
        image_id=1
    )

    print("\n" + "=" * 60)
    print("VISION AGENT TEST")
    print("=" * 60)

    print("\nAnswer:")
    print(result["answer"])

    print("\nSource Information:")
    print("Document:", result["document"])
    print("Page:", result["page"])
    print("Image ID:", result["image_id"])
    print("Image Path:", result["image_path"])