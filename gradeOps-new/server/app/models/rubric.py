"""
Rubric model for defining grading criteria per exam.
Stores criteria as JSONB for flexibility while maintaining structure.

JSON Schema Example:
{
    "criteria": [
        {
            "id": "c1",
            "description": "Correct formula used",
            "marks": 3
        },
        {
            "id": "c2",
            "description": "Correct substitution",
            "marks": 3
        }
    ],
    "max_marks": 10
}

Note: This is the ORM model (database schema).
For API validation, use schemas/rubric.py
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, func, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import List, Dict, Any

from .base import Base


class Rubric(Base):
    """
    Rubric defines the grading criteria for an exam.
    
    One rubric per exam (1:1 relationship).
    Criteria stored as JSONB for flexibility—can be read by GPT-4o for grading.
    
    Attributes:
        id: Unique rubric identifier
        exam_id: FK to exams (unique—one rubric per exam)
        criteria: JSONB list of criteria objects
        max_marks: Total possible marks
        created_at: When rubric was created
        updated_at: When rubric was last modified
    """
    __tablename__ = "rubrics"
    __table_args__ = {"schema": "public"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique rubric identifier"
    )
    
    exam_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.exams.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One rubric per exam
        index=True,
        comment="FK to exam (one rubric per exam)"
    )
    
    criteria = Column(
        JSON,
        nullable=False,
        comment="""JSONB array of criteria objects.
        Each criterion should have: id, description, marks"""
    )
    
    max_marks = Column(
        Integer,
        nullable=False,
        comment="Total possible marks for this exam"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When rubric was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="When rubric was last updated"
    )

    def __repr__(self) -> str:
        return f"<Rubric(id={self.id}, exam_id={self.exam_id}, max_marks={self.max_marks})>"
    
    def get_criteria(self) -> List[Dict[str, Any]]:
        """
        Safely retrieve criteria list from JSONB.
        
        Returns:
            List of criterion objects or empty list if invalid
        """
        if isinstance(self.criteria, list):
            return self.criteria
        return []
    
    def get_criterion_by_id(self, criterion_id: str) -> Dict[str, Any] | None:
        """
        Find a specific criterion by ID.
        
        Args:
            criterion_id: The id of the criterion to find
            
        Returns:
            Criterion object or None if not found
        """
        for criterion in self.get_criteria():
            if criterion.get("id") == criterion_id:
                return criterion
        return None
