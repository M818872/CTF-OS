# Contributing to CTF-OS

## Development rules

1. Keep capabilities small and deterministic where possible.
2. Do not bypass the execution policy for convenience.
3. Add tests for new runtime behavior and security-sensitive changes.
4. Prefer existing dependencies over new infrastructure.
5. Keep public contracts typed and documented.

## Pull requests

A PR should explain the user-visible behavior, tests executed, and any security or performance implications. CI must pass before merge.

## Commit style

Use short conventional prefixes such as `feat`, `fix`, `test`, `docs`, `ci`, and `refactor`.
