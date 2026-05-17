"""
AnswerRegion service layer - Business logic for answer region operations.

Handles:
- Answer region creation and retrieval
- OCR text extraction tracking
- Region listing for submissions
"""

import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import AnswerRegion, Submission
from app.schemas import AnswerRegionCreate, AnswerRegionUpdate

logger = logging.getLogger(__name__)


class AnswerRegionService:
    """Service layer for answer region operations."""
    
    @staticmethod
    def create_answer_region(
        db: Session, 
        submission_id: UUID, 
        region: AnswerRegionCreate
    ) -> AnswerRegion:
        """
        Create a new answer region.
        
        Args:
            db: Database session
            submission_id: Submission UUID
            region: AnswerRegionCreate schema
            
        Returns:
            Created AnswerRegion object
            
        Raises:
            ValueError: If submission not found
        """
        try:
            # Verify submission exists
            submission = db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            if not submission:
                raise ValueError(f"Submission {submission_id} not found")
            
            db_region = AnswerRegion(
                submission_id=submission_id,
                question_id=region.question_id,
                image_url=region.image_url,
                extracted_text=region.extracted_text
            )
            
            db.add(db_region)
            db.commit()
            db.refresh(db_region)
            logger.info(f"Created answer region: {db_region.id}")
            return db_region
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating answer region: {str(e)}")
            raise
    
    @staticmethod
    def get_answer_region_by_id(
        db: Session, 
        region_id: UUID
    ) -> Optional[AnswerRegion]:
        """
        Get answer region by ID.
        
        Args:
            db: Database session
            region_id: AnswerRegion UUID
            
        Returns:
            AnswerRegion object or None if not found
        """
        try:
            region = db.query(AnswerRegion).filter(
                AnswerRegion.id == region_id
            ).first()
            return region
        except Exception as e:
            logger.error(f"Error retrieving answer region: {str(e)}")
            raise
    
    @staticmethod
    def get_regions_by_submission(
        db: Session, 
        submission_id: UUID,
        question_id: Optional[str] = None
    ) -> List[AnswerRegion]:
        """
        Get all answer regions for a submission.
        
        Args:
            db: Database session
            submission_id: Submission UUID
            question_id: Optional question filter
            
        Returns:
            List of AnswerRegion objects
        """
        try:
            query = db.query(AnswerRegion).filter(
                AnswerRegion.submission_id == submission_id
            )
            if question_id:
                query = query.filter(AnswerRegion.question_id == question_id)
            return query.order_by(AnswerRegion.question_id).all()
        except Exception as e:
            logger.error(f"Error retrieving answer regions: {str(e)}")
            raise
    
    @staticmethod
    def update_answer_region(
        db: Session, 
        region_id: UUID, 
        region_update: AnswerRegionUpdate
    ) -> Optional[AnswerRegion]:
        """
        Update answer region (e.g., add extracted text from OCR).
        
        Args:
            db: Database session
            region_id: AnswerRegion UUID
            region_update: AnswerRegionUpdate schema
            
        Returns:
            Updated AnswerRegion or None if not found
        """
        try:
            region = db.query(AnswerRegion).filter(
                AnswerRegion.id == region_id
            ).first()
            if not region:
                logger.warning(f"Answer region not found: {region_id}")
                return None
            
            update_data = region_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(region, key, value)
            
            db.commit()
            db.refresh(region)
            logger.info(f"Updated answer region: {region_id}")
            return region
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating answer region: {str(e)}")
            raise
    
    @staticmethod
    def delete_answer_region(db: Session, region_id: UUID) -> bool:
        """
        Delete answer region.
        
        Args:
            db: Database session
            region_id: AnswerRegion UUID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            region = db.query(AnswerRegion).filter(
                AnswerRegion.id == region_id
            ).first()
            if not region:
                logger.warning(f"Answer region not found for deletion: {region_id}")
                return False
            
            db.delete(region)
            db.commit()
            logger.info(f"Deleted answer region: {region_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting answer region: {str(e)}")
            raise
    
    @staticmethod
    def update_extracted_text(
        db: Session, 
        region_id: UUID, 
        extracted_text: str
    ) -> Optional[AnswerRegion]:
        """
        Update extracted text for a region (from OCR).
        
        Args:
            db: Database session
            region_id: AnswerRegion UUID
            extracted_text: OCR'd text
            
        Returns:
            Updated AnswerRegion or None if not found
        """
        try:
            region = db.query(AnswerRegion).filter(
                AnswerRegion.id == region_id
            ).first()
            if not region:
                return None
            
            region.extracted_text = extracted_text
            db.commit()
            db.refresh(region)
            logger.info(f"Updated OCR text for region: {region_id}")
            return region
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating OCR text: {str(e)}")
            raise
