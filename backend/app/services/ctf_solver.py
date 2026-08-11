from __future__ import annotations

import base64
import binascii
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

from app.runtime.result_parser import extract_tokens
from app.services.execution import CapabilityExecutionService


@dataclass(frozen=True)
class SolveResult:
    flag: str | None
    steps: list[dict[str, object]]
    summary: str


class CtfSolver:
    """Autonomous, bounded CTF solving loop for the dedicated runtime.

    The solver is intentionally tool-driven: inspect the input, infer the
    challenge shape from observed output, run the next relevant technique,
    decode useful artifacts, and repeat until a flag is found or the bounded
    investigation budget is exhausted.
    """

    _FLAG = re.compile(
        r"(?:flag|ctf|thm|htb|picoctf|picoCTF)\{[^\n\r{}]{1,512}\}",
        re.IGNORECASE,
    )
    _URL = re.compile(r"https?://[^\s\"'<>]{4,500}", re.IGNORECASE)
    _B64 = re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{20,}={0,2}(?![A-Za-z0-9+/])")
    _HEX = re.compile(r"(?<![0-9a-fA-F])(?:[0-9a-fA-F]{2}){8,}(?![0-9a-fA-F])")
    _JWT = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
    _MAX_STEPS = int(os.getenv("CTF_OS_SOLVER_MAX_STEPS", "24"))
    _MAX_LINKS = int(os.getenv("CTF_OS_SOLVER_MAX_LINKS", "12"))

    def __init__(self) -> None:
        self.executor = CapabilityExecutionService()
        self._apt_updated = False

    async def solve(
        self,
        challenge: str,
        url: str | None = None,
        artifact_path: str | None = None,
    ) -> SolveResult:
        steps: list[dict[str, object]] = []
        evidence: list[str] = [challenge]
        seen: set[str] = set()
        workdir = Path(tempfile.mkdtemp(prefix="ctfos-solve-"))

        try:
            if self._find_flag(challenge):
                return SolveResult(self._find_flag(challenge), steps, "Flag found directly in the supplied challenge.")

            if artifact_path:
                await self._solve_file(Path(artifact_path), workdir, steps, evidence, seen)
            if url and not self._find_flag("\n".join(evidence)):
                await self._solve_web(url, steps, evidence, seen)

            # Run generic decoding against accumulated text after tool passes.
            await self._decode_evidence(evidence, steps, seen)
            flag = self._find_flag("\n".join(evidence))
            if flag:
                return SolveResult(flag, steps, f"Flag found after {len(steps)} autonomous analysis steps.")
            return SolveResult(
                None,
                steps,
                f"Completed {len(steps)} adaptive CTF analysis steps without finding a flag.",
            )
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    async def _solve_file(
        self,
        path: Path,
        workdir: Path,
        steps: list[dict[str, object]],
        evidence: list[str],
        seen: set[str],
    ) -> None:
        if not path.exists():
            raise ValueError(f"Challenge artifact not found: {path}")

        await self._run("identify file", ["file", "-k", str(path)], steps, evidence, seen)
        await self._run("extract strings", ["strings", "-a", str(path)], steps, evidence, seen)
        await self._run("inspect metadata", ["exiftool", str(path)], steps, evidence, seen)
        if self._find_flag("\n".join(evidence)):
            return

        kind = (evidence[-1] if evidence else "").lower()
        name = path.name.lower()
        mime = await self._file_type(path)
        descriptor = f"{kind}\n{mime}\n{name}".lower()

        if "zip archive" in descriptor or path.suffix.lower() == ".zip":
            await self._archive_pass(path, workdir, steps, evidence, seen, "zip")
        elif "7-zip" in descriptor or path.suffix.lower() == ".7z":
            await self._archive_pass(path, workdir, steps, evidence, seen, "7z")
        elif "rar archive" in descriptor or path.suffix.lower() == ".rar":
            await self._archive_pass(path, workdir, steps, evidence, seen, "rar")
        elif "tar archive" in descriptor or path.suffix.lower() in {".tar", ".tgz", ".gz", ".bz2", ".xz"}:
            await self._archive_pass(path, workdir, steps, evidence, seen, "tar")
        elif any(token in descriptor for token in ("png", "jpeg", "jpg", "bitmap", "gif")):
            await self._image_pass(path, workdir, steps, evidence, seen)
        elif "pdf" in descriptor:
            await self._run("extract PDF text", ["pdftotext", "-layout", str(path), "-"], steps, evidence, seen)
        elif "pcap" in descriptor or "capture file" in descriptor:
            await self._pcap_pass(path, steps, evidence, seen)
        elif "elf" in descriptor or "executable" in descriptor:
            await self._binary_pass(path, steps, evidence, seen)
        else:
            await self._run("hex preview", ["xxd", "-l", "512", str(path)], steps, evidence, seen)
            await self._run("embedded data scan", ["binwalk", str(path)], steps, evidence, seen)

        if not self._find_flag("\n".join(evidence)):
            await self._xor_pass(path, steps, evidence)
            await self._decode_evidence(evidence, steps, seen)

    async def _archive_pass(
        self,
        path: Path,
        workdir: Path,
        steps: list[dict[str, object]],
        evidence: list[str],
        seen: set[str],
        archive_type: str,
    ) -> None:
        listing = ["7z", "l", "-slt", str(path)] if archive_type in {"7z", "rar"} else ["unzip", "-l", str(path)]
        await self._run("list archive", listing, steps, evidence, seen)
        destination = workdir / f"extract-{len(seen)}"
        destination.mkdir(parents=True, exist_ok=True)
        if archive_type == "zip":
            command = ["unzip", "-o", str(path), "-d", str(destination)]
        else:
            command = ["7z", "x", "-y", f"-o{destination}", str(path)]
        await self._run("extract archive", command, steps, evidence, seen)
        files = [item for item in destination.rglob("*") if item.is_file()][:40]
        for child in files:
            if len(steps) >= self._MAX_STEPS or self._find_flag("\n".join(evidence)):
                break
            await self._run("inspect extracted file", ["file", "-k", str(child)], steps, evidence, seen)
            await self._run("strings extracted file", ["strings", "-a", str(child)], steps, evidence, seen)
            if child.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".gif"}:
                await self._image_pass(child, workdir, steps, evidence, seen)
            elif child.suffix.lower() in {".zip", ".7z", ".rar", ".tar", ".gz"}:
                await self._archive_pass(child, workdir, steps, evidence, seen, "zip" if child.suffix == ".zip" else "7z")

    async def _image_pass(
        self,
        path: Path,
        workdir: Path,
        steps: list[dict[str, object]],
        evidence: list[str],
        seen: set[str],
    ) -> None:
        await self._run("scan embedded image data", ["binwalk", "-e", str(path)], steps, evidence, seen)
        await self._run("inspect image bit planes", ["zsteg", "-a", str(path)], steps, evidence, seen, optional=True, package="zsteg")
        if path.suffix.lower() in {".jpg", ".jpeg"}:
            await self._run("inspect JPEG stego", ["steghide", "info", str(path)], steps, evidence, seen, optional=True, package="steghide")
            # Try challenge-derived passwords without brute-forcing the runtime.
            passwords = self._password_candidates(evidence)
            for password in passwords[:12]:
                output = await self._run(
                    "try stego password",
                    ["steghide", "extract", "-sf", str(path), "-p", password, "-f"],
                    steps,
                    evidence,
                    seen,
                    optional=True,
                    package="steghide",
                )
                if output and self._find_flag(output):
                    return
        await self._run("scan appended image data", ["strings", "-a", "-n", "6", str(path)], steps, evidence, seen)

    async def _pcap_pass(self, path: Path, steps: list[dict[str, object]], evidence: list[str], seen: set[str]) -> None:
        await self._run("list captured protocols", ["tshark", "-r", str(path), "-qz", "io,phs"], steps, evidence, seen)
        await self._run("search packet text", ["tshark", "-r", str(path), "-Y", "tcp or udp", "-T", "fields", "-e", "data.data"], steps, evidence, seen)
        await self._run("search HTTP objects", ["tshark", "-r", str(path), "-Y", "http", "-T", "fields", "-e", "http.request.uri", "-e", "http.file_data"], steps, evidence, seen)

    async def _binary_pass(self, path: Path, steps: list[dict[str, object]], evidence: list[str], seen: set[str]) -> None:
        await self._run("inspect ELF headers", ["readelf", "-h", str(path)], steps, evidence, seen)
        await self._run("inspect ELF sections", ["readelf", "-S", str(path)], steps, evidence, seen)
        await self._run("inspect symbols", ["readelf", "-s", str(path)], steps, evidence, seen)
        await self._run("extract executable strings", ["strings", "-a", "-n", "5", str(path)], steps, evidence, seen)

    async def _solve_web(self, url: str, steps: list[dict[str, object]], evidence: list[str], seen: set[str]) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Only http and https challenge URLs are supported")
        base = f"{parsed.scheme}://{parsed.netloc}"
        candidates = [
            url,
            urljoin(url.rstrip("/") + "/", "robots.txt"),
            urljoin(url.rstrip("/") + "/", "sitemap.xml"),
            urljoin(url.rstrip("/") + "/", ".git/HEAD"),
            urljoin(url.rstrip("/") + "/", "admin"),
            urljoin(url.rstrip("/") + "/", "flag"),
            urljoin(url.rstrip("/") + "/", "robots.txt%3F"),
        ]
        for target in candidates:
            await self._run("fetch web target", ["curl", "-ksL", "--max-time", "30", "-i", target], steps, evidence, seen)
            if self._find_flag("\n".join(evidence)):
                return

        host = parsed.hostname or ""
        await self._run("enumerate target services", ["nmap", "-Pn", "-T3", "--top-ports", "100", "-sV", host], steps, evidence, seen, optional=True, package="nmap")
        links = self._same_origin_links("\n".join(evidence), base)
        for link in links[: self._MAX_LINKS]:
            await self._run("inspect discovered endpoint", ["curl", "-ksL", "--max-time", "20", "-i", link], steps, evidence, seen)
            if self._find_flag("\n".join(evidence)):
                return

        await self._decode_evidence(evidence, steps, seen)

    async def _run(
        self,
        name: str,
        argv: list[str],
        steps: list[dict[str, object]],
        evidence: list[str],
        seen: set[str],
        optional: bool = False,
        package: str | None = None,
    ) -> str:
        if len(steps) >= self._MAX_STEPS:
            return ""
        command = " ".join(self._quote(arg) for arg in argv)
        if command in seen:
            return ""
        seen.add(command)
        if package and shutil.which(argv[0]) is None:
            if os.getenv("CTF_OS_AUTO_INSTALL", "1") == "1":
                installed = await self._install(package)
                if not installed:
                    if optional:
                        return ""
                    raise RuntimeError(f"Required CTF tool is unavailable: {argv[0]}")
            elif optional:
                return ""
            else:
                raise RuntimeError(f"Required CTF tool is unavailable: {argv[0]}")
        try:
            result = await self.executor.execute_terminal(command)
        except (RuntimeError, ValueError) as exc:
            if optional:
                return ""
            raise RuntimeError(f"{name}: {exc}") from exc
        output = f"{result.stdout}\n{result.stderr}".strip()
        evidence.append(output)
        steps.append(
            {
                "name": name,
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout[-12000:],
                "stderr": result.stderr[-4000:],
                "tokens": result.tokens,
            }
        )
        return output

    async def _install(self, package: str) -> bool:
        package_map = {
            "zsteg": ["ruby", "ruby-dev"],
            "steghide": ["steghide"],
            "nmap": ["nmap"],
        }
        packages = package_map.get(package, [package])
        if not self._apt_updated:
            update = await self.executor.execute_terminal("apt-get update")
            if update.returncode != 0:
                return False
            self._apt_updated = True
        for item in packages:
            result = await self.executor.execute_terminal(f"apt-get install -y {self._quote(item)}")
            if result.returncode != 0:
                return False
        if package == "zsteg" and shutil.which("zsteg") is None:
            result = await self.executor.execute_terminal("gem install zsteg --no-document")
            return result.returncode == 0
        return shutil.which(package) is not None

    async def _file_type(self, path: Path) -> str:
        result = await self.executor.execute_terminal(f"file -b {self._quote(str(path))}")
        return result.stdout.lower()

    async def _decode_evidence(self, evidence: list[str], steps: list[dict[str, object]], seen: set[str]) -> None:
        text = "\n".join(evidence)
        candidates: list[tuple[str, str]] = []
        candidates.extend(("base64", value) for value in self._B64.findall(text))
        candidates.extend(("hex", value) for value in self._HEX.findall(text))
        candidates.extend(("jwt", value) for value in self._JWT.findall(text))
        for kind, value in candidates[:80]:
            if len(steps) >= self._MAX_STEPS:
                break
            decoded = self._decode_candidate(kind, value)
            if decoded and decoded != value:
                evidence.append(decoded)
                steps.append({"name": f"decode {kind}", "command": f"internal:{kind}", "returncode": 0, "stdout": decoded[-12000:], "stderr": "", "tokens": extract_tokens(decoded)})
                if self._find_flag(decoded):
                    return
        urls = self._URL.findall(text)
        for discovered in urls[:10]:
            if discovered not in seen:
                # Keep decoding focused; URL execution is handled by the web pass.
                evidence.append(unquote(discovered))

    @staticmethod
    def _decode_candidate(kind: str, value: str) -> str | None:
        try:
            if kind == "base64":
                raw = base64.b64decode(value + "=" * (-len(value) % 4), validate=False)
                decoded = raw.decode("utf-8", errors="ignore").strip()
                return decoded if decoded and sum(ch.isprintable() for ch in decoded) / len(decoded) > 0.8 else None
            if kind == "hex":
                raw = bytes.fromhex(value)
                decoded = raw.decode("utf-8", errors="ignore").strip()
                return decoded if decoded and sum(ch.isprintable() for ch in decoded) / len(decoded) > 0.8 else None
            if kind == "jwt":
                parts = value.split(".")
                raw = base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4))
                return raw.decode("utf-8", errors="ignore")
        except (ValueError, UnicodeError, binascii.Error):
            return None
        return None

    async def _xor_pass(self, path: Path, steps: list[dict[str, object]], evidence: list[str]) -> None:
        try:
            data = path.read_bytes()[:2_000_000]
        except OSError:
            return
        best: list[tuple[float, int, str]] = []
        for key in range(1, 256):
            decoded = bytes(byte ^ key for byte in data)
            printable = sum((32 <= byte < 127) or byte in {9, 10, 13} for byte in decoded) / max(1, len(decoded))
            text = decoded.decode("utf-8", errors="ignore")
            score = printable + (4.0 if self._find_flag(text) else 0.0)
            if score > 0.78:
                best.append((score, key, text[:12000]))
        best.sort(reverse=True)
        for score, key, text in best[:5]:
            evidence.append(text)
            steps.append({"name": "single-byte XOR analysis", "command": f"internal:xor key=0x{key:02x}", "returncode": 0, "stdout": text, "stderr": "", "tokens": extract_tokens(text)})
            if self._find_flag(text):
                return

    @staticmethod
    def _password_candidates(evidence: list[str]) -> list[str]:
        text = "\n".join(evidence)
        words = re.findall(r"[A-Za-z0-9_!@#$%^&*.-]{4,32}", text)
        seen: set[str] = set()
        result: list[str] = []
        for word in words:
            if word.lower() in {"http", "https", "localhost", "password"}:
                continue
            if word not in seen:
                seen.add(word)
                result.append(word)
        return result

    @staticmethod
    def _same_origin_links(text: str, base: str) -> list[str]:
        links: list[str] = []
        seen: set[str] = set()
        for raw in CtfSolver._URL.findall(text):
            try:
                parsed = urlparse(raw)
                if parsed.netloc != urlparse(base).netloc:
                    continue
                clean = raw.rstrip("'\".,);]")
                if clean not in seen:
                    seen.add(clean)
                    links.append(clean)
            except ValueError:
                continue
        return links

    @staticmethod
    def _find_flag(text: str) -> str | None:
        matches = extract_tokens(text)
        for token in matches:
            if CtfSolver._FLAG.fullmatch(token):
                return token
        match = CtfSolver._FLAG.search(text)
        return match.group(0) if match else None

    @staticmethod
    def _quote(value: str) -> str:
        import shlex

        return shlex.quote(value)
