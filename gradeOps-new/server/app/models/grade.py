"""
Grade model for storing AI-generated grades and TA feedback.
Represents the final grade object after LangGraph pipeline completion.

This model stores:
- Predicted grades from LangGraph (criteria breakdown, justification, confidence)
- TA feedback (approval/override status)
- Plagiarism detection results
- Embeddings for semantic plagiarism detection

Note: This is the ORM model (database schema).
For API validation, use schemas/grade.py
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, String, DateTime, Integer, Float, 
    Boolean, ForeignKey, func, JSON, Text
)
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid

from .base import Base


class TAStatus(str, Enum):
    """TA decision status for a grade."""
    PENDING = "pending"          # Awaiting TA review
    APPROVED = "approved"        # TA accepted AI grade
    OVERRIDDEN = "overridden"    # TA changed the grade


class Grade(Base):
    """
    AI-generated grade for a single answer region.
    
    Lifecycle:
        1. Created by LangGraph pipeline (ta_status='pending')
        2. TA reviews in dashboard
        3. TA approves or overrides (ta_status='approved'/'overridden')
    
    Attributes:
        id: Unique grade identifier
        answer_region_id: FK to answer_regions
        awarded_marks: Marks awarded by AI
        max_marks: Total possible marks
        criteria_breakdown: JSONB with per-criterion scores
        justification: Human-readable explanation of grade
        confidence_score: AI's confidence (0-1)
        plagiarism_flag: Whether plagiarism was detected
        similar_submission_ids: List of similar submission IDs
        embedding: 384-dim vector from sentence-transformers (for plagiarism detection)
        ta_status: Whether TA approved/overridden
        created_at: When AI generated the grade
        updated_at: When TA made a decision
        
    Constraints:
        - One grade per answer_region (unique FK)
        - confidence_score must be 0-1
        - awarded_marks <= max_marks
    """
    __tablename__ = "grades"
    __table_args__ = {"schema": "public"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique grade identifier"
    )
    
    answer_region_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.answer_regions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One grade per answer region
        index=True,
        comment="FK to answer_regions (one grade per region)"
    )
    
    awarded_marks = Column(
        Integer,
        nullable=True,
        comment="Marks awarded by AI (nullable if not yet graded)"
    )

    ai_awarded_marks = Column(
        Integer,
        nullable=True,
        comment="Original AI marks. Immutable audit field."
    )
    
    max_marks = Column(
        Integer,
        nullable=False,
        comment="Total possible marks for this answer"
    )
    
    criteria_breakdown = Column(
        JSON,
        nullable=False,
        comment="""JSONB array of criterion results.
        Structure: [{"id": "c1", "awarded": 3, "justification": "..."}]"""
    )

    ai_criteria_breakdown = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Original AI criteria breakdown. Immutable audit field."
    )
    
    justification = Column(
        String(2000),
        nullable=False,
        comment="Human-readable explanation of the grade (for TA dashboard)"
    )

    ai_justification = Column(
        Text,
        nullable=False,
        default="",
        comment="Original AI justification. Immutable audit field."
    )
    
    confidence_score = Column(
        Float,
        nullable=False,
        comment="AI confidence in grade (0-1)"
    )

    ai_confidence_score = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="Original AI confidence score. Immutable audit field."
    )
    
    plagiarism_flag = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether plagiarism was detected in this answer"
    )
    
    similar_submission_ids = Column(
        JSON,  # Array of UUIDs
        default=[],
        nullable=False,
        comment="List of similar submission IDs (for plagiarism investigation)"
    )
    
    ta_status = Column(
        String(20),  # Using String instead of Enum for backwards compatibility
        default=TAStatus.PENDING.value,
        nullable=False,
        comment="TA decision: pending, approved, or overridden"
    )

    ta_note = Column(
        Text,
        nullable=True,
        comment="TA note/reason for approval or override."
    )

    overridden_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User ID of TA who overrode the grade."
    )

    overridden_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when TA overrode the grade."
    )
    
    embedding = Column(
        Vector(384),  # pgvector extension, 384-dim from sentence-transformers
        nullable=True,
        comment="Embedding vector for plagiarism detection (cosine similarity search)"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When AI grade was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="When TA made a decision on this grade"
    )

    def __repr__(self) -> str:
        return (
            f"<Grade(id={self.id}, awarded={self.awarded_marks}, "
            f"max={self.max_marks}, ta_status={self.ta_status})>"
        )
    
    def get_criteria_breakdown(self) -> List[Dict[str, Any]]:
        """
        Safely retrieve criteria breakdown from JSONB.
        
        Returns:
            List of criterion results or empty list if invalid
        """
        if isinstance(self.criteria_breakdown, list):
            return self.criteria_breakdown
        return []
    
    def get_similar_submissions(self) -> List[str]:
        """
        Safely retrieve list of similar submission IDs.
        
        Returns:
            List of submission IDs or empty list if none/invalid
        """
        if isinstance(self.similar_submission_ids, list):
            return self.similar_submission_ids
        return []
    
    def is_pending(self) -> bool:
        """Check if grade is pending TA review."""
        return self.ta_status == TAStatus.PENDING.value
    
    def is_approved(self) -> bool:
        """Check if grade was approved by TA."""
        return self.ta_status == TAStatus.APPROVED.value
    
    def is_overridden(self) -> bool:
        """Check if grade was overridden by TA."""
        return self.ta_status == TAStatus.OVERRIDDEN.value
