"""
Export service layer - Business logic for exporting grades.

Handles:
- Grade export data aggregation
- CSV formatting
- Statistics compilation
"""

import logging
import csv
from io import StringIO
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Grade, AnswerRegion, Submission, Exam, Rubric
from app.services.grade_service import GradeService

logger = logging.getLogger(__name__)


class ExportService:
    """Service layer for export operations."""
    
    @staticmethod
    def prepare_export_data(db: Session, exam_id: UUID) -> List[Dict[str, Any]]:
        """
        Prepare grade data for export.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            
        Returns:
            List of dictionaries with export data
        """
        try:
            # Get all approved/finalized grades
            grades = GradeService.get_grades_by_exam(db, exam_id)
            
            export_data = []
            for grade in grades:
                region = db.query(AnswerRegion).filter(
                    AnswerRegion.id == grade.answer_region_id
                ).first()
                
                submission = db.query(Submission).filter(
                    Submission.id == region.submission_id
                ).first()
                
                export_data.append({
                    "student_name": submission.student_name or "N/A",
                    "roll_number": submission.roll_number or "N/A",
                    "question_id": region.question_id,
                    "awarded_marks": grade.awarded_marks or 0,
                    "max_marks": grade.max_marks,
                    "percentage": (
                        grade.awarded_marks / grade.max_marks * 100 
                        if grade.max_marks > 0 else 0
                    ),
                    "justification": grade.justification,
                    "ta_status": grade.ta_status,
                    "plagiarism_flag": "Yes" if grade.plagiarism_flag else "No",
                    "confidence_score": f"{grade.confidence_score:.2%}",
                    "created_at": grade.created_at.isoformat(),
                })
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error preparing export data: {str(e)}")
            raise
    
    @staticmethod
    def generate_csv(
        db: Session,
        exam_id: UUID,
        include_justifications: bool = False,
        include_plagiarism: bool = False,
    ) -> str:
        """
        Generate CSV string from grades.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            
        Returns:
            CSV formatted string
        """
        try:
            export_data = ExportService.prepare_export_data(db, exam_id)
            
            if not export_data:
                logger.warning(f"No grades to export for exam: {exam_id}")
                return ""
            
            # Create CSV
            output = StringIO()
            fieldnames = ["student_name", "roll_number", "question_id", "awarded_marks", "max_marks", "percentage", "ta_status", "confidence_score", "created_at"]
            if include_justifications:
                fieldnames.append("justification")
            if include_plagiarism:
                fieldnames.append("plagiarism_flag")
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            normalized_rows = []
            for row in export_data:
                reduced = dict(row)
                if not include_justifications:
                    reduced.pop("justification", None)
                if not include_plagiarism:
                    reduced.pop("plagiarism_flag", None)
                normalized_rows.append(reduced)
            writer.writerows(normalized_rows)
            
            csv_string = output.getvalue()
            logger.info(f"Generated CSV export for exam: {exam_id}")
            return csv_string
            
        except Exception as e:
            logger.error(f"Error generating CSV: {str(e)}")
            raise
    
    @staticmethod
    def get_exam_summary(db: Session, exam_id: UUID) -> Dict[str, Any]:
        """
        Get summary statistics for exam.
        
        Args:
            db: Database session
            exam_id: Exam UUID
            
        Returns:
            Dictionary with summary data
        """
        try:
            exam = db.query(Exam).filter(Exam.id == exam_id).first()
            rubric = db.query(Rubric).filter(Rubric.exam_id == exam_id).first()
            
            grades = GradeService.get_grades_by_exam(db, exam_id)
            
            if not grades:
                return {
                    "exam_title": exam.title if exam else "Unknown",
                    "total_grades": 0,
                    "average_marks": 0,
                    "average_confidence": 0,
                    "plagiarism_count": 0,
                }
            
            marks = [g.awarded_marks for g in grades if g.awarded_marks is not None]
            confidence_scores = [g.confidence_score for g in grades]
            plagiarism_count = sum(1 for g in grades if g.plagiarism_flag)
            
            return {
                "exam_title": exam.title if exam else "Unknown",
                "exam_id": str(exam_id),
                "max_marks": rubric.max_marks if rubric else 0,
                "total_grades": len(grades),
                "average_marks": sum(marks) / len(marks) if marks else 0,
                "average_percentage": (
                    (sum(marks) / (len(marks) * (rubric.max_marks or 100)) * 100)
                    if marks and rubric else 0
                ),
                "average_confidence": (
                    sum(confidence_scores) / len(confidence_scores) 
                    if confidence_scores else 0
                ),
                "plagiarism_count": plagiarism_count,
                "export_timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error getting exam summary: {str(e)}")
            raise
