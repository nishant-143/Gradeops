"""
Pydantic schemas for Submission API validation.
Separate from ORM models (app/models/submission.py).
"""

from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field


class SubmissionStatusEnum(str, Enum):
    """Submission lifecycle states."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    GRADED = "graded"


class SubmissionBase(BaseModel):
    """Base submission schema."""
    student_name: Optional[str] = Field(None, max_length=255, description="Student name")
    roll_number: Optional[str] = Field(None, max_length=50, description="Student roll number")
    pdf_url: Optional[str] = Field(None, description="URL to PDF in Supabase Storage")


class SubmissionCreate(SubmissionBase):
    """Schema for creating a submission."""
    pass


class SubmissionUpdate(BaseModel):
    """Schema for updating a submission."""
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    status: Optional[SubmissionStatusEnum] = None


class SubmissionResponse(SubmissionBase):
    """Schema for submission API response."""
    id: UUID = Field(..., description="Submission UUID")
    exam_id: UUID = Field(..., description="Exam UUID")
    status: SubmissionStatusEnum = Field(..., description="Current status")
    created_at: datetime = Field(..., description="When submitted")
    updated_at: datetime = Field(..., description="Last updated")
    
    class Config:
        from_attributes = True


class SubmissionListResponse(BaseModel):
    """Schema for list of submissions."""
    submissions: list[SubmissionResponse]
    total: int = Field(..., description="Total submissions")
    graded_count: int = Field(..., description="Number graded")
