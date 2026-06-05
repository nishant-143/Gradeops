-- Migration 008
-- Adds immutable AI audit fields to grades and introduces pipeline_jobs queue table.

ALTER TABLE grades
    ADD COLUMN IF NOT EXISTS ai_awarded_marks INTEGER,
    ADD COLUMN IF NOT EXISTS ai_criteria_breakdown JSONB DEFAULT '[]'::jsonb NOT NULL,
    ADD COLUMN IF NOT EXISTS ai_justification TEXT DEFAULT '' NOT NULL,
    ADD COLUMN IF NOT EXISTS ai_confidence_score FLOAT DEFAULT 0 NOT NULL,
    ADD COLUMN IF NOT EXISTS ta_note TEXT,
    ADD COLUMN IF NOT EXISTS overridden_by UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS overridden_at TIMESTAMPTZ;

UPDATE grades
SET
    ai_awarded_marks = COALESCE(ai_awarded_marks, awarded_marks),
    ai_criteria_breakdown = CASE
        WHEN ai_criteria_breakdown = '[]'::jsonb THEN COALESCE(criteria_breakdown, '[]'::jsonb)
        ELSE ai_criteria_breakdown
    END,
    ai_justification = CASE
        WHEN ai_justification = '' THEN COALESCE(justification, '')
        ELSE ai_justification
    END,
    ai_confidence_score = CASE
        WHEN ai_confidence_score = 0 THEN COALESCE(confidence_score, 0)
        ELSE ai_confidence_score
    END;

CREATE TABLE IF NOT EXISTS pipeline_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    attempts INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_submission_id ON pipeline_jobs(submission_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_status ON pipeline_jobs(status);

DROP TRIGGER IF EXISTS pipeline_jobs_updated_at_trigger ON pipeline_jobs;
CREATE TRIGGER pipeline_jobs_updated_at_trigger
BEFORE UPDATE ON pipeline_jobs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
