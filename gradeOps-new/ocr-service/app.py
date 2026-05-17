import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from inference import run_ocr_inference


class OCRInferRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    question_id: str = Field(..., description="Question identifier")


class OCRInferResponse(BaseModel):
    extracted_text: str | None
    confidence: float
    question_id: str


app = FastAPI(title="GradeOps OCR Service", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/infer", response_model=OCRInferResponse)
def infer(payload: OCRInferRequest):
    try:
        text, confidence = run_ocr_inference(payload.image, payload.question_id)
        return OCRInferResponse(
            extracted_text=text,
            confidence=confidence,
            question_id=payload.question_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"detail": "Model inference failed", "error_code": "OCR_FAILURE", "message": str(exc)},
        ) from exc
