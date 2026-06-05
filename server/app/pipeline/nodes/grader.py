from app.pipeline.prompts.grading_prompt import build_grading_prompt
from app.pipeline.state import GradeState
from app.services.llm_service import llm_service


def grader_node(state: GradeState) -> GradeState:
    if state.get("needs_manual_review"):
        state["criteria_breakdown"] = []
        state["awarded_marks"] = 0
        state["max_marks"] = state["rubric"].get("max_marks", 0)
        state["confidence_score"] = 0.0
        return state

    strict_mode = bool(state.get("needs_reeval"))
    prompt = build_grading_prompt(
        answer=state["cleaned_text"] or "",
        rubric=state["rubric"],
        strict=strict_mode,
    )
    result = llm_service.invoke_json(prompt, trace={"answer_region_id": state["answer_region_id"], "node": "grader"})
    state["criteria_breakdown"] = result.get("criteria", [])
    state["awarded_marks"] = int(result.get("total_awarded", 0))
    state["max_marks"] = int(result.get("max_marks", state["rubric"].get("max_marks", 0)))
    state["confidence_score"] = float(result.get("confidence", 0.0))
    if strict_mode:
        state["reeval_count"] = state.get("reeval_count", 0) + 1
        state["needs_reeval"] = False
    return state
