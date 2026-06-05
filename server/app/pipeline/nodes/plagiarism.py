from typing import List

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings
from app.pipeline.state import GradeState

_embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)


def plagiarism_node(state: GradeState) -> GradeState:
    if state.get("needs_manual_review"):
        state["embedding"] = []
        state["plagiarism_flag"] = False
        state["similar_submission_ids"] = []
        return state

    embedding = _embedding_model.encode(state.get("cleaned_text", "")).tolist()
    similar_submission_ids: List[str] = []

    for stored in state.get("all_embeddings", []):
        vector = stored.get("vector")
        region_id = stored.get("answer_region_id")
        if not vector or not region_id:
            continue
        sim = cosine_similarity([embedding], [vector])[0][0]
        if sim >= settings.PLAGIARISM_THRESHOLD:
            similar_submission_ids.append(region_id)

    state["embedding"] = embedding
    state["similar_submission_ids"] = similar_submission_ids
    state["plagiarism_flag"] = len(similar_submission_ids) > 0
    return state
