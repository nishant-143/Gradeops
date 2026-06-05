"""
Export routes for grades and results.

Endpoints:
- GET /export/{exam_id}/csv - Export grades as CSV
- GET /export/{exam_id}/summary - Get summary report
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.core.dependencies import require_role
from app.core.supabase import get_db_session
from app.services import ExportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get(
    "/{exam_id}/csv",
    responses={
        200: {"content": {"text/csv": {}}},
        404: {"description": "Exam not found"},
        500: {"description": "Export failed"},
    },
)
def export_grades_csv(
    exam_id: str,
    include_justifications: bool = False,
    include_plagiarism: bool = False,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Export exam grades as CSV.
    
    Includes student info, marks by criterion, total marks, TA status.
    Optional: justifications and plagiarism flags.
    
    Args:
        exam_id: Exam UUID
        include_justifications: Include AI justifications in export
        include_plagiarism: Include plagiarism detection results
        db: Database session
        
    Returns:
        CSV file as download
    """
    try:
        exam_uuid = UUID(exam_id)
        
        csv_content = ExportService.generate_csv(
            db,
            exam_uuid,
            include_justifications=include_justifications,
            include_plagiarism=include_plagiarism
        )
        
        if not csv_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No grades found for exam {exam_id}"
            )
        
        logger.info(f"CSV export generated for exam {exam_id}")
        
        # Return as streaming response
        output = io.StringIO(csv_content)
        
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=grades_{exam_id}.csv"
            }
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export grades as CSV"
        )


@router.get(
    "/{exam_id}/summary",
    response_model=dict,
)
def get_export_summary(
    exam_id: str,
    db: Session = Depends(get_db_session),
    _user=Depends(require_role("instructor")),
):
    """
    Get comprehensive summary report for exam.
    
    Includes:
    - Overall statistics (total grades, average, distribution)
    - TA review status
    - Plagiarism detection summary
    - Grade distribution by criterion
    - High/low performers
    
    Args:
        exam_id: Exam UUID
        db: Database session
        
    Returns:
        Summary report dictionary
    """
    try:
        exam_uuid = UUID(exam_id)
        
        summary = ExportService.get_exam_summary(db, exam_uuid)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for exam {exam_id}"
            )
        
        logger.info(f"Summary report generated for exam {exam_id}")
        
        return {
            "exam_id": str(exam_id),
            **summary
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate summary report"
        )
