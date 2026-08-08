# CTF-OS Implementation Status

## Current milestone

**Alpha 0.1 — Integrated foundation**

### Implemented

- FastAPI backend bootstrap
- Typed environment configuration
- Structured JSON logging
- Health endpoint
- Docker Compose with backend, frontend, PostgreSQL, and Redis
- PostgreSQL and Redis health checks
- SQLAlchemy async database layer
- Minimal SDK contracts
- Capability registry
- Deterministic investigation manager/agent
- Policy-bounded local executor
- Sequential workflow engine
- Crypto specialist and crypto workflow
- Evidence store and investigation timeline primitives
- Deterministic Markdown report generation
- Investigation API
- Backend unit tests
- Frontend Next.js dashboard shell
- Backend and frontend GitHub Actions workflows

## Runtime contract

The agent plans against registered capabilities. It does not invent tool names or bypass the execution policy. External execution is isolated behind an executor interface so policy, planning, and execution remain independently testable.

```text
Investigation
    -> Manager / Agent
    -> Workflow
    -> Capability Registry
    -> Executor / Specialist
    -> Evidence + Timeline
    -> Report
```

## Remaining Alpha work

1. Add persistent evidence/timeline tables and migrations.
2. Connect investigation execution to the workflow engine through an API job boundary.
3. Add artifact/file ingestion with size and type limits.
4. Add plugin discovery and version validation.
5. Add more Crypto capabilities (XOR, Caesar, common encodings and candidate ranking).
6. Add Web, Forensics, Reverse, Stego, Network, OSINT, Mobile, Cloud, and AD specialist contracts.
7. Add browser execution through an isolated Playwright worker.
8. Add terminal UI and live event streaming.
9. Add end-to-end Docker validation and frontend/backend integration tests.
10. Run the complete CI suite and review the branch before merging to `main`.

## Definition of done for Alpha 0.1

- Backend and frontend containers build.
- `/api/health` returns HTTP 200.
- Backend and frontend tests/builds pass.
- Static checks pass.
- Local PostgreSQL and Redis services start through Compose.
- Manager can create and plan an investigation against registered capabilities.
- Execution is policy bounded and test covered.
- Crypto findings become evidence and timeline events.
- Reports can be generated from recorded evidence.
- All Alpha CI checks are green.
