"""
Database models (ORM layer).
Uses SQLAlchemy with PostgreSQL (via Supabase).

Import all models here for easy access and migration setup.

Example:
    from app.models import User, Exam, Rubric, Submission, AnswerRegion, Grade
"""

from .base import Base, BaseModel
from .user import User, UserRole
from .exam import Exam, ExamStatus
from .rubric import Rubric
from .submission import Submission, SubmissionStatus
from .answer_region import AnswerRegion
from .grade import Grade, TAStatus
from .pipeline_job import PipelineJob, PipelineJobStatus

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "UserRole",
    "Exam",
    "ExamStatus",
    "Rubric",
    "Submission",
    "SubmissionStatus",
    "AnswerRegion",
    "Grade",
    "TAStatus",
    "PipelineJob",
    "PipelineJobStatus",
]