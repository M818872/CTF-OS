# CTF-OS Implementation Status

## Current milestone

**Alpha 0.1 — Integrated investigation foundation**

### Implemented

- FastAPI backend bootstrap with typed configuration and structured logging
- Health endpoint and Docker Compose development stack
- PostgreSQL/Redis service definitions with health checks
- SQLAlchemy investigation and activity persistence models
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
- Next.js investigation dashboard and investigation workspace
- Controlled capability execution from the workspace
- Backend unit/integration tests for manager, workflow, evidence, specialists, Tool Bus and Kali boundaries
- Backend and frontend GitHub Actions validation

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
    -> Report
```

## Alpha completion criteria

The integrated foundation is considered build-complete when:

- Backend and frontend CI checks are green.
- Backend static checks and tests pass.
- Frontend lint, type-check and production build pass.
- Investigation creation and workspace retrieval work through the API.
- Manager planning produces specialist/capability work.
- Tool execution accepts only registered capabilities.
- Execution has bounded timeout and no shell-string interpretation.
- Findings can be represented as evidence and timeline events.
- Reports can be generated from investigation records.
- Docker Compose definitions remain available for local service orchestration.

These criteria are currently satisfied on `feature/bootstrap` by the validated CI baseline.

## Post-alpha hardening / expansion

These are deliberately separate from the build-complete foundation rather than pretending they already exist:

1. Persist evidence as first-class SQL tables with migrations.
2. Add a durable background job queue for long-running tool execution.
3. Add artifact/file ingestion with strict size/type/sandbox controls.
4. Add signed/versioned plugin discovery.
5. Expand specialist-specific workflows across Web, Forensics, Reverse, Stego, Network, OSINT, Mobile, Cloud and AD.
6. Add isolated browser automation through a dedicated worker.
7. Add live event streaming and terminal UI.
8. Add full Docker end-to-end tests including PostgreSQL and Redis.
9. Add authentication, authorization, secrets management and production observability.
10. Review and merge the validated branch into `main` when the project owner is ready.
