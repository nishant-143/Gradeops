"""
AnswerRegion model for cropped answer images per question.
One answer region = one question's answer from one student.

Lifecycle:
    1. Created by OpenCV when processing submission PDF
    2. OCR'd by Qwen-VL on HF Spaces
    3. Graded by LangGraph pipeline
    4. TA reviews and approves/overrides in dashboard

Note: This is the ORM model (database schema).
For API validation, use schemas/answer_region.py
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base


class AnswerRegion(Base):
    """
    Represents a cropped answer image for one question answered by one student.
    
    Created when:
        - PDF is uploaded and split into pages
        - OpenCV crops each question's answer region
        - Image stored in Supabase Storage (answer-images bucket)
    
    Then:
        - Qwen-VL OCRs the image (returns extracted_text)
        - LangGraph grades the text
        - TA reviews the grade in dashboard
    
    Attributes:
        id: Unique region identifier
        submission_id: FK to submissions
        question_id: Question number/ID (string for flexibility)
        image_url: URL to cropped image in Supabase Storage (answer-images bucket)
        extracted_text: OCR'd text from image (filled by Qwen-VL)
        created_at: When region was cropped
        updated_at: When OCR/grading happened
    
    Constraints:
        - image_url should point to answer-images bucket
        - extracted_text filled after OCR (initially nullable)
    """
    __tablename__ = "answer_regions"
    __table_args__ = {"schema": "public"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique answer region identifier"
    )
    
    submission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to submissions"
    )
    
    question_id = Column(
        String(50),
        nullable=False,
        comment="Question ID/number (e.g., 'Q1', 'Q2a', etc.)"
    )
    
    image_url = Column(
        String(500),
        nullable=False,
        comment="URL to cropped answer image in Supabase Storage (answer-images bucket)"
    )
    
    extracted_text = Column(
        Text,
        nullable=True,
        comment="OCR'd text from image (extracted by Qwen-VL)"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When answer region was created (image cropped)"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="When OCR/grading updated this record"
    )

    def __repr__(self) -> str:
        return (
            f"<AnswerRegion(id={self.id}, submission_id={self.submission_id}, "
            f"question={self.question_id})>"
        )
    
    def has_extraction(self) -> bool:
        """Check if OCR has extracted text from this answer region."""
        return self.extracted_text is not None and len(self.extracted_text.strip()) > 0
