from app.pipeline.prompts.justification_prompt import build_justification_prompt
from app.pipeline.state import GradeState
from app.services.llm_service import llm_service


def justifier_node(state: GradeState) -> GradeState:
    if state.get("needs_manual_review"):
        state["justification"] = "OCR text unavailable; sent for manual TA review."
        return state

    prompt = build_justification_prompt(
        criteria_breakdown=state.get("criteria_breakdown", []),
        total_awarded=state.get("awarded_marks", 0),
        max_marks=state.get("max_marks", 0),
    )
    result = llm_service.invoke_json(prompt, trace={"answer_region_id": state["answer_region_id"], "node": "justifier"})
    state["justification"] = result.get("justification", "").strip() or "No justification generated."
    return state
