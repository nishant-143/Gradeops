-- Migration 007_grades.sql
-- Create grades table for AI-generated grades and TA feedback
--
-- Relationship:
--   - ONE-TO-ONE with answer_regions (unique constraint)
--   - Created by LangGraph pipeline
--   - Modified by TA approvals/overrides
--
-- Foreign Keys:
--   - answer_region_id -> answer_regions.id (ON DELETE CASCADE, UNIQUE)
--
-- Key Features:
--   - JSONB criteria_breakdown for per-criterion scores
--   - pgvector embedding for plagiarism detection (cosine similarity)
--   - ta_status tracking TA review state
--   - confidence_score from LangGraph
--   - plagiarism_flag + similar_submission_ids
--
-- JSONB Schemas:
--
-- criteria_breakdown:
-- [
--     {"id": "c1", "awarded": 3, "justification": "Used Newton's second law correctly"},
--     {"id": "c2", "awarded": 3, "justification": "Correct values substituted"},
--     {"id": "c3", "awarded": 1, "justification": "Arithmetic error in final step"}
-- ]
--
-- similar_submission_ids:
-- ["uuid1", "uuid2", "uuid3"]
--
-- Status: IDEMPOTENT (with IF NOT EXISTS)

CREATE TABLE IF NOT EXISTS grades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_region_id UUID NOT NULL UNIQUE REFERENCES answer_regions(id) ON DELETE CASCADE,
    awarded_marks INTEGER,
    max_marks INTEGER NOT NULL,
    criteria_breakdown JSONB NOT NULL,
    justification VARCHAR(2000) NOT NULL,
    confidence_score FLOAT NOT NULL,
    plagiarism_flag BOOLEAN DEFAULT FALSE,
    similar_submission_ids JSONB DEFAULT '[]'::jsonb,
    ta_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (ta_status IN ('pending', 'approved', 'overridden')),
    embedding vector(384),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_grades_answer_region_id ON grades(answer_region_id);
CREATE INDEX IF NOT EXISTS idx_grades_ta_status ON grades(ta_status);
CREATE INDEX IF NOT EXISTS idx_grades_plagiarism_flag ON grades(plagiarism_flag);
CREATE INDEX IF NOT EXISTS idx_grades_confidence ON grades(confidence_score);

-- Vector similarity search index for plagiarism detection
-- Using IVFFlat algorithm for fast approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS idx_grades_embedding ON grades
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- JSONB index for criteria searching
CREATE INDEX IF NOT EXISTS idx_grades_criteria_breakdown ON grades USING GIN (criteria_breakdown);

-- Trigger to auto-update updated_at timestamp
DROP TRIGGER IF EXISTS grades_updated_at_trigger ON grades;
CREATE TRIGGER grades_updated_at_trigger
BEFORE UPDATE ON grades
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE grades ENABLE ROW LEVEL SECURITY;

-- Table comments
COMMENT ON TABLE grades IS 'AI-generated grades with TA review status. One grade per answer region. Embeddings for plagiarism detection.';
COMMENT ON COLUMN grades.answer_region_id IS 'FK to answer_region (unique—one grade per answer)';
COMMENT ON COLUMN grades.awarded_marks IS 'Marks awarded by AI (nullable if not yet graded)';
COMMENT ON COLUMN grades.criteria_breakdown IS 'JSONB array of criterion results with justifications';
COMMENT ON COLUMN grades.justification IS 'Human-readable explanation of grade (for TA dashboard)';
COMMENT ON COLUMN grades.confidence_score IS 'AI confidence (0-1)';
COMMENT ON COLUMN grades.plagiarism_flag IS 'Whether plagiarism was detected';
COMMENT ON COLUMN grades.similar_submission_ids IS 'JSONB array of similar submission IDs';
COMMENT ON COLUMN grades.ta_status IS 'TA decision: pending, approved, or overridden';
COMMENT ON COLUMN grades.embedding IS '384-dim vector from sentence-transformers (pgvector)';
COMMENT ON INDEX idx_grades_embedding IS 'IVFFlat index for cosine similarity plagiarism search';

-- Grant permissions (adjust to your needs)
-- The public role can SELECT but not INSERT/UPDATE/DELETE (managed by application)
GRANT SELECT ON grades TO authenticated;
GRANT INSERT, UPDATE, DELETE ON grades TO authenticated;
