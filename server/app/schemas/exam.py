"""
Pydantic schemas for Exam API validation.
Separate from ORM models (app/models/exam.py).
"""

from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field


class ExamStatusEnum(str, Enum):
    """Exam lifecycle states."""
    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"
    EXPORTED = "exported"


class ExamBase(BaseModel):
    """Base exam schema."""
    title: str = Field(..., min_length=1, max_length=255, description="Exam title")
    status: ExamStatusEnum = Field(default=ExamStatusEnum.DRAFT, description="Exam status")


class ExamCreate(ExamBase):
    """Schema for creating a new exam."""
    pass


class ExamUpdate(BaseModel):
    """Schema for updating an exam."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[ExamStatusEnum] = None


class ExamResponse(ExamBase):
    """Schema for exam API response."""
    id: UUID = Field(..., description="Exam UUID")
    instructor_id: UUID = Field(..., description="Instructor UUID")
    created_at: datetime = Field(..., description="When exam was created")
    updated_at: datetime = Field(..., description="When exam was last updated")
    
    class Config:
        from_attributes = True


class ExamListResponse(BaseModel):
    """Schema for list of exams."""
    exams: list[ExamResponse]
    total: int = Field(..., description="Total number of exams")


class ExamDetailResponse(ExamResponse):
    """Detailed exam response including related data."""
    submission_count: int = Field(default=0, description="Number of submissions")
    graded_count: int = Field(default=0, description="Number of graded submissions")
