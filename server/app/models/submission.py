"""
Submission model for student-submitted exam PDFs.
Tracks upload status and lifecycle.

Note: This is the ORM model (database schema).
For API validation, use schemas/submission.py
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base


class SubmissionStatus(str, Enum):
    """Lifecycle stages for a submission."""
    UPLOADED = "uploaded"        # PDF received, not yet processed
    PROCESSING = "processing"    # Pages being split and cropped
    GRADED = "graded"           # All answer regions graded by LangGraph


class Submission(Base):
    """
    Represents a student's submitted exam PDF.
    
    Lifecycle:
        1. uploaded - instructor uploads batch PDF or student submits
        2. processing - backend splits pages and crops answer regions
        3. graded - all answer regions have grades from LangGraph
    
    Attributes:
        id: Unique submission identifier
        exam_id: FK to exams
        student_name: Name of student (optional, for manual uploads)
        roll_number: Student roll/ID (optional)
        pdf_url: URL to PDF in Supabase Storage (exam-pdfs bucket)
        status: Current processing stage
        created_at: When PDF was uploaded
        updated_at: When status changed
    
    Constraints:
        - pdf_url should point to exam-pdfs bucket in Supabase Storage
        - student_name and roll_number may be filled after OCR analysis
    """
    __tablename__ = "submissions"
    __table_args__ = {"schema": "public"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique submission identifier"
    )
    
    exam_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to exam"
    )
    
    student_name = Column(
        String(255),
        nullable=True,
        comment="Student's full name (optional, for batch processing)"
    )
    
    roll_number = Column(
        String(50),
        nullable=True,
        comment="Student's roll number or ID (optional)"
    )
    
    pdf_url = Column(
        String(500),
        nullable=False,
        comment="URL to PDF in Supabase Storage (exam-pdfs bucket)"
    )
    
    status = Column(
        String(20),
        default=SubmissionStatus.UPLOADED.value,
        nullable=False,
        comment="Current processing status"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When PDF was uploaded"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="When status was last updated"
    )

    def __repr__(self) -> str:
        return (
            f"<Submission(id={self.id}, exam_id={self.exam_id}, "
            f"student={self.student_name}, status={self.status})>"
        )
    
    def is_processing_complete(self) -> bool:
        """Check if submission has been fully processed and graded."""
        return self.status == SubmissionStatus.GRADED
