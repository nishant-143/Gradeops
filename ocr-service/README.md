# GradeOps OCR Service

Lightweight OCR microservice using **Tesseract** (open-source, no model download required).

## How it works

1. Receives a base64-encoded image + question ID via `POST /infer`
2. Preprocesses the image (grayscale → auto-contrast → sharpen)
3. Runs Tesseract with LSTM engine (`--oem 3 --psm 6`)
4. Returns extracted text + mean confidence score (0–1)

## Endpoints

### `GET /health`
```json
{ "status": "ok" }
```

### `POST /infer`
Request:
```json
{
  "image": "<base64-encoded image>",
  "question_id": "Q1"
}
```
Response:
```json
{
  "extracted_text": "The mitochondria is the powerhouse of the cell.",
  "confidence": 0.87,
  "question_id": "Q1"
}
```

`confidence` is `null` (returns `None`) when no text is detected.

## Run locally

```bash
# Install Tesseract (macOS)
brew install tesseract

# Install Tesseract (Ubuntu/Debian)
sudo apt-get install tesseract-ocr tesseract-ocr-eng

pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

## Run with Docker

```bash
docker build -t gradeops-ocr .
docker run -p 8001:8001 gradeops-ocr
```

## Why Tesseract?

- **No model download** — Tesseract ships with a trained LSTM model via the system package
- **Open source** — Apache 2.0, backed by Google
- **Well-maintained** — active GitHub repo: [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
- **pytesseract** is the standard Python wrapper: [madmaze/pytesseract](https://github.com/madmaze/pytesseract)
- Handles printed text well; for purely handwritten answers consider upgrading to [EasyOCR](https://github.com/JaidedAI/EasyOCR) by swapping `inference.py`

## Upgrading to a better model

The `inference.py` contract (`run_ocr_inference(image_b64, question_id) → (str, float)`) is stable.
To swap in a better model (e.g. EasyOCR, TrOCR, Qwen-VL), only edit `inference.py` — `app.py` stays unchanged.
