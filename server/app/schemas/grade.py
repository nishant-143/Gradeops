"""
Pydantic schemas for Grade API validation.
Separate from ORM models (app/models/grade.py).
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class TAStatusEnum(str, Enum):
    """TA decision status."""
    PENDING = "pending"
    APPROVED = "approved"
    OVERRIDDEN = "overridden"


class CriterionResultBase(BaseModel):
    """Result for a single criterion."""
    id: str = Field(..., description="Criterion ID")
    awarded: int = Field(..., ge=0, description="Marks awarded")
    justification: str = Field(..., description="Why this score")


class GradeBase(BaseModel):
    """Base grade schema."""
    awarded_marks: Optional[int] = Field(None, ge=0, description="Marks awarded")
    ai_awarded_marks: Optional[int] = Field(None, ge=0, description="Original AI marks")
    max_marks: int = Field(..., ge=0, description="Total possible marks")
    criteria_breakdown: List[CriterionResultBase] = Field(..., description="Per-criterion scores")
    ai_criteria_breakdown: List[CriterionResultBase] = Field(default=[], description="Immutable AI breakdown")
    justification: str = Field(..., max_length=2000, description="Grade explanation")
    ai_justification: str = Field(default="", description="Immutable AI justification")
    confidence_score: float = Field(..., ge=0, le=1, description="AI confidence (0-1)")
    ai_confidence_score: float = Field(default=0, ge=0, le=1, description="Immutable AI confidence")
    plagiarism_flag: bool = Field(default=False, description="Plagiarism detected?")
    similar_submission_ids: List[str] = Field(default=[], description="Similar submissions")
    ta_note: Optional[str] = Field(None, description="TA review note")
    
    @field_validator("awarded_marks")
    @classmethod
    def validate_awarded_marks(cls, v, values):
        """Ensure awarded_marks <= max_marks."""
        if v is not None and "max_marks" in values.data:
            if v > values.data["max_marks"]:
                raise ValueError("awarded_marks cannot exceed max_marks")
        return v


class GradeCreate(GradeBase):
    """Schema for creating a grade (from LangGraph)."""
    answer_region_id: str = Field(..., description="AnswerRegion UUID")


class GradeUpdate(BaseModel):
    """Schema for updating a grade (TA override)."""
    awarded_marks: Optional[int] = None
    ta_status: Optional[TAStatusEnum] = None
    justification: Optional[str] = None
    criteria_breakdown: Optional[List[CriterionResultBase]] = None


class GradeApprove(BaseModel):
    """Schema for TA grade approval."""
    feedback: Optional[str] = Field(None, max_length=1000, description="TA feedback")


class GradeOverride(BaseModel):
    """Schema for TA grade override."""
    criteria_breakdown: List[CriterionResultBase] = Field(..., description="Adjusted criterion scores")
    reason: str = Field(..., max_length=2000, description="Reason for override")


class GradeResponse(GradeBase):
    """Schema for grade API response."""
    id: str = Field(..., description="Grade UUID")
    answer_region_id: str = Field(..., description="AnswerRegion UUID")
    ta_status: TAStatusEnum = Field(..., description="TA review status")
    overridden_by: Optional[str] = Field(None, description="TA user ID who overrode")
    overridden_at: Optional[datetime] = Field(None, description="Override timestamp")
    created_at: datetime = Field(..., description="When grade was created")
    updated_at: datetime = Field(..., description="When TA made decision")
    
    class Config:
        from_attributes = True


class GradeQueueResponse(BaseModel):
    """Schema for TA review queue item."""
    grade: GradeResponse
    student_name: Optional[str] = Field(None, description="Student name")
    question_id: str = Field(..., description="Question ID")
    image_url: str = Field(..., description="Answer image URL")
    extracted_text: Optional[str] = Field(None, description="OCR'd text")


class GradeQueueListResponse(BaseModel):
    """Schema for list of grades in TA queue."""
    queue: List[GradeQueueResponse]
    total: int = Field(..., description="Total items in queue")
    pending_count: int = Field(..., description="Pending TA review")
    approved_count: int = Field(..., description="TA approved")
    overridden_count: int = Field(..., description="TA overridden")
