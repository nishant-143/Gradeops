-- Migration 001_pgvector.sql
-- Enable pgvector extension for semantic search (plagiarism detection)
-- 
-- pgvector is a PostgreSQL extension that allows storing and searching
-- high-dimensional vectors. We use it for plagiarism detection by
-- storing sentence-transformer embeddings and computing cosine similarity.
--
-- Status: IDEMPOTENT (safe to run multiple times)

CREATE EXTENSION IF NOT EXISTS "vector";

-- Verify installation
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'vector'
    ) THEN
        RAISE EXCEPTION 'pgvector extension failed to load';
    END IF;
END $$;

-- Log successful completion
COMMENT ON EXTENSION vector IS 'PostgreSQL extension for storing and searching vector embeddings (pgvector)';
