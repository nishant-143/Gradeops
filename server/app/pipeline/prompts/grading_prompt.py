from typing import Any, Dict


def build_grading_prompt(answer: str, rubric: Dict[str, Any], strict: bool = False) -> str:
    criteria = rubric.get("criteria", [])
    criteria_text = "\n".join(
        f"CRITERION ID: '{c['id']}'\nDESCRIPTION: {c['description']}\nMAX MARKS: {c['marks']}\n---" for c in criteria
    )
    mode_instructions = (
        "STRICT MODE ENABLED: Be highly critical. Penalize any unsupported assumptions, vague statements, or missing key terms heavily. Do not give the benefit of the doubt."
        if strict
        else "Be fair, objective, and strictly aligned with the rubric."
    )
    return f"""
You are an expert, impartial academic examiner tasked with grading a student's answer based on a specific rubric. {mode_instructions}

IMPORTANT INSTRUCTIONS:
1. READ THE RUBRIC CAREFULLY: Evaluate the answer against EACH criterion separately.
2. OCR ERRORS: The student answer is extracted via OCR. It may contain typos or formatting errors. Focus on the semantic meaning, but DO NOT hallucinate missing concepts.
3. NO BENEFIT OF THE DOUBT: If a concept is missing, factually incorrect, or irrelevant, award 0 marks for that specific part.
4. CHAIN OF THOUGHT: For each criterion, write a detailed 'justification' FIRST, explaining exactly what the student did right and wrong, and ONLY THEN decide the 'awarded' marks.
5. NO HALF MARKS: Use integers for awarded marks. Awarded marks MUST NOT exceed the max marks for that criterion.

RUBRIC CRITERIA:
{criteria_text}
Total max marks: {rubric.get("max_marks", 0)}

STUDENT ANSWER:
\"\"\"
{answer}
\"\"\"

Return ONLY valid JSON with this exact shape and order:
{{
  "criteria": [
    {{
      "id": "must exactly match the CRITERION ID",
      "justification": "Detailed reasoning explaining why marks are given or deducted based on the text.",
      "awarded": 0
    }}
  ],
  "total_awarded": 0,
  "max_marks": {rubric.get("max_marks", 0)},
  "confidence": 0.0
}}
"""
