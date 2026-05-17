-- Migration 002_users.sql
-- Create users table for instructors and TAs
--
-- Constraints:
--   - email: UNIQUE, indexed for fast lookups
--   - role: CHECK constraint to only allow 'instructor' or 'ta'
--   - Timestamps auto-managed (created_at, updated_at)
--
-- Indexes:
--   - PRIMARY KEY on id (automatic)
--   - UNIQUE on email
--   - INDEX on id (for foreign keys)
--
-- Status: IDEMPOTENT (with IF NOT EXISTS)

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('instructor', 'ta')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Enable RLS (Row Level Security) for multi-tenancy
-- Each user should only see their own data by default
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS users_updated_at_trigger ON users;
CREATE TRIGGER users_updated_at_trigger
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Table comment for documentation
COMMENT ON TABLE users IS 'Stores instructors and TAs. Multi-tenant isolation via instructor_id foreign keys.';
COMMENT ON COLUMN users.id IS 'UUID primary key, auto-generated';
COMMENT ON COLUMN users.email IS 'User email, must be unique';
COMMENT ON COLUMN users.role IS 'Either instructor or ta';
