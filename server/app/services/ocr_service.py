import base64
import logging
from typing import Any, Dict

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    @retry(stop=stop_after_attempt(settings.OCR_MAX_RETRIES), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def _call_remote(self, image_bytes: bytes, question_id: str) -> Dict[str, Any]:
        if not settings.OCR_API_URL:
            raise RuntimeError("OCR_API_URL is not set")

        payload = {
            "image": base64.b64encode(image_bytes).decode("utf-8"),
            "question_id": question_id,
        }
        async with httpx.AsyncClient(timeout=settings.OCR_TIMEOUT_SECONDS) as client:
            res = await client.post(f"{settings.OCR_API_URL.rstrip('/')}/infer", json=payload)
            res.raise_for_status()
            return res.json()

    async def extract_text(self, image_bytes: bytes, question_id: str) -> Dict[str, Any]:
        if settings.OCR_API_URL:
            return await self._call_remote(image_bytes, question_id)

        if settings.OCR_ENABLE_LOCAL_FALLBACK:
            logger.warning("ocr.local_fallback question_id=%s", question_id)
            return {
                "extracted_text": None,
                "confidence": 0.0,
                "question_id": question_id,
                "fallback": "local-disabled",
            }

        raise RuntimeError("OCR service unavailable and local fallback disabled")


ocr_service = OCRService()
