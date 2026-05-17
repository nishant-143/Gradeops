"""
Grade management and TA review routes.

Endpoints:
- GET /grades/queue - Get pending grades for review
- GET /grades/{exam_id}/stats - Get grading statistics for exam
- GET /grades/{grade_id} - Get grade details
- PATCH /grades/{grade_id}/approve - Approve a grade
- PATCH /grades/{grade_id}/override - Override a grade
- GET /grades/answer-region/{answer_region_id} - Get grades for answer region
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.core.supabase import get_db_session
from app.schemas import (
    GradeResponse,
    GradeApprove,
    GradeOverride,
    GradeQueueResponse,
    ErrorResponse,
)
from app.services import GradeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/grades", tags=["grades"])


@router.get(
    "/queue",
    response_model=list[GradeQueueResponse],
)
def get_grade_queue(
    exam_id: str = Query(...),
    priority: str = Query(None, description="Filter by priority (high, medium, low)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("ta")),
):
    """
    Get pending grades for TA review.
    
    Returns grades with ta_status='pending' ordered by submission date,
    with high-confidence or plagiarism-flagged items first.
    
    Args:
        exam_id: Exam UUID to filter grades
        priority: Optional priority filter (high, medium, low)
        limit: Number of grades to return
        offset: Pagination offset
        db: Database session
        
    Returns:
        List of GradeQueueResponse with enriched data
    """
    try:
        from app.models import AnswerRegion, Submission
        
        exam_uuid = UUID(exam_id)
        grades = GradeService.get_pending_grades(
            db, exam_uuid, priority=priority, limit=limit, offset=offset
        )
        
        queue_items = []
        for grade in grades:
            # Fetch related answer region
            answer_region = db.query(AnswerRegion).filter(
                AnswerRegion.id == grade.answer_region_id
            ).first()
            
            # Fetch related submission
            submission = None
            if answer_region:
                submission = db.query(Submission).filter(
                    Submission.id == answer_region.submission_id
                ).first()
            
            queue_items.append(GradeQueueResponse(
                grade=GradeResponse.model_validate(grade),
                student_name=submission.student_name if submission else None,
                question_id=answer_region.question_id if answer_region else "",
                image_url=answer_region.image_url if answer_region else "",
                extracted_text=answer_region.extracted_text if answer_region else None
            ))
        
        return queue_items
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam ID format"
        )
    except Exception as e:
        logger.error(f"Error getting grade queue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get grade queue"
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam ID format"
        )
    except Exception as e:
        logger.error(f"Error getting grade queue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get grade queue"
        )


@router.get(
    "/{exam_id}/stats",
    response_model=dict,
)
def get_exam_grading_stats(
    exam_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("ta", "instructor")),
):
    """
    Get grading statistics for an exam.
    
    Returns: total grades, pending review, approved, overridden,
    average score, high confidence rate, plagiarism flags.
    
    Args:
        exam_id: Exam UUID
        db: Database session
        
    Returns:
        Dictionary with statistics
    """
    try:
        exam_uuid = UUID(exam_id)
        stats = GradeService.get_exam_stats(db, exam_uuid)
        
        return {
            "exam_id": str(exam_id),
            "total_grades": stats.get("total_grades", 0),
            "pending_review": stats.get("pending_review", 0),
            "approved": stats.get("approved", 0),
            "overridden": stats.get("overridden", 0),
            "average_score": stats.get("average_score", 0.0),
            "high_confidence_rate": stats.get("high_confidence_rate", 0.0),
            "plagiarism_flags": stats.get("plagiarism_flags", 0),
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam ID format"
        )
    except Exception as e:
        logger.error(f"Error getting exam stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get exam statistics"
        )


@router.get(
    "/{grade_id}",
    response_model=GradeResponse,
)
def get_grade(
    grade_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("ta", "instructor")),
):
    """
    Get grade details.
    
    Args:
        grade_id: Grade UUID
        db: Database session
        
    Returns:
        GradeResponse with full grade details
    """
    try:
        grade_uuid = UUID(grade_id)
        grade = GradeService.get_grade_by_id(db, grade_uuid)
        
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grade {grade_id} not found"
            )
        
        return GradeResponse.model_validate(grade)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid grade ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get grade"
        )


@router.patch(
    "/{grade_id}/approve",
    response_model=GradeResponse,
)
def approve_grade(
    grade_id: str,
    approval: GradeApprove,
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
    _user=Depends(require_role("ta")),
):
    """
    Approve a grade by TA.
    
    Updates ta_status to 'approved' and optionally stores TA feedback.
    
    Args:
        grade_id: Grade UUID
        approval: GradeApprove with optional feedback
        db: Database session
        
    Returns:
        Updated GradeResponse
    """
    try:
        grade_uuid = UUID(grade_id)
        grade = GradeService.approve_grade(db, grade_uuid, approval.feedback, current_user.id)
        
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grade {grade_id} not found"
            )
        
        logger.info(f"Grade approved: {grade_id}")
        return GradeResponse.model_validate(grade)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid grade ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve grade"
        )


@router.patch(
    "/{grade_id}/override",
    response_model=GradeResponse,
)
def override_grade(
    grade_id: str,
    override: GradeOverride,
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
    _user=Depends(require_role("ta")),
):
    """
    Override a grade with TA-adjusted marks.
    
    Updates ta_status to 'overridden' and stores new criteria breakdown
    with TA justification for each criterion.
    
    Args:
        grade_id: Grade UUID
        override: GradeOverride with new criteria breakdown and reason
        db: Database session
        
    Returns:
        Updated GradeResponse with new marks
    """
    try:
        grade_uuid = UUID(grade_id)
        grade = GradeService.override_grade(
            db,
            grade_uuid,
            override.criteria_breakdown,
            override.reason,
            current_user.id,
        )
        
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grade {grade_id} not found"
            )
        
        logger.info(f"Grade overridden: {grade_id}")
        return GradeResponse.model_validate(grade)
        
    except ValueError as e:
        logger.warning(f"Grade override validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error overriding grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to override grade"
        )


@router.get(
    "/answer-region/{answer_region_id}",
    response_model=list[GradeResponse],
)
def get_grades_for_answer_region(
    answer_region_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("ta", "instructor")),
):
    """
    Get all grades for an answer region.
    
    Args:
        answer_region_id: Answer region UUID
        db: Database session
        
    Returns:
        List of GradeResponse
    """
    try:
        region_uuid = UUID(answer_region_id)
        grades = GradeService.get_grades_for_answer_region(db, region_uuid)
        
        return [
            GradeResponse.model_validate(grade)
            for grade in grades
        ]
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer region ID format"
        )
    except Exception as e:
        logger.error(f"Error getting grades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get grades"
        )
