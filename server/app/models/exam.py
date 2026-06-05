"""
Exam model for managing exam metadata and lifecycle.
Links to instructor, rubrics, and submissions.

Note: This is the ORM model (database schema).
For API validation, use schemas/exam.py
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base


class ExamStatus(str, Enum):
    """Possible statuses for an exam throughout its lifecycle."""
    DRAFT = "draft"              # Instructor is still setting up
    PROCESSING = "processing"    # Submissions are being graded
    READY = "ready"              # All grades complete, ready for review
    EXPORTED = "exported"        # Grades have been exported


class Exam(Base):
    """
    Represents an exam created by an instructor.
    
    Lifecycle:
        1. draft - instructor creates exam and rubric
        2. processing - PDFs uploaded, LangGraph pipeline running
        3. ready - all grades computed, TAs can approve/override
        4. exported - final grades exported as CSV/PDF
    
    Attributes:
        id: Unique exam identifier
        instructor_id: FK to users table
        title: Human-readable exam name
        status: Current lifecycle stage
        created_at: When exam was created
        updated_at: When exam was last modified
    """
    __tablename__ = "exams"
    __table_args__ = {"schema": "public"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique exam identifier"
    )
    
    instructor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to instructor who created this exam"
    )
    
    title = Column(
        String(255),
        nullable=False,
        comment="Exam title/name"
    )
    
    status = Column(
        String(20),
        default=ExamStatus.DRAFT.value,
        nullable=False,
        comment="Current status of the exam"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When exam was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="When exam was last updated"
    )

    def __repr__(self) -> str:
        return f"<Exam(id={self.id}, title={self.title}, status={self.status})>"
