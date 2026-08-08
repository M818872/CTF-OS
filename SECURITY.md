# Security Policy

## Scope

CTF-OS is intended for authorized CTF, lab, and training environments. Do not use it against systems without permission.

## Reporting

Please report security issues privately to the repository maintainers before opening a public issue when the issue could expose credentials, execute unintended commands, or compromise a deployment.

## Execution safety

The execution runtime is deliberately policy-bounded. New command capabilities must document their allowlist, argument constraints, timeout behavior, output limits, and test coverage before being enabled.

Never commit secrets, API keys, challenge credentials, or private target information.
