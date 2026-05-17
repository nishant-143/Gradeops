from typing import Any, Dict, List, Optional, TypedDict


class CriterionResult(TypedDict):
    id: str
    awarded: int
    justification: str


class GradeState(TypedDict):
    # Inputs
    answer_region_id: str
    question_id: str
    raw_ocr_text: Optional[str]
    rubric: Dict[str, Any]
    all_embeddings: List[Dict[str, Any]]

    # Pipeline outputs
    cleaned_text: Optional[str]
    criteria_breakdown: List[CriterionResult]
    awarded_marks: int
    max_marks: int
    justification: str
    confidence_score: float
    needs_reeval: bool
    reeval_count: int
    plagiarism_flag: bool
    similar_submission_ids: List[str]
    embedding: List[float]
    needs_manual_review: bool
    errors: List[str]
