from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from app.runtime.result_parser import extract_tokens
from app.services.execution import CapabilityExecutionService


@dataclass(frozen=True)
class SolveStep:
    name: str
    command: str


@dataclass(frozen=True)
class SolveResult:
    flag: str | None
    steps: list[dict[str, object]]
    summary: str


class CtfSolver:
    """Small deterministic solve loop for the first end-to-end CTF runtime.

    It deliberately starts with low-risk discovery/inspection actions. The
    execution boundary remains responsible for enabling direct tool use in a
    dedicated CTF runtime.
    """

    _FLAG = re.compile(r"\b(?:FLAG|CTF|THM|HTB|PICOCTF)\{[^\n\r{}]{1,512}\}", re.IGNORECASE)

    def __init__(self) -> None:
        self.executor = CapabilityExecutionService()

    async def solve(
        self,
        challenge: str,
        url: str | None = None,
        artifact_path: str | None = None,
    ) -> SolveResult:
        steps: list[dict[str, object]] = []
        accumulated = challenge

        if artifact_path:
            steps.extend(
                [
                    {"name": "identify file", "command": f"file {artifact_path}"},
                    {"name": "extract strings", "command": f"strings -a {artifact_path}"},
                    {"name": "inspect metadata", "command": f"exiftool {artifact_path}"},
                ]
            )

        if url:
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError("Only http and https challenge URLs are supported")
            steps.extend(
                [
                    {"name": "fetch target", "command": f"curl -ksL --max-time 30 {url}"},
                    {"name": "inspect robots", "command": f"curl -ksL --max-time 15 {url.rstrip('/')}/robots.txt"},
                ]
            )

        for step in steps:
            command = str(step["command"])
            result = await self.executor.execute_terminal(command)
            output = f"{result.stdout}\n{result.stderr}"
            accumulated += "\n" + output
            step["returncode"] = result.returncode
            step["stdout"] = result.stdout[-12000:]
            step["stderr"] = result.stderr[-4000:]
            step["tokens"] = result.tokens
            found = self._find_flag(output)
            if found:
                return SolveResult(found, steps, f"Flag found during {step['name']}.")

        found = self._find_flag(accumulated)
        if found:
            return SolveResult(found, steps, "Flag found in the supplied challenge input or collected evidence.")
        return SolveResult(
            None,
            steps,
            "The first autonomous discovery pass completed without finding a flag; more specialist reasoning is required.",
        )

    @classmethod
    def _find_flag(cls, text: str) -> str | None:
        matches = extract_tokens(text)
        for token in matches:
            if cls._FLAG.fullmatch(token):
                return token
        match = cls._FLAG.search(text)
        return match.group(0) if match else None
