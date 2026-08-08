# CTF-OS Implementation Status

## Current milestone

**Alpha 0.2 — Persistent investigation artifacts**

### Implemented

- FastAPI backend bootstrap with typed configuration and structured logging
- Health endpoint and Docker Compose development stack
- PostgreSQL/Redis service definitions with health checks
- SQLAlchemy investigation, activity, evidence, and artifact persistence models
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
    -> Policy-bounded Executor
    -> Evidence + Timeline
    -> Artifacts
    -> Report
```

## Alpha 0.2 completion criteria

- Evidence and artifact records persist with an investigation.
- Evidence and artifact APIs validate ownership through the investigation ID.
- Artifact uploads are bounded to 10 MiB and receive SHA-256 integrity metadata.
- Reports include timeline, evidence, and artifact summaries.
- Backend static checks and tests pass.

A PostgreSQL migration is included at `backend/migrations/001_alpha_persistence.sql`; development startup also creates the declared SQLAlchemy tables automatically.

## Next hardening / expansion

1. Add a durable background job queue for long-running tool execution.
2. Add signed/versioned plugin discovery.
3. Expand specialist-specific workflows across Web, Forensics, Reverse, Stego, Network, OSINT, Mobile, Cloud and AD.
4. Add isolated browser automation through a dedicated worker.
5. Add live event streaming and terminal UI.
6. Add full Docker end-to-end tests including PostgreSQL and Redis.
7. Add authentication, authorization, secrets management and production observability.
