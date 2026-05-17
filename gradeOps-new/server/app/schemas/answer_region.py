"""
Pydantic schemas for AnswerRegion API validation.
Separate from ORM models (app/models/answer_region.py).
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AnswerRegionBase(BaseModel):
    """Base answer region schema."""
    question_id: str = Field(..., description="Question ID (e.g., Q1, Q2a)")
    image_url: str = Field(..., description="URL to cropped image in Supabase")
    extracted_text: Optional[str] = Field(None, description="OCR'd text (filled by Qwen-VL)")


class AnswerRegionCreate(AnswerRegionBase):
    """Schema for creating an answer region."""
    submission_id: str = Field(..., description="Submission UUID")


class AnswerRegionUpdate(BaseModel):
    """Schema for updating an answer region."""
    extracted_text: Optional[str] = None
    image_url: Optional[str] = None


class AnswerRegionResponse(AnswerRegionBase):
    """Schema for answer region API response."""
    id: str = Field(..., description="AnswerRegion UUID")
    submission_id: str = Field(..., description="Submission UUID")
    created_at: datetime = Field(..., description="When region was created")
    updated_at: datetime = Field(..., description="Last updated")
    
    class Config:
        from_attributes = True


class AnswerRegionListResponse(BaseModel):
    """Schema for list of answer regions."""
    regions: list[AnswerRegionResponse]
    total: int = Field(..., description="Total regions")
    extracted_count: int = Field(..., description="Number with extracted text")
