"""
Exam service layer - Business logic for exam operations.

Handles:
- Exam creation, retrieval, updates
- Exam lifecycle management (draft→processing→ready→exported)
- Exam listings with filters
"""

import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Exam, ExamStatus, Submission, Grade, AnswerRegion
from app.schemas import ExamCreate, ExamUpdate

logger = logging.getLogger(__name__)


class ExamService:
    """Service layer for exam operations."""
    
    @staticmethod
    def create_exam(db: Session, instructor_id: UUID, exam: ExamCreate) -> Exam:
        """
        Create a new exam.
        
        Args:
            db: Database session
            instructor_id: Instructor UUID
            exam: ExamCreate schema
            
        Returns:
            Created Exam object
        """
        try:
            # Explicitly convert enum to its string value
            status_value = exam.status.value if exam.status else ExamStatus.DRAFT.value
            
            db_exam = Exam(
                instructor_id=instructor_id,
                title=exam.title,
                status=status_value
            )
            db.add(db_exam)
            db.commit()
            db.refresh(db_exam)
            logger.info(f"Created exam: {db_exam.id} - {db_exam.title}")
            return db_exam
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating exam: {str(e)}")
            raise
    
    @staticmethod
    def get_exam_by_id(db: Session, exam_id: UUID) -> Optional[Exam]:
        """
        Retrieve exam by ID.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            
        Returns:
            Exam object or None if not found
        """
        try:
            exam = db.query(Exam).filter(Exam.id == exam_id).first()
            return exam
        except Exception as e:
            logger.error(f"Error retrieving exam: {str(e)}")
            raise
    
    @staticmethod
    def get_exams(
        db: Session, 
        instructor_id: Optional[UUID] = None, 
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Exam]:
        """
        Get exams, optionally filtered by instructor and/or status.
        
        Args:
            db: Database session
            instructor_id: Optional Instructor UUID filter
            status: Optional status filter
            limit: Pagination limit
            offset: Pagination offset
            
        Returns:
            List of Exam objects
        """
        try:
            query = db.query(Exam)
            if instructor_id:
                query = query.filter(Exam.instructor_id == instructor_id)
            if status:
                query = query.filter(Exam.status == status)
            return query.order_by(Exam.created_at.desc()).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"Error retrieving exams: {str(e)}")
            raise
    
    @staticmethod
    def update_exam(db: Session, exam_id: UUID, exam_update: ExamUpdate) -> Optional[Exam]:
        """
        Update exam information.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            exam_update: ExamUpdate schema
            
        Returns:
            Updated Exam or None if not found
        """
        try:
            exam = db.query(Exam).filter(Exam.id == exam_id).first()
            if not exam:
                logger.warning(f"Exam not found: {exam_id}")
                return None
            
            update_data = exam_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(exam, key, value)
            
            db.commit()
            db.refresh(exam)
            logger.info(f"Updated exam: {exam_id}")
            return exam
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating exam: {str(e)}")
            raise
    
    @staticmethod
    @staticmethod
    def update_exam_status(
        db: Session, 
        exam_id: UUID, 
        new_status: ExamStatus
    ) -> Optional[Exam]:
        """
        Update exam status (lifecycle management).
        
        Args:
            db: Database session
            exam_id: Exam UUID
            new_status: New ExamStatus
            
        Returns:
            Updated Exam or None if not found
        """
        try:
            exam = db.query(Exam).filter(Exam.id == exam_id).first()
            if not exam:
                return None
            
            # Explicitly convert enum to its string value
            exam.status = new_status.value if isinstance(new_status, ExamStatus) else new_status
            db.commit()
            db.refresh(exam)
            logger.info(f"Exam {exam_id} status changed to: {exam.status}")
            return exam
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating exam status: {str(e)}")
            raise
    
    @staticmethod
    def delete_exam(db: Session, exam_id: UUID) -> bool:
        """
        Delete an exam (cascades to submissions, grades, etc.).
        
        Args:
            db: Database session
            exam_id: Exam UUID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            exam = db.query(Exam).filter(Exam.id == exam_id).first()
            if not exam:
                logger.warning(f"Exam not found for deletion: {exam_id}")
                return False
            
            db.delete(exam)
            db.commit()
            logger.info(f"Deleted exam: {exam_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting exam: {str(e)}")
            raise
    
    @staticmethod
    def get_exam_stats(db: Session, exam_id: UUID) -> dict:
        """
        Get statistics for an exam (submission count, grade count, etc.).
        
        Args:
            db: Database session
            exam_id: Exam UUID
            
        Returns:
            Dictionary with exam statistics
        """
        try:
            total_submissions = db.query(func.count(Submission.id)).filter(
                Submission.exam_id == exam_id
            ).scalar() or 0
            
            graded_submissions = db.query(func.count(Submission.id)).filter(
                Submission.exam_id == exam_id,
                Submission.status == "graded"
            ).scalar() or 0
            
            total_answer_regions = db.query(func.count(AnswerRegion.id)).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id
            ).scalar() or 0
            
            graded_regions = db.query(func.count(Grade.id)).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id,
                Grade.ta_status == "approved"
            ).scalar() or 0
            
            return {
                "total_submissions": total_submissions,
                "graded_submissions": graded_submissions,
                "total_answer_regions": total_answer_regions,
                "graded_regions": graded_regions,
                "grading_progress": (
                    graded_regions / total_answer_regions * 100 
                    if total_answer_regions > 0 else 0
                )
            }
        except Exception as e:
            logger.error(f"Error getting exam stats: {str(e)}")
            raise
