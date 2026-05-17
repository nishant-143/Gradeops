"""
Pydantic schemas for Rubric API validation.
Separate from ORM models (app/models/rubric.py).
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class CriterionBase(BaseModel):
    """Base criterion schema."""
    id: str = Field(..., description="Criterion ID")
    description: str = Field(..., min_length=1, description="Criterion description")
    marks: int = Field(..., ge=0, description="Marks for this criterion")


class RubricBase(BaseModel):
    """Base rubric schema."""
    criteria: List[CriterionBase] = Field(..., description="List of criteria")
    max_marks: int = Field(..., ge=0, description="Total possible marks")
    
    @field_validator("criteria")
    @classmethod
    def validate_criteria(cls, v):
        """Ensure at least one criterion and unique IDs."""
        if not v:
            raise ValueError("Rubric must have at least one criterion")
        
        ids = [c.id for c in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Criterion IDs must be unique")
        
        return v


class RubricCreate(RubricBase):
    """Schema for creating a rubric."""
    pass


class RubricUpdate(BaseModel):
    """Schema for updating a rubric."""
    criteria: Optional[List[CriterionBase]] = None
    max_marks: Optional[int] = Field(None, ge=0)


class RubricResponse(RubricBase):
    """Schema for rubric API response."""
    id: UUID = Field(..., description="Rubric UUID")
    exam_id: UUID = Field(..., description="Exam UUID")
    created_at: datetime = Field(..., description="When rubric was created")
    updated_at: datetime = Field(..., description="When rubric was last updated")
    
    class Config:
        from_attributes = True
