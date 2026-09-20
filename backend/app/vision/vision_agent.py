from pathlib import Path
from typing import Any

from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor


MODEL_NAME = "Salesforce/blip-image-captioning-base"


class VisionAgent:
    def __init__(self):
        self._processor = None
        self._model = None

    def _load_model(self):
        if self._processor is not None and self._model is not None:
            return

        self._processor = BlipProcessor.from_pretrained(MODEL_NAME)
        self._model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)

    def _resolve_image_path(self, image_reference: str | None):
        if not image_reference:
            return None

        reference = image_reference.strip()

        if not reference:
            return None

        marker = "/extracted_images/"

        if marker in reference:
            relative_path = reference.split(marker, 1)[1]
            backend_dir = Path(__file__).resolve().parents[2]
            return backend_dir / "extracted_images" / relative_path

        direct_path = Path(reference)

        if direct_path.exists():
            return direct_path

        return None

    def run(self, image_reference: str | None, query: str) -> dict[str, Any]:

        query = query.strip()

        if not image_reference:
            return {
                "image_reference": None,
                "query": query,
                "answer": "",
            }

        image_path = self._resolve_image_path(image_reference)

        if image_path is None or not image_path.exists():
            return {
                "image_reference": image_reference,
                "query": query,
                "answer": "",
                "error": "Image file not found.",
            }

        try:
            self._load_model()

            image = Image.open(image_path).convert("RGB")

            # BLIP captioning works better without feeding the user's
            # question as the generation prompt.
            inputs = self._processor(
                images=image,
                return_tensors="pt",
            )

            outputs = self._model.generate(
                **inputs,
                max_new_tokens=80,
                num_beams=5,
            )

            answer = self._processor.decode(
                outputs[0],
                skip_special_tokens=True,
            ).strip()

            return {
                "image_reference": image_reference,
                "query": query,
                "answer": answer,
                "image_path": str(image_path),
            }

        except Exception as exc:
            return {
                "image_reference": image_reference,
                "query": query,
                "answer": "",
                "error": str(exc),
            }