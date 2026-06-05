-- Migration 003_exams.sql
-- Create exams table for instructor-created exams
--
-- Foreign Keys:
--   - instructor_id -> users.id (ON DELETE CASCADE)
--
-- Constraints:
--   - status: CHECK constraint for valid lifecycle states
--   - title: NOT NULL, human-readable
--
-- Indexes:
--   - PRIMARY KEY on id
--   - UNIQUE on id (automatic)
--   - INDEX on instructor_id (for querying instructor's exams)
--
-- Status: IDEMPOTENT (with IF NOT EXISTS)

CREATE TABLE IF NOT EXISTS exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instructor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'processing', 'ready', 'exported')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_exams_instructor_id ON exams(instructor_id);
CREATE INDEX IF NOT EXISTS idx_exams_status ON exams(status);

-- Trigger to auto-update updated_at timestamp
DROP TRIGGER IF EXISTS exams_updated_at_trigger ON exams;
CREATE TRIGGER exams_updated_at_trigger
BEFORE UPDATE ON exams
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE exams ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Instructors can only see their own exams
DROP POLICY IF EXISTS exams_instructor_isolation ON exams;
CREATE POLICY exams_instructor_isolation ON exams
    USING (instructor_id = auth.uid());

-- Table comments
COMMENT ON TABLE exams IS 'Exams created by instructors. Lifecycle: draft -> processing -> ready -> exported.';
COMMENT ON COLUMN exams.instructor_id IS 'FK to instructor who created this exam';
COMMENT ON COLUMN exams.status IS 'Exam lifecycle state';
