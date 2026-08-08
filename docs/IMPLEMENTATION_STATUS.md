# CTF-OS Implementation Status

## Current milestone

**Alpha 0.1 — Foundation**

This branch contains the first executable foundation of CTF-OS.

### Implemented

- FastAPI backend bootstrap
- Typed environment configuration
- Structured JSON logging
- Health endpoint
- Docker Compose development services
- PostgreSQL and Redis health checks
- Minimal SDK contracts
- Capability registry
- Deterministic investigation agent
- Backend unit tests
- GitHub Actions quality workflow

## Agent contract

The investigation agent is intentionally small. It does not execute operating-system commands and it does not invent tool names. It plans against registered capabilities and delegates execution to later runtime components.

```text
Investigation
    -> Manager / Agent
    -> Workflow
    -> Capability Registry
    -> Executor
    -> Evidence
```

This separation keeps reasoning, policy, and execution independently testable.

## Build order

1. Foundation
2. Execution runtime
3. Plugin SDK
4. Workflow engine
5. First specialist (Crypto)
6. Investigation API
7. Timeline and evidence
8. Report generation
9. Additional specialists

## Definition of done for Alpha 0.1

- Backend container builds.
- `/api/health` returns HTTP 200.
- Backend tests pass.
- Static checks pass.
- Local PostgreSQL and Redis services start through Compose.
- Manager can create and plan an investigation against registered capabilities.
