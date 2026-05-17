"""
Submission service layer - Business logic for submission operations.

Handles:
- Submission creation, retrieval, updates
- PDF upload tracking
- Processing status management
"""

import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Submission, SubmissionStatus, AnswerRegion, Grade, Exam
from app.schemas import SubmissionCreate, SubmissionUpdate

logger = logging.getLogger(__name__)


class SubmissionService:
    """Service layer for submission operations."""
    
    @staticmethod
    def create_submission(db: Session, exam_id: UUID, submission: SubmissionCreate) -> Submission:
        """
        Create a new submission.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            submission: SubmissionCreate schema
            
        Returns:
            Created Submission object
            
        Raises:
            ValueError: If exam not found
        """
        try:
            # Verify exam exists
            exam = db.query(Exam).filter(Exam.id == exam_id).first()
            if not exam:
                raise ValueError(f"Exam {exam_id} not found")
            
            db_submission = Submission(
                exam_id=exam_id,
                student_name=submission.student_name,
                roll_number=submission.roll_number,
                pdf_url=submission.pdf_url,
                status=SubmissionStatus.UPLOADED.value
            )
            
            db.add(db_submission)
            db.commit()
            db.refresh(db_submission)
            logger.info(f"Created submission: {db_submission.id}")
            return db_submission
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating submission: {str(e)}")
            raise
    
    @staticmethod
    def get_submission_by_id(db: Session, submission_id: UUID) -> Optional[Submission]:
        """
        Get submission by ID.
        
        Args:
            db: Database session
            submission_id: Submission UUID
            
        Returns:
            Submission object or None if not found
        """
        try:
            submission = db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            return submission
        except Exception as e:
            logger.error(f"Error retrieving submission: {str(e)}")
            raise
    
    @staticmethod
    def get_submissions_by_exam(
        db: Session, 
        exam_id: UUID,
        status: Optional[str] = None
    ) -> List[Submission]:
        """
        Get all submissions for an exam.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            status: Optional status filter
            
        Returns:
            List of Submission objects
        """
        try:
            query = db.query(Submission).filter(Submission.exam_id == exam_id)
            if status:
                query = query.filter(Submission.status == status)
            return query.order_by(Submission.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error retrieving submissions: {str(e)}")
            raise
    
    @staticmethod
    def update_submission(
        db: Session, 
        submission_id: UUID, 
        submission_update: SubmissionUpdate
    ) -> Optional[Submission]:
        """
        Update submission.
        
        Args:
            db: Database session
            submission_id: Submission UUID
            submission_update: SubmissionUpdate schema
            
        Returns:
            Updated Submission or None if not found
        """
        try:
            submission = db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            if not submission:
                logger.warning(f"Submission not found: {submission_id}")
                return None
            
            update_data = submission_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(submission, key, value)
            
            db.commit()
            db.refresh(submission)
            logger.info(f"Updated submission: {submission_id}")
            return submission
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating submission: {str(e)}")
            raise
    
    @staticmethod
    def update_submission_status(
        db: Session, 
        submission_id: UUID, 
        new_status: SubmissionStatus
    ) -> Optional[Submission]:
        """
        Update submission status (processing lifecycle).
        
        Args:
            db: Database session
            submission_id: Submission UUID
            new_status: New status
            
        Returns:
            Updated Submission or None if not found
        """
        try:
            submission = db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            if not submission:
                return None
            
            # Explicitly convert enum to its string value
            submission.status = new_status.value if isinstance(new_status, SubmissionStatus) else new_status
            db.commit()
            db.refresh(submission)
            logger.info(f"Submission {submission_id} status: {submission.status}")
            return submission
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating submission status: {str(e)}")
            raise
    
    @staticmethod
    def delete_submission(db: Session, submission_id: UUID) -> bool:
        """
        Delete submission (cascades to answer regions and grades).
        
        Args:
            db: Database session
            submission_id: Submission UUID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            submission = db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            if not submission:
                logger.warning(f"Submission not found for deletion: {submission_id}")
                return False
            
            db.delete(submission)
            db.commit()
            logger.info(f"Deleted submission: {submission_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting submission: {str(e)}")
            raise
    
    @staticmethod
    def get_submission_stats(db: Session, submission_id: UUID) -> dict:
        """
        Get statistics for a submission.
        
        Args:
            db: Database session
            submission_id: Submission UUID
            
        Returns:
            Dictionary with submission statistics
        """
        try:
            total_questions = db.query(func.count(AnswerRegion.id)).filter(
                AnswerRegion.submission_id == submission_id
            ).scalar() or 0
            
            graded_questions = db.query(func.count(Grade.id)).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).filter(
                AnswerRegion.submission_id == submission_id,
                Grade.ta_status != "pending"
            ).scalar() or 0
            
            return {
                "total_questions": total_questions,
                "graded_questions": graded_questions,
                "progress": (
                    graded_questions / total_questions * 100 
                    if total_questions > 0 else 0
                )
            }
        except Exception as e:
            logger.error(f"Error getting submission stats: {str(e)}")
            raise
