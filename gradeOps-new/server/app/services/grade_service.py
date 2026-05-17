"""
Grade service layer - Business logic for grade operations and TA review.

Handles:
- Grade creation from LangGraph pipeline
- TA review and approval/override
- Grade retrieval for dashboard
- Plagiarism flag tracking
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import Grade, TAStatus, AnswerRegion, Submission, Exam
from app.schemas import GradeCreate, GradeUpdate

logger = logging.getLogger(__name__)


class GradeService:
    """Service layer for grade operations."""
    
    @staticmethod
    def create_grade(db: Session, grade: GradeCreate, embedding: Optional[List[float]] = None) -> Grade:
        """
        Create a new grade (from LangGraph pipeline).
        
        Args:
            db: Database session
            grade: GradeCreate schema (from pipeline)
            
        Returns:
            Created Grade object
            
        Raises:
            ValueError: If answer region not found or grade exists
        """
        try:
            # Verify answer region exists
            region = db.query(AnswerRegion).filter(
                AnswerRegion.id == grade.answer_region_id
            ).first()
            if not region:
                raise ValueError(f"Answer region {grade.answer_region_id} not found")
            
            # Check if grade already exists
            existing = db.query(Grade).filter(
                Grade.answer_region_id == grade.answer_region_id
            ).first()
            if existing:
                raise ValueError(f"Grade already exists for this answer region")
            
            db_grade = Grade(
                answer_region_id=grade.answer_region_id,
                awarded_marks=grade.awarded_marks,
                ai_awarded_marks=grade.awarded_marks,
                max_marks=grade.max_marks,
                criteria_breakdown=grade.model_dump()["criteria_breakdown"],
                ai_criteria_breakdown=grade.model_dump()["criteria_breakdown"],
                justification=grade.justification,
                ai_justification=grade.justification,
                confidence_score=grade.confidence_score,
                ai_confidence_score=grade.confidence_score,
                plagiarism_flag=grade.plagiarism_flag,
                similar_submission_ids=grade.similar_submission_ids,
                ta_status=TAStatus.PENDING.value,
                embedding=embedding,
            )
            
            db.add(db_grade)
            db.commit()
            db.refresh(db_grade)
            logger.info(f"Created grade: {db_grade.id}")
            return db_grade
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating grade: {str(e)}")
            raise
    
    @staticmethod
    def get_grade_by_id(db: Session, grade_id: UUID) -> Optional[Grade]:
        """
        Get grade by ID.
        
        Args:
            db: Database session
            grade_id: Grade UUID
            
        Returns:
            Grade object or None if not found
        """
        try:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            return grade
        except Exception as e:
            logger.error(f"Error retrieving grade: {str(e)}")
            raise
    
    @staticmethod
    def get_grade_by_answer_region(db: Session, answer_region_id: UUID) -> Optional[Grade]:
        """
        Get grade for a specific answer region.
        
        Args:
            db: Database session
            answer_region_id: AnswerRegion UUID
            
        Returns:
            Grade object or None if not found
        """
        try:
            grade = db.query(Grade).filter(
                Grade.answer_region_id == answer_region_id
            ).first()
            return grade
        except Exception as e:
            logger.error(f"Error retrieving grade by answer region: {str(e)}")
            raise
    
    @staticmethod
    def get_grades_for_answer_region(db: Session, answer_region_id: UUID) -> List[Grade]:
        """
        Get all grades for an answer region (for history/tracking).
        
        Args:
            db: Database session
            answer_region_id: AnswerRegion UUID
            
        Returns:
            List of Grade objects for the answer region
        """
        try:
            grades = db.query(Grade).filter(
                Grade.answer_region_id == answer_region_id
            ).order_by(Grade.created_at.desc()).all()
            return grades
        except Exception as e:
            logger.error(f"Error retrieving grades for answer region: {str(e)}")
            raise
    
    @staticmethod
    def get_pending_grades(
        db: Session, 
        exam_id: UUID,
        priority: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Grade]:
        """
        Get all pending grades for an exam (for TA review dashboard).
        Prioritize high-confidence and plagiarism-flagged items.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            priority: Filter by priority (high, medium, low)
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of pending Grade objects
        """
        try:
            query = db.query(Grade).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id,
                Grade.ta_status == TAStatus.PENDING.value
            )
            
            # Priority ordering: plagiarism flags first, then by confidence desc
            query = query.order_by(
                Grade.plagiarism_flag.desc(),
                Grade.confidence_score.desc(),
                Grade.created_at.asc()
            )
            
            # Apply priority filter
            if priority == "high":
                query = query.filter(
                    (Grade.plagiarism_flag == True) | (Grade.confidence_score >= 0.8)
                )
            elif priority == "medium":
                query = query.filter(
                    (Grade.confidence_score >= 0.5) & (Grade.confidence_score < 0.8)
                )
            elif priority == "low":
                query = query.filter(Grade.confidence_score < 0.5)
            
            grades = query.limit(limit).offset(offset).all()
            return grades
        except Exception as e:
            logger.error(f"Error retrieving pending grades: {str(e)}")
            raise
    
    @staticmethod
    def get_grades_by_exam(
        db: Session, 
        exam_id: UUID,
        status: Optional[str] = None
    ) -> List[Grade]:
        """
        Get all grades for an exam, optionally filtered by status.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            status: Optional status filter (pending, approved, overridden)
            
        Returns:
            List of Grade objects
        """
        try:
            query = db.query(Grade).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id
            )
            
            if status:
                query = query.filter(Grade.ta_status == status)
            
            return query.order_by(Grade.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error retrieving exam grades: {str(e)}")
            raise
    
    @staticmethod
    def approve_grade(
        db: Session, 
        grade_id: UUID,
        feedback: Optional[str] = None,
        ta_user_id: Optional[UUID] = None,
    ) -> Optional[Grade]:
        """
        TA approves an AI-generated grade with optional feedback.
        
        Args:
            db: Database session
            grade_id: Grade UUID
            feedback: Optional TA feedback text
            
        Returns:
            Updated Grade or None if not found
        """
        try:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if not grade:
                logger.warning(f"Grade not found: {grade_id}")
                return None
            
            grade.ta_status = TAStatus.APPROVED.value
            grade.ta_note = feedback
            db.commit()
            db.refresh(grade)
            logger.info(f"Grade approved: {grade_id}")
            return grade
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error approving grade: {str(e)}")
            raise
    
    @staticmethod
    def override_grade(
        db: Session, 
        grade_id: UUID,
        criteria_breakdown: List[Dict[str, Any]],
        reason: str,
        ta_user_id: Optional[UUID] = None,
    ) -> Optional[Grade]:
        """
        TA overrides an AI-generated grade with new criteria scores.
        
        Args:
            db: Database session
            grade_id: Grade UUID
            criteria_breakdown: New criterion results
            reason: Reason for override
            
        Returns:
            Updated Grade or None if not found
        """
        try:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if not grade:
                logger.warning(f"Grade not found: {grade_id}")
                return None
            
            # Calculate new awarded marks from criteria
            new_awarded_marks = sum(
                c.get("awarded", 0) if isinstance(c, dict) else c.awarded 
                for c in criteria_breakdown
            )
            
            # Update fields
            grade.awarded_marks = new_awarded_marks
            grade.criteria_breakdown = [
                c if isinstance(c, dict) else c.model_dump() 
                for c in criteria_breakdown
            ]
            grade.justification = f"[TA Override Reason]: {reason}"
            grade.ta_note = reason
            grade.ta_status = TAStatus.OVERRIDDEN.value
            grade.overridden_by = ta_user_id
            grade.overridden_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(grade)
            logger.info(f"Grade overridden: {grade_id}")
            return grade
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error overriding grade: {str(e)}")
            raise
    
    @staticmethod
    def update_grade_embedding(
        db: Session, 
        grade_id: UUID, 
        embedding: List[float]
    ) -> Optional[Grade]:
        """
        Update grade embedding vector (for plagiarism detection).
        
        Args:
            db: Database session
            grade_id: Grade UUID
            embedding: 384-dim vector
            
        Returns:
            Updated Grade or None if not found
        """
        try:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if not grade:
                return None
            
            grade.embedding = embedding
            db.commit()
            db.refresh(grade)
            logger.info(f"Updated embedding for grade: {grade_id}")
            return grade
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating grade embedding: {str(e)}")
            raise
    
    @staticmethod
    def get_exam_stats(db: Session, exam_id: UUID) -> Dict[str, Any]:
        """
        Get comprehensive grade statistics for an exam.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            
        Returns:
            Dictionary with grade statistics
        """
        try:
            total_grades = db.query(func.count(Grade.id)).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id
            ).scalar() or 0
            
            pending = db.query(func.count(Grade.id)).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id,
                Grade.ta_status == TAStatus.PENDING.value
            ).scalar() or 0
            
            approved = db.query(func.count(Grade.id)).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id,
                Grade.ta_status == TAStatus.APPROVED.value
            ).scalar() or 0
            
            overridden = db.query(func.count(Grade.id)).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id,
                Grade.ta_status == TAStatus.OVERRIDDEN.value
            ).scalar() or 0
            
            plagiarism_count = db.query(func.count(Grade.id)).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id,
                Grade.plagiarism_flag == True
            ).scalar() or 0
            
            avg_score = db.query(func.avg(Grade.awarded_marks)).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id
            ).scalar() or 0.0
            
            high_conf_count = db.query(func.count(Grade.id)).join(
                AnswerRegion, AnswerRegion.id == Grade.answer_region_id
            ).join(
                Submission, Submission.id == AnswerRegion.submission_id
            ).filter(
                Submission.exam_id == exam_id,
                Grade.confidence_score >= 0.8
            ).scalar() or 0
            
            high_conf_rate = (high_conf_count / total_grades * 100) if total_grades > 0 else 0.0
            
            return {
                "total_grades": total_grades,
                "pending_review": pending,
                "approved": approved,
                "overridden": overridden,
                "plagiarism_flags": plagiarism_count,
                "average_score": float(avg_score),
                "high_confidence_rate": float(high_conf_rate)
            }
        except Exception as e:
            logger.error(f"Error getting exam stats: {str(e)}")
            raise

    @staticmethod
    def get_exam_embeddings(db: Session, exam_id: UUID) -> List[Dict[str, Any]]:
        rows = (
            db.query(Grade.answer_region_id, Grade.embedding)
            .join(AnswerRegion, AnswerRegion.id == Grade.answer_region_id)
            .join(Submission, Submission.id == AnswerRegion.submission_id)
            .filter(
                Submission.exam_id == exam_id,
                Grade.embedding.isnot(None),
            )
            .all()
        )
        return [
            {"answer_region_id": str(answer_region_id), "vector": embedding}
            for answer_region_id, embedding in rows
            if embedding
        ]
