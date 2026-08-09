# CTF-OS Implementation Status

## Current milestone

**Alpha 0.3 — Durable execution runtime**

### Implemented

- FastAPI backend bootstrap with typed configuration and structured logging
- Health endpoint and Docker Compose development stack
- PostgreSQL/Redis service definitions with health checks
- SQLAlchemy investigation, activity, evidence, artifact, and execution-job persistence models
- Minimal typed SDK contracts
- Global capability registry and specialist catalog
- Deterministic Global Manager / autonomous specialist routing
- Sequential workflow planning engine
- Shared Tool Bus contracts
- Kali tool profiles and runtime discovery
- Policy-bounded local/Kali execution boundary with timeout and allow-list controls
- Deterministic built-in CTF analysis capabilities
- Crypto specialist workflow and specialist capability catalog
- Structured evidence and shared-memory primitives
- Investigation timeline/activity recording
- Deterministic Markdown report generation
- Investigation create/list/workspace/plan/execute/report APIs
- Evidence create/list APIs with confidence and source metadata
- Bounded artifact upload with filename sanitization, 10 MiB limit, SHA-256 hashing, and local storage key
- Next.js investigation dashboard and investigation workspace
- Controlled capability execution from the workspace
- Durable PostgreSQL-backed execution queue with leases, retries, and persisted results
- Dedicated execution worker service in Docker Compose
- Queued terminal execution and job-status APIs
- Backend unit/integration tests and GitHub Actions validation

## Runtime contract

The Global Manager plans against registered capabilities. Specialists select capabilities from the shared catalog; they do not invent executable names. Tool execution is isolated behind an explicit boundary and is policy constrained. Arbitrary shell interpretation is not part of the agent API.

```text
Challenge
    -> Investigation
    -> Global Manager
    -> Specialist Router
    -> Workflow
    -> Capability Registry
    -> Shared Tool Bus
    -> Durable Job Queue
    -> Dedicated Worker
    -> Policy-bounded Executor
    -> Evidence + Timeline
    -> Artifacts
    -> Report
```

## Alpha 0.3 completion criteria

- Long-running terminal execution can be queued without blocking the API request.
- Jobs persist in PostgreSQL and survive API/worker restarts.
- Workers claim jobs with row-level locking and recover stale leases.
- Failed jobs retry with bounded exponential backoff and eventually enter `failed` state.
- Job results, errors, attempts, and lifecycle timestamps are persisted.
- Backend static checks and tests pass.

A PostgreSQL migration is included at `backend/migrations/002_execution_jobs.sql`; development startup and the worker also create declared SQLAlchemy tables automatically.

## Next hardening / expansion

1. Add signed/versioned plugin discovery.
2. Expand specialist-specific workflows across Web, Forensics, Reverse, Stego, Network, OSINT, Mobile, Cloud and AD.
3. Add isolated browser automation through a dedicated worker.
4. Add live event streaming and terminal UI.
5. Add full Docker end-to-end tests including PostgreSQL and Redis.
6. Add authentication, authorization, secrets management and production observability.
