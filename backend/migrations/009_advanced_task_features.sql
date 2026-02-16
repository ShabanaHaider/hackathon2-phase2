-- Migration: Advanced Task Features (Priority, Due Dates, Tags)
-- Adds priority, due_at, is_recurring, recurrence_pattern columns to tasks table
-- Creates tags and task_tags tables for tag functionality

-- Add new columns to tasks table
ALTER TABLE tasks
ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'medium',
ADD COLUMN due_at TIMESTAMPTZ,
ADD COLUMN is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN recurrence_pattern VARCHAR(20);

-- Create indexes for performance
CREATE INDEX ix_tasks_priority ON tasks(priority);
CREATE INDEX ix_tasks_due_at ON tasks(due_at);
CREATE INDEX ix_tasks_user_id_priority ON tasks(user_id, priority);
CREATE INDEX ix_tasks_user_id_due_at ON tasks(user_id, due_at);

-- Create tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_tags_user_id ON tags(user_id);
CREATE UNIQUE INDEX uq_tags_user_id_name ON tags(user_id, LOWER(name));

-- Create task_tags link table
CREATE TABLE task_tags (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX ix_task_tags_tag_id ON task_tags(tag_id);