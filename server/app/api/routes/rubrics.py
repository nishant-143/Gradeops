"""
Rubric management routes.

Endpoints:
- POST /rubrics - Create rubric for exam
- GET /rubrics/{exam_id} - Get rubric for exam
- GET /rubrics/id/{rubric_id} - Get rubric by ID
- PUT /rubrics/{rubric_id} - Update rubric
- DELETE /rubrics/{rubric_id} - Delete rubric
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.core.supabase import get_db_session
from app.schemas import RubricCreate, RubricUpdate, RubricResponse, ErrorResponse
from app.services import RubricService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rubrics", tags=["rubrics"])


@router.post(
    "",
    response_model=RubricResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rubric(
    exam_id: str = Query(..., description="Exam UUID"),
    rubric: RubricCreate = Body(...),
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Create a rubric for an exam.
    
    Args:
        exam_id: Exam UUID
        rubric: RubricCreate schema with criteria
        db: Database session
        
    Returns:
        Created RubricResponse
    """
    try:
        exam_uuid = UUID(exam_id)
        db_rubric = RubricService.create_rubric(db, exam_uuid, rubric)
        logger.info(f"Rubric created for exam: {exam_id}")
        return RubricResponse.model_validate(db_rubric)
        
    except ValueError as e:
        logger.warning(f"Rubric creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating rubric: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create rubric"
        )


@router.get(
    "/{exam_id}",
    response_model=RubricResponse,
)
def get_rubric_by_exam(
    exam_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    """
    Get rubric for an exam.
    
    Args:
        exam_id: Exam UUID
        db: Database session
        
    Returns:
        RubricResponse
    """
    try:
        exam_uuid = UUID(exam_id)
        rubric = RubricService.get_rubric_by_exam(db, exam_uuid)
        
        if not rubric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rubric for exam {exam_id} not found"
            )
        
        return RubricResponse.model_validate(rubric)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rubric: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rubric"
        )


@router.get(
    "/id/{rubric_id}",
    response_model=RubricResponse,
)
def get_rubric_by_id(
    rubric_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    """
    Get rubric by ID.
    
    Args:
        rubric_id: Rubric UUID
        db: Database session
        
    Returns:
        RubricResponse
    """
    try:
        rubric_uuid = UUID(rubric_id)
        rubric = RubricService.get_rubric_by_id(db, rubric_uuid)
        
        if not rubric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rubric {rubric_id} not found"
            )
        
        return RubricResponse.model_validate(rubric)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid rubric ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rubric: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rubric"
        )


@router.put(
    "/{rubric_id}",
    response_model=RubricResponse,
)
def update_rubric(
    rubric_id: str,
    rubric_update: RubricUpdate,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Update a rubric.
    
    Args:
        rubric_id: Rubric UUID
        rubric_update: RubricUpdate schema
        db: Database session
        
    Returns:
        Updated RubricResponse
    """
    try:
        rubric_uuid = UUID(rubric_id)
        rubric = RubricService.update_rubric(db, rubric_uuid, rubric_update)
        
        if not rubric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rubric {rubric_id} not found"
            )
        
        logger.info(f"Rubric updated: {rubric_id}")
        return RubricResponse.model_validate(rubric)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid rubric ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rubric: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update rubric"
        )


@router.delete(
    "/{rubric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rubric(
    rubric_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Delete a rubric.
    
    Args:
        rubric_id: Rubric UUID
        db: Database session
    """
    try:
        rubric_uuid = UUID(rubric_id)
        deleted = RubricService.delete_rubric(db, rubric_uuid)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rubric {rubric_id} not found"
            )
        
        logger.info(f"Rubric deleted: {rubric_id}")
        return None
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid rubric ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rubric: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete rubric"
        )
