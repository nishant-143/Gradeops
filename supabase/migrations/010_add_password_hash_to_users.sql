-- Migration 010_add_password_hash_to_users.sql
-- Add password_hash column to users table for secure password storage
-- 
-- Status: IDEMPOTENT (with IF NOT EXISTS)

ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NOT NULL DEFAULT '';

-- Update existing rows with a placeholder (should not have any existing users)
UPDATE public.users SET password_hash = '' WHERE password_hash IS NULL;

-- Remove the default constraint after migration
ALTER TABLE public.users 
ALTER COLUMN password_hash DROP DEFAULT;

-- Add comment
COMMENT ON COLUMN public.users.password_hash IS 'Bcrypt hashed password for authentication';
