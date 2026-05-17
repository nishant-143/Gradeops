# GradeOps OCR Service

This service exposes the OCR contract used by the backend pipeline:

- `POST /infer`

Request:

```json
{
  "image": "<base64>",
  "question_id": "Q1"
}
```

Response:

```json
{
  "extracted_text": "....",
  "confidence": 0.87,
  "question_id": "Q1"
}
```

## Run locally

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

Set `OCR_MOCK_MODE=false` once `inference.py` is wired to your real OCR model.
