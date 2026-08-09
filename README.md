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

## CTF runtime and Kali tools

CTF-OS can detect whether a catalogued Kali tool is installed before the agent runs it. In a dedicated authorized CTF runtime, automatic provisioning can be enabled:

```bash
export CTF_OS_EXECUTION_MODE=direct
export CTF_OS_AUTO_INSTALL=1
```

Known Debian/Kali package mappings are installed automatically when available. If a tool has no known package mapping, the Tool Bus accepts an explicit custom installer command. Custom installer commands are passed through the same argv-based runtime boundary; shell operators such as `&&` are not interpreted as shell syntax.

After provisioning, the agent retries the requested tool and continues with the resulting output, token extraction, and finding extraction.

## Security boundary

CTF-OS is intended for authorized CTF/lab environments. Direct execution and automatic provisioning are disabled by default and should only be enabled inside the dedicated CTF runtime. The API layer should not be exposed as an unrestricted remote shell.
