"""
API routes package.

Exports all route routers for inclusion in FastAPI app.
"""

from . import auth, exams, rubrics, submissions, answer_regions, grades, export, pipeline

__all__ = ["auth", "exams", "rubrics", "submissions", "answer_regions", "grades", "export", "pipeline"]
