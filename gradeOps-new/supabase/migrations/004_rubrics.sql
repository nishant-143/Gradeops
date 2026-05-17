-- Migration 004_rubrics.sql
-- Create rubrics table for exam grading criteria
--
-- Relationship:
--   - ONE-TO-ONE with exams (unique constraint on exam_id)
--   - criteria stored as JSONB for flexibility
--
-- Foreign Keys:
--   - exam_id -> exams.id (ON DELETE CASCADE, UNIQUE)
--
-- JSONB Schema (example):
-- {
--     "criteria": [
--         {"id": "c1", "description": "Correct formula used", "marks": 3},
--         {"id": "c2", "description": "Correct substitution", "marks": 3},
--         {"id": "c3", "description": "Final answer correct", "marks": 4}
--     ],
--     "max_marks": 10
-- }
--
-- Status: IDEMPOTENT (with IF NOT EXISTS)

CREATE TABLE IF NOT EXISTS rubrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL UNIQUE REFERENCES exams(id) ON DELETE CASCADE,
    criteria JSONB NOT NULL,
    max_marks INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_rubrics_exam_id ON rubrics(exam_id);

-- JSONB index for efficient criteria searching
CREATE INDEX IF NOT EXISTS idx_rubrics_criteria ON rubrics USING GIN (criteria);

-- Trigger to auto-update updated_at timestamp
DROP TRIGGER IF EXISTS rubrics_updated_at_trigger ON rubrics;
CREATE TRIGGER rubrics_updated_at_trigger
BEFORE UPDATE ON rubrics
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE rubrics ENABLE ROW LEVEL SECURITY;

-- Table comments
COMMENT ON TABLE rubrics IS 'Grading criteria for exams. One rubric per exam. Criteria stored as JSONB.';
COMMENT ON COLUMN rubrics.exam_id IS 'FK to exam (unique—one rubric per exam)';
COMMENT ON COLUMN rubrics.criteria IS 'JSONB array of criterion objects with id, description, marks';
COMMENT ON COLUMN rubrics.max_marks IS 'Total possible marks for exam';
