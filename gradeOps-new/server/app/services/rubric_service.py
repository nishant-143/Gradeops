"""
Rubric service layer - Business logic for rubric operations.

Handles:
- Rubric creation, retrieval, updates
- Criteria validation
- Rubric-exam association
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import Rubric, Exam
from app.schemas import RubricCreate, RubricUpdate

logger = logging.getLogger(__name__)


class RubricService:
    """Service layer for rubric operations."""
    
    @staticmethod
    def create_rubric(db: Session, exam_id: UUID, rubric: RubricCreate) -> Rubric:
        """
        Create a new rubric for an exam.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            rubric: RubricCreate schema
            
        Returns:
            Created Rubric object
            
        Raises:
            ValueError: If exam not found or rubric already exists
        """
        try:
            # Verify exam exists
            exam = db.query(Exam).filter(Exam.id == exam_id).first()
            if not exam:
                raise ValueError(f"Exam {exam_id} not found")
            
            # Check if rubric already exists for this exam
            existing = db.query(Rubric).filter(Rubric.exam_id == exam_id).first()
            if existing:
                raise ValueError(f"Rubric already exists for exam {exam_id}")
            
            # Create rubric
            db_rubric = Rubric(
                exam_id=exam_id,
                criteria=[c.model_dump() for c in rubric.criteria],
                max_marks=rubric.max_marks
            )
            
            db.add(db_rubric)
            db.commit()
            db.refresh(db_rubric)
            logger.info(f"Created rubric for exam: {exam_id}")
            return db_rubric
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating rubric: {str(e)}")
            raise
    
    @staticmethod
    def get_rubric_by_exam(db: Session, exam_id: UUID) -> Optional[Rubric]:
        """
        Get rubric for an exam.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            
        Returns:
            Rubric object or None if not found
        """
        try:
            rubric = db.query(Rubric).filter(Rubric.exam_id == exam_id).first()
            return rubric
        except Exception as e:
            logger.error(f"Error retrieving rubric: {str(e)}")
            raise
    
    @staticmethod
    def get_rubric_by_id(db: Session, rubric_id: UUID) -> Optional[Rubric]:
        """
        Get rubric by ID.
        
        Args:
            db: Database session
            rubric_id: Rubric UUID
            
        Returns:
            Rubric object or None if not found
        """
        try:
            rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
            return rubric
        except Exception as e:
            logger.error(f"Error retrieving rubric by ID: {str(e)}")
            raise
    
    @staticmethod
    def update_rubric(db: Session, rubric_id: UUID, rubric_update: RubricUpdate) -> Optional[Rubric]:
        """
        Update rubric.
        
        Args:
            db: Database session
            rubric_id: Rubric UUID
            rubric_update: RubricUpdate schema
            
        Returns:
            Updated Rubric or None if not found
        """
        try:
            rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
            if not rubric:
                logger.warning(f"Rubric not found: {rubric_id}")
                return None
            
            if rubric_update.criteria:
                rubric.criteria = [c.model_dump() for c in rubric_update.criteria]
            
            if rubric_update.max_marks is not None:
                rubric.max_marks = rubric_update.max_marks
            
            db.commit()
            db.refresh(rubric)
            logger.info(f"Updated rubric: {rubric_id}")
            return rubric
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating rubric: {str(e)}")
            raise
    
    @staticmethod
    def delete_rubric(db: Session, rubric_id: UUID) -> bool:
        """
        Delete a rubric.
        
        Args:
            db: Database session
            rubric_id: Rubric UUID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
            if not rubric:
                logger.warning(f"Rubric not found for deletion: {rubric_id}")
                return False
            
            db.delete(rubric)
            db.commit()
            logger.info(f"Deleted rubric: {rubric_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting rubric: {str(e)}")
            raise
    
    @staticmethod
    def validate_rubric_structure(rubric_data: Dict[str, Any]) -> bool:
        """
        Validate rubric JSON structure.
        
        Args:
            rubric_data: Rubric dictionary
            
        Returns:
            True if valid structure
            
        Raises:
            ValueError: If structure invalid
        """
        if not isinstance(rubric_data, dict):
            raise ValueError("Rubric must be a dictionary")
        
        if "criteria" not in rubric_data:
            raise ValueError("Rubric must contain 'criteria' array")
        
        if not isinstance(rubric_data["criteria"], list):
            raise ValueError("'criteria' must be an array")
        
        if len(rubric_data["criteria"]) == 0:
            raise ValueError("Rubric must have at least one criterion")
        
        # Validate each criterion
        for criterion in rubric_data["criteria"]:
            if not isinstance(criterion, dict):
                raise ValueError("Each criterion must be a dictionary")
            
            if "id" not in criterion or "description" not in criterion or "marks" not in criterion:
                raise ValueError("Each criterion must have id, description, and marks")
            
            if not isinstance(criterion["marks"], (int, float)) or criterion["marks"] < 0:
                raise ValueError("Criterion marks must be a non-negative number")
        
        return True
