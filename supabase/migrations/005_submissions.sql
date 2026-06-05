-- Migration 005_submissions.sql
-- Create submissions table for student-submitted exam PDFs
--
-- Relationship:
--   - MANY submissions per exam
--   - One submission = one student's PDF for one exam
--
-- Foreign Keys:
--   - exam_id -> exams.id (ON DELETE CASCADE)
--
-- Lifecycle:
--   - uploaded: PDF received, not yet processed
--   - processing: Pages being split and cropped
--   - graded: All answer regions graded by LangGraph
--
-- Status: IDEMPOTENT (with IF NOT EXISTS)

CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_name TEXT,
    roll_number TEXT,
    pdf_url TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'graded')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_submissions_exam_id ON submissions(exam_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_student_roll ON submissions(exam_id, roll_number);

-- Trigger to auto-update updated_at timestamp
DROP TRIGGER IF EXISTS submissions_updated_at_trigger ON submissions;
CREATE TRIGGER submissions_updated_at_trigger
BEFORE UPDATE ON submissions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;

-- Table comments
COMMENT ON TABLE submissions IS 'Student-submitted exam PDFs. Lifecycle: uploaded -> processing -> graded.';
COMMENT ON COLUMN submissions.exam_id IS 'FK to exam';
COMMENT ON COLUMN submissions.pdf_url IS 'URL to PDF in Supabase Storage (exam-pdfs bucket)';
COMMENT ON COLUMN submissions.status IS 'Processing stage of submission';
COMMENT ON COLUMN submissions.student_name IS 'Student name (optional, for batch processing)';
COMMENT ON COLUMN submissions.roll_number IS 'Student roll/ID (optional)';
