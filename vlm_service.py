import base64
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "llava"


def encode_image(image_path):
    """Convert an image into base64 format."""

    with open(image_path, "rb") as image_file:
        return base64.b64encode(
            image_file.read()
        ).decode("utf-8")


def ask_vlm(image_path, question):
    """Send an image and question to LLaVA."""

    image_base64 = encode_image(image_path)

    payload = {
        "model": MODEL_NAME,
        "prompt": question,
        "images": [image_base64],
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=600
    )

    response.raise_for_status()

    result = response.json()

    return result["response"]


if __name__ == "__main__":

    image_path = (
        "data/extracted_images/"
        "page_1_image_1.jpeg"
    )

    question = (
        "Describe this image in detail. "
        "Identify any text, logos, charts, "
        "or other visual information present."
    )

    print("\n" + "=" * 60)
    print("LLaVA VLM TEST")
    print("=" * 60)

    answer = ask_vlm(
        image_path,
        question
    )

    print("\nVLM Response:")
    print(answer)