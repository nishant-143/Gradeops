import re

from app.pipeline.state import GradeState


def preprocessor_node(state: GradeState) -> GradeState:
    raw = state.get("raw_ocr_text")
    if not raw:
        state["cleaned_text"] = None
        state["needs_manual_review"] = True
        state["errors"] = state.get("errors", []) + ["missing_ocr_text"]
        return state

    cleaned = raw.strip()
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.replace("\u200b", "")

    state["cleaned_text"] = cleaned
    state["needs_manual_review"] = False
    return state
