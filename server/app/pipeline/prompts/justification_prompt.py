from typing import Any, Dict, List


def build_justification_prompt(criteria_breakdown: List[Dict[str, Any]], total_awarded: int, max_marks: int) -> str:
    criteria_text = "\n".join(
        f"- {c.get('id')}: awarded {c.get('awarded')} | {c.get('justification')}"
        for c in criteria_breakdown
    )
    return f"""
Write a concise grading justification for a TA review dashboard.
Do not invent marks or criterion IDs. Keep it under 120 words.

Total score: {total_awarded}/{max_marks}
Criterion decisions:
{criteria_text}

Return ONLY valid JSON:
{{
  "justification": "single concise paragraph"
}}
"""
