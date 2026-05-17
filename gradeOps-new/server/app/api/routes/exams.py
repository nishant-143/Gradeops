"""
Exam management routes.

Endpoints:
- POST /exams - Create new exam
- GET /exams - List exams for current instructor
- GET /exams/{exam_id} - Get exam details
- PUT /exams/{exam_id} - Update exam
- DELETE /exams/{exam_id} - Delete exam
- GET /exams/{exam_id}/stats - Get exam grading statistics
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.core.supabase import get_db_session
from app.models import Exam, ExamStatus
from app.schemas import (
    ExamCreate,
    ExamUpdate,
    ExamResponse,
    ExamListResponse,
    ErrorResponse,
)
from app.services import ExamService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/exams", tags=["exams"])


@router.post(
    "",
    response_model=ExamResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exam(
    exam: ExamCreate,
    instructor_id: str = Query(..., description="Instructor UUID"),
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Create a new exam.

    The exam starts in DRAFT status. Instructor can add rubric and upload submissions.

    Args:
        exam: ExamCreate schema with title and optional status
        instructor_id: UUID of the instructor creating the exam
        db: Database session

    Returns:
        ExamResponse with created exam details

    Raises:
        HTTPException 400: If validation fails
        HTTPException 401: If unauthorized
        HTTPException 500: If database error occurs
    """
    try:
        # Validate instructor_id is a valid UUID
        try:
            instructor_uuid = UUID(instructor_id)
        except ValueError:
            logger.warning(f"Invalid instructor_id format: {instructor_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid instructor_id format. Must be a valid UUID.",
            )

        # Create exam
        db_exam = ExamService.create_exam(db, instructor_uuid, exam)

        logger.info(f"Exam created: {db_exam.id} by instructor {instructor_uuid}")
        return ExamResponse.model_validate(db_exam)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating exam: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create exam",
        )


@router.get(
    "",
    response_model=ExamListResponse,
)
def list_exams(
    instructor_id: Optional[str] = Query(None, description="Optional Instructor UUID filter"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    """
    List exams.
    
    If instructor_id is provided, filters by that instructor.
    Instructors can see their own exams, TAs can see all exams (optionally filtered).

    Args:
        instructor_id: Optional UUID of the instructor
        status_filter: Optional status filter (draft, processing, ready, exported)
        limit: Number of exams to return
        offset: Pagination offset
        db: Database session

    Returns:
        ExamListResponse
    """
    try:
        instructor_uuid = None
        if instructor_id:
            try:
                instructor_uuid = UUID(instructor_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid instructor_id format",
                )
                
        exams = ExamService.get_exams(
            db, instructor_uuid, status_filter, limit, offset
        )
        return ExamListResponse(
            exams=[ExamResponse.model_validate(exam) for exam in exams],
            total=len(exams),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing exams: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list exams",
        )


@router.get(
    "/{exam_id}",
    response_model=ExamResponse,
)
def get_exam(
    exam_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    """
    Get exam details.

    Args:
        exam_id: Exam UUID
        db: Database session

    Returns:
        ExamResponse
    """
    try:
        exam_uuid = UUID(exam_id)
        exam = ExamService.get_exam_by_id(db, exam_uuid)

        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exam {exam_id} not found",
            )

        return ExamResponse.model_validate(exam)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam_id format",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exam: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get exam",
        )


@router.put(
    "/{exam_id}",
    response_model=ExamResponse,
)
def update_exam(
    exam_id: str,
    exam_update: ExamUpdate,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Update exam details.

    Can only update title and status. Some status transitions may be restricted
    based on business logic (e.g., can't go back to DRAFT once in PROCESSING).

    Args:
        exam_id: Exam UUID
        exam_update: ExamUpdate schema with fields to update
        db: Database session

    Returns:
        Updated ExamResponse

    Raises:
        HTTPException 400: If invalid state transition
        HTTPException 404: If exam not found
    """
    try:
        exam_uuid = UUID(exam_id)
        exam = ExamService.update_exam(db, exam_uuid, exam_update)

        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exam {exam_id} not found",
            )

        logger.info(f"Exam updated: {exam_id}")
        return ExamResponse.model_validate(exam)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam_id format",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating exam: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update exam",
        )


@router.delete(
    "/{exam_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_exam(
    exam_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Delete an exam and all associated data (rubrics, submissions, grades).

    Args:
        exam_id: Exam UUID
        db: Database session

    Raises:
        HTTPException 404: If exam not found
        HTTPException 500: If deletion fails
    """
    try:
        exam_uuid = UUID(exam_id)
        deleted = ExamService.delete_exam(db, exam_uuid)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exam {exam_id} not found",
            )

        logger.info(f"Exam deleted: {exam_id}")
        return None

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam_id format",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting exam: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete exam",
        )


@router.get(
    "/{exam_id}/stats",
    response_model=dict,
)
def get_exam_stats(
    exam_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    """
    Get exam grading statistics.

    Returns summary of grading progress, score distribution, and TA review status.

    Args:
        exam_id: Exam UUID
        db: Database session

    Returns:
        Dictionary with statistics including:
        - total_submissions
        - graded_count
        - pending_review
        - average_score
        - high_confidence_rate
        - plagiarism_flags
    """
    try:
        exam_uuid = UUID(exam_id)
        stats = ExamService.get_exam_stats(db, exam_uuid)

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exam {exam_id} not found or no grades yet",
            )

        logger.info(f"Stats retrieved for exam: {exam_id}")
        return {
            "exam_id": str(exam_id),
            **stats,
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam_id format",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exam stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get exam statistics",
        )
