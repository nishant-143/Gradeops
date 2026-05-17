"""
Submission management routes.

Endpoints:
- POST /submissions - Upload new submission
- GET /submissions - List submissions for exam
- GET /submissions/{submission_id} - Get submission details
- PATCH /submissions/{submission_id}/status - Update submission status
- DELETE /submissions/{submission_id} - Delete submission
"""

import logging
import uuid
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.core.supabase import SupabaseConfig, supabase
from app.core.supabase import get_db_session
from app.schemas import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionResponse,
    SubmissionListResponse,
    ErrorResponse,
)
from app.services import SubmissionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.post(
    "",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_submission(
    exam_id: str = Form(...),
    student_name: str = Form(None),
    roll_number: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Upload a new exam submission (PDF).
    
    Args:
        exam_id: Exam UUID
        student_name: Optional student name
        roll_number: Optional roll number
        file: PDF file upload
        db: Database session
        
    Returns:
        Created SubmissionResponse
    """
    try:
        exam_uuid = UUID(exam_id)
        
        # Validate file is PDF
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # Read file content
        content = await file.read()
        
        # Try uploading to Supabase storage (may fail if bucket doesn't exist)
        public_url = None
        try:
            object_path = f"{exam_id}/{uuid.uuid4()}_{file.filename}"
            supabase.storage.from_(SupabaseConfig.EXAM_PDFS_BUCKET).upload(
                path=object_path,
                file=content,
                file_options={"content-type": "application/pdf"},
            )
            public_url = supabase.storage.from_(SupabaseConfig.EXAM_PDFS_BUCKET).get_public_url(object_path)
            logger.info(f"File uploaded to Supabase storage: {object_path}")
        except Exception as storage_err:
            logger.warning(f"Supabase storage upload failed (bucket may not exist): {storage_err}")
            public_url = f"local://{file.filename}"  # Fallback placeholder
        
        # Create submission record in DB (always succeeds)
        submission_create = SubmissionCreate(
            student_name=student_name or file.filename.replace('.pdf', '').replace('_', ' ').replace('-', ' '),
            roll_number=roll_number,
            pdf_url=public_url,
        )

        db_submission = SubmissionService.create_submission(db, exam_uuid, submission_create)
        
        logger.info(f"Submission uploaded for exam {exam_id}: {db_submission.id}")
        return SubmissionResponse.model_validate(db_submission)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload submission: {str(e)}"
        )


@router.get(
    "",
    response_model=SubmissionListResponse,
)
def list_submissions(
    exam_id: str = Query(...),
    status_filter: str = Query(None),
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    """
    List submissions for an exam.
    
    Args:
        exam_id: Exam UUID
        status_filter: Optional status filter (uploaded, processing, graded)
        db: Database session
        
    Returns:
        List of SubmissionListResponse
    """
    try:
        exam_uuid = UUID(exam_id)
        submissions = SubmissionService.get_submissions_by_exam(
            db, exam_uuid, status_filter
        )
        
        graded_count = sum(1 for sub in submissions if str(sub.status) == "SubmissionStatus.GRADED" or str(sub.status) == "graded")
        return SubmissionListResponse(
            submissions=[SubmissionResponse.model_validate(sub) for sub in submissions],
            total=len(submissions),
            graded_count=graded_count,
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam ID format"
        )
    except Exception as e:
        logger.error(f"Error listing submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list submissions"
        )


@router.get(
    "/{submission_id}",
    response_model=SubmissionResponse,
)
def get_submission(
    submission_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor", "ta")),
):
    """
    Get submission details.
    
    Args:
        submission_id: Submission UUID
        db: Database session
        
    Returns:
        SubmissionResponse
    """
    try:
        submission_uuid = UUID(submission_id)
        submission = SubmissionService.get_submission_by_id(db, submission_uuid)
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission {submission_id} not found"
            )
        
        return SubmissionResponse.model_validate(submission)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get submission"
        )


@router.patch(
    "/{submission_id}/status",
    response_model=SubmissionResponse,
)
def update_submission_status(
    submission_id: str,
    status_update: SubmissionUpdate,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Update submission status.
    
    Args:
        submission_id: Submission UUID
        status_update: SubmissionUpdate with new status
        db: Database session
        
    Returns:
        Updated SubmissionResponse
    """
    try:
        submission_uuid = UUID(submission_id)
        submission = SubmissionService.update_submission_status(
            db, submission_uuid, status_update.status
        )
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission {submission_id} not found"
            )
        
        logger.info(f"Submission {submission_id} status updated to {status_update.status}")
        return SubmissionResponse.model_validate(submission)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating submission status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update submission status"
        )


@router.delete(
    "/{submission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_submission(
    submission_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Delete a submission.
    
    Args:
        submission_id: Submission UUID
        db: Database session
    """
    try:
        submission_uuid = UUID(submission_id)
        deleted = SubmissionService.delete_submission(db, submission_uuid)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission {submission_id} not found"
            )
        
        logger.info(f"Submission deleted: {submission_id}")
        return None
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete submission"
        )
