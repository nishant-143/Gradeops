"""
Answer Region management routes.

Endpoints:
- POST /answer-regions - Create answer region
- GET /answer-regions/{answer_region_id} - Get answer region details
- GET /answer-regions/submission/{submission_id} - List regions for submission
- PATCH /answer-regions/{answer_region_id} - Update answer region
- DELETE /answer-regions/{answer_region_id} - Delete answer region
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.core.supabase import get_db_session
from app.schemas import (
    AnswerRegionCreate,
    AnswerRegionUpdate,
    AnswerRegionResponse,
    AnswerRegionListResponse,
    ErrorResponse,
)
from app.services import AnswerRegionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/answer-regions", tags=["answer-regions"])


@router.post(
    "",
    response_model=AnswerRegionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_answer_region(
    submission_id: str = Query(...),
    region: AnswerRegionCreate = None,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Create a new answer region for a submission.
    
    Args:
        submission_id: Submission UUID
        region: AnswerRegionCreate schema
        db: Database session
        
    Returns:
        AnswerRegionResponse with created region
    """
    try:
        submission_uuid = UUID(submission_id)
        db_region = AnswerRegionService.create_answer_region(
            db, submission_uuid, region
        )
        
        return AnswerRegionResponse.model_validate(db_region)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission ID format"
        )
    except Exception as e:
        logger.error(f"Error creating answer region: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create answer region"
        )


@router.get(
    "/{answer_region_id}",
    response_model=AnswerRegionResponse,
)
def get_answer_region(
    answer_region_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    """
    Get answer region details.
    
    Args:
        answer_region_id: AnswerRegion UUID
        db: Database session
        
    Returns:
        AnswerRegionResponse with region details
    """
    try:
        region_uuid = UUID(answer_region_id)
        region = AnswerRegionService.get_answer_region_by_id(db, region_uuid)
        
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer region {answer_region_id} not found"
            )
        
        return AnswerRegionResponse.model_validate(region)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer region ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting answer region: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get answer region"
        )


@router.get(
    "/submission/{submission_id}",
    response_model=AnswerRegionListResponse,
)
def list_answer_regions_for_submission(
    submission_id: str,
    question_id: str = Query(None, description="Optional question ID filter"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    """
    List all answer regions for a submission.
    
    Args:
        submission_id: Submission UUID
        question_id: Optional question ID filter
        limit: Number of results to return
        offset: Pagination offset
        db: Database session
        
    Returns:
        AnswerRegionListResponse with regions
    """
    try:
        submission_uuid = UUID(submission_id)
        regions = AnswerRegionService.get_regions_by_submission(
            db, submission_uuid, question_id=question_id
        )
        
        # Manual pagination
        paginated = regions[offset : offset + limit]
        
        return AnswerRegionListResponse(
            regions=[
                AnswerRegionResponse.model_validate(r) for r in paginated
            ],
            total=len(regions)
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission ID format"
        )
    except Exception as e:
        logger.error(f"Error listing answer regions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list answer regions"
        )


@router.patch(
    "/{answer_region_id}",
    response_model=AnswerRegionResponse,
)
def update_answer_region(
    answer_region_id: str,
    update: AnswerRegionUpdate,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Update an answer region.
    
    Args:
        answer_region_id: AnswerRegion UUID
        update: AnswerRegionUpdate schema
        db: Database session
        
    Returns:
        Updated AnswerRegionResponse
    """
    try:
        region_uuid = UUID(answer_region_id)
        region = AnswerRegionService.update_answer_region(
            db, region_uuid, update
        )
        
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer region {answer_region_id} not found"
            )
        
        logger.info(f"Answer region updated: {answer_region_id}")
        return AnswerRegionResponse.model_validate(region)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer region ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating answer region: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update answer region"
        )


@router.delete(
    "/{answer_region_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_answer_region(
    answer_region_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Delete an answer region.
    
    Args:
        answer_region_id: AnswerRegion UUID
        db: Database session
    """
    try:
        region_uuid = UUID(answer_region_id)
        deleted = AnswerRegionService.delete_answer_region(db, region_uuid)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer region {answer_region_id} not found"
            )
        
        logger.info(f"Answer region deleted: {answer_region_id}")
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer region ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting answer region: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete answer region"
        )
