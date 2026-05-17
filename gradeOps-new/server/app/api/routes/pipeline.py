import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.dependencies import require_role
from app.core.supabase import get_db_session
from app.models import Submission, Exam
from app.services import PipelineService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post(
    "/process/{submission_id}",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
)
def process_submission_pipeline(
    submission_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    try:
        submission_uuid = UUID(submission_id)
        submission = db.query(Submission).filter(
            Submission.id == submission_uuid
        ).first()
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission {submission_id} not found"
            )
        job = PipelineService.enqueue_job(db, submission_uuid)
        return {
            "job_id": str(job.id),
            "submission_id": str(submission_uuid),
            "status": job.status,
            "status_url": f"/api/pipeline/status/{job.id}"
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission ID format"
        )
    except Exception as e:
        logger.error(f"Error starting pipeline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start pipeline processing"
        )


@router.get(
    "/status/{pipeline_id}",
    response_model=dict,
)
def get_pipeline_status(
    pipeline_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    try:
        job_uuid = UUID(pipeline_id)
        job = PipelineService.get_job(db, job_uuid)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline job {pipeline_id} not found"
            )
        return {
            "id": str(job.id),
            "submission_id": str(job.submission_id),
            "status": job.status,
            "progress": job.progress,
            "attempts": job.attempts,
            "error": job.error,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pipeline ID format",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pipeline status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pipeline status"
        )


@router.get(
    "/history/{exam_id}",
    response_model=dict,
)
def get_pipeline_history(
    exam_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    try:
        exam_uuid = UUID(exam_id)
        exam = db.query(Exam).filter(Exam.id == exam_uuid).first()
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exam {exam_id} not found"
            )
        jobs = PipelineService.get_jobs_for_exam(db, exam_uuid, limit, offset)
        return {
            "exam_id": str(exam_uuid),
            "history": [
                {
                    "job_id": str(job.id),
                    "submission_id": str(job.submission_id),
                    "status": job.status,
                    "progress": job.progress,
                    "attempts": job.attempts,
                    "error": job.error,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                }
                for job in jobs
            ],
            "total": len(jobs),
            "limit": limit,
            "offset": offset
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pipeline history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pipeline history"
        )
