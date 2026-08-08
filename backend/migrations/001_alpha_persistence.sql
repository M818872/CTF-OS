-- CTF-OS Alpha persistence migration
-- Apply after the existing investigations and investigation_activities tables.

CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY,
    investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
    kind VARCHAR(50) NOT NULL DEFAULT 'observation',
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(100) NOT NULL DEFAULT 'agent',
    confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_evidence_investigation_id ON evidence(investigation_id);

CREATE TABLE IF NOT EXISTS artifacts (
    id UUID PRIMARY KEY,
    investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(120) NOT NULL DEFAULT 'application/octet-stream',
    size_bytes INTEGER NOT NULL,
    sha256 VARCHAR(64) NOT NULL,
    storage_key VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_artifacts_investigation_id ON artifacts(investigation_id);
CREATE INDEX IF NOT EXISTS ix_artifacts_sha256 ON artifacts(sha256);
