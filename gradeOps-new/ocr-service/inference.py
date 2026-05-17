import base64
import io
import os
from typing import Tuple

from PIL import Image


def run_ocr_inference(image_b64: str, question_id: str) -> Tuple[str | None, float]:
    # Placeholder production contract implementation.
    # Swap internals with your Qwen-VL inference path when ready.
    image_bytes = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_bytes))
    _ = image.size  # touch image to validate input

    if os.getenv("OCR_MOCK_MODE", "true").lower() == "true":
        return None, 0.0

    # Implement real model call here.
    return None, 0.0
