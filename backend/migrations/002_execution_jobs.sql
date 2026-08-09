-- CTF-OS durable execution queue
-- Apply after 001_alpha_persistence.sql.

CREATE TABLE IF NOT EXISTS execution_jobs (
    id UUID PRIMARY KEY,
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    kind VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'queued',
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB,
    error TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    available_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    locked_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_execution_jobs_status ON execution_jobs(status);
CREATE INDEX IF NOT EXISTS ix_execution_jobs_available_at ON execution_jobs(available_at);
CREATE INDEX IF NOT EXISTS ix_execution_jobs_investigation_id ON execution_jobs(investigation_id);
