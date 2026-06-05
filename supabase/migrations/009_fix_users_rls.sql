-- Migration 009_fix_users_rls.sql
-- Fix: Disable RLS on users table (was enabled without policies, blocking all access)
-- 
-- Issue: RLS was enabled in 002_users.sql but no policies were defined.
-- This blocked ALL database access to the users table.
-- 
-- Solution: Disable RLS since the backend uses the service role key which
-- has full server-side access and handles authentication itself.
--
-- Status: IDEMPOTENT (safe to run multiple times)

-- Disable RLS on users table to restore database access
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Verify the change
-- SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'users';
