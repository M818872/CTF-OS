# CTF-OS

AI-native Capture The Flag investigation platform.

## Current Alpha

CTF-OS is being developed as a modular monolith with a strict separation between reasoning, workflow orchestration, capability registration, execution, and evidence.

```text
Challenge -> Investigation -> Manager -> Workflow -> Capability -> Executor -> Evidence -> Timeline -> Report
```

## Repository

- `backend/` — FastAPI application and runtime
- `sdk/` — public plugin/capability contracts
- `frontend/` — Next.js investigation console
- `docs/` — architecture and implementation status

## Development

Backend:

```bash
cd backend
pip install -e '.[dev]'
pytest
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Full local stack:

```bash
docker compose up --build
```

## Engineering rules

1. Deterministic tools before LLM reasoning whenever possible.
2. Agents plan; policy-bounded executors perform actions.
3. Every meaningful action produces traceable evidence.
4. New tools enter through capability/plugin contracts.
5. CI must stay green; do not weaken checks to hide failures.
6. Keep the architecture modular without premature microservices.

## Security boundary

CTF-OS is intended for authorized CTF/lab environments. The execution layer uses explicit capability policies rather than unrestricted agent shell access.
