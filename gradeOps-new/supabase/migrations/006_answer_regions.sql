-- Migration 006_answer_regions.sql
-- Create answer_regions table for cropped answer images per question
--
-- Relationship:
--   - MANY answer regions per submission (one per question)
--   - Created by OpenCV when processing submission PDF
--   - Contains crop coordinates or URL to pre-cropped image
--
-- Foreign Keys:
--   - submission_id -> submissions.id (ON DELETE CASCADE)
--
-- Lifecycle:
--   1. Created when PDF is processed (image cropped and stored)
--   2. OCR'd by Qwen-VL (extracted_text filled)
--   3. Graded by LangGraph (grade created with FK to this)
--   4. TA reviews in dashboard
--
-- Status: IDEMPOTENT (with IF NOT EXISTS)

CREATE TABLE IF NOT EXISTS answer_regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL,
    image_url TEXT NOT NULL,
    extracted_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_answer_regions_submission_id ON answer_regions(submission_id);
CREATE INDEX IF NOT EXISTS idx_answer_regions_question_id ON answer_regions(submission_id, question_id);

-- Trigger to auto-update updated_at timestamp
DROP TRIGGER IF EXISTS answer_regions_updated_at_trigger ON answer_regions;
CREATE TRIGGER answer_regions_updated_at_trigger
BEFORE UPDATE ON answer_regions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE answer_regions ENABLE ROW LEVEL SECURITY;

-- Table comments
COMMENT ON TABLE answer_regions IS 'Cropped answer images per question per student. Created by OpenCV, OCR''d by Qwen-VL, graded by LangGraph.';
COMMENT ON COLUMN answer_regions.submission_id IS 'FK to submission';
COMMENT ON COLUMN answer_regions.question_id IS 'Question ID/number (e.g., Q1, Q2a)';
COMMENT ON COLUMN answer_regions.image_url IS 'URL to cropped image in Supabase Storage (answer-images bucket)';
COMMENT ON COLUMN answer_regions.extracted_text IS 'OCR''d text from image (filled by Qwen-VL)';
