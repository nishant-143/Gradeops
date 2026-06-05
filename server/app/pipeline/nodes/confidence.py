from app.core.config import settings
from app.pipeline.state import GradeState


def confidence_node(state: GradeState) -> GradeState:
    min_conf = 0.7
    max_reeval = 1
    state["needs_reeval"] = (
        not state.get("needs_manual_review", False)
        and state.get("confidence_score", 0.0) < min_conf
        and state.get("reeval_count", 0) < max_reeval
    )
    # Hard guard against impossible grades
    if state.get("awarded_marks", 0) > state.get("max_marks", 0):
        state["errors"] = state.get("errors", []) + ["awarded_exceeds_max"]
        state["awarded_marks"] = state.get("max_marks", 0)
    return state
