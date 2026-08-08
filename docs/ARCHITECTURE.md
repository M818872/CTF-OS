# CTF-OS Architecture

## Design goal

CTF-OS is an AI-assisted CTF investigation platform. Deterministic capabilities do the measurable work; the manager plans and selects capabilities; the evidence layer preserves observations for verification and reporting.

## Runtime

```text
UI -> API -> Investigation Manager -> Workflow -> Capability Registry -> Executor
                                                        |                 |
                                                        +-> Specialist    +-> Tool
                                                              |
                                                              v
                                                         Evidence -> Timeline -> Report
```

## Boundaries

- **API:** transport and validation only.
- **Manager:** investigation planning and delegation.
- **Workflow:** ordered, conditional task execution.
- **Capability:** stable semantic contract such as `decode.base64` or `analyze.hash`.
- **Plugin:** concrete implementation of a capability using a local tool or library.
- **Executor:** policy-controlled process boundary. It must not become an unrestricted shell exposed to a model.
- **Evidence:** immutable observations with source and confidence.
- **Timeline:** chronological investigation events.
- **Report:** deterministic rendering of recorded evidence and events.

## AI boundary

The model may propose actions only through registered capabilities. It never receives arbitrary command execution as a primitive. This makes decisions auditable and lets deterministic tests cover security-sensitive execution paths.

## Performance strategy

Prefer local deterministic operations first. Invoke an LLM only when classification, interpretation, or synthesis cannot be reliably performed by a deterministic capability. Keep plugin startup cheap and stream large outputs rather than duplicating them in memory.

## Versioning

Alpha uses a modular monolith. Services should not be split until measurements demonstrate a real scaling or isolation requirement.
