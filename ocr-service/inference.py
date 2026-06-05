import base64
import io
from typing import Tuple

import pytesseract
from PIL import Image, ImageFilter, ImageOps


def _preprocess(image: Image.Image) -> Image.Image:
    """
    Light preprocessing to improve Tesseract accuracy on handwritten/printed answers.
    - Convert to grayscale
    - Auto-contrast
    - Mild sharpening
    """
    image = image.convert("L")          # grayscale
    image = ImageOps.autocontrast(image, cutoff=2)
    image = image.filter(ImageFilter.SHARPEN)
    return image


def run_ocr_inference(image_b64: str, question_id: str) -> Tuple[str | None, float]:
    """
    Run Tesseract OCR on a base64-encoded image.

    Returns:
        (extracted_text, confidence)
        confidence is the mean character-level confidence reported by Tesseract (0–1).
        Returns (None, 0.0) if no text is detected.
    """
    image_bytes = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_bytes))
    image = _preprocess(image)

    # --psm 6  → assume a uniform block of text (good for answer boxes)
    # --oem 3  → use LSTM engine (most accurate)
    config = "--psm 6 --oem 3"

    # Get detailed output with per-word confidences
    data = pytesseract.image_to_data(
        image,
        config=config,
        output_type=pytesseract.Output.DICT,
    )

    # Filter to words with confidence >= 0 (Tesseract uses -1 for non-word rows)
    confidences = [c for c in data["conf"] if c >= 0]
    words = [
        data["text"][i]
        for i, c in enumerate(data["conf"])
        if c >= 0 and data["text"][i].strip()
    ]

    if not words:
        return None, 0.0

    extracted_text = " ".join(words).strip()
    mean_confidence = sum(confidences) / len(confidences) / 100.0  # normalise to 0–1

    return extracted_text, round(mean_confidence, 4)
