from pathlib import Path

import pytest

from app.services.ctf_solver import CtfSolver


def test_find_flag_supports_common_ctf_formats() -> None:
    assert CtfSolver._find_flag("noise THM{hidden_flag} trailing") == "THM{hidden_flag}"
    assert CtfSolver._find_flag("picoCTF{decode_me}") == "picoCTF{decode_me}"


def test_decode_base64_and_hex() -> None:
    assert CtfSolver._decode_candidate("base64", "cGljb0NURnt0ZXN0fQ==") == "picoCTF{test}"
    assert CtfSolver._decode_candidate("hex", "7069636f4354467b746573747d") == "picoCTF{test}"


def test_same_origin_links_excludes_external_hosts() -> None:
    text = "https://challenge.local/a https://evil.example/x https://challenge.local/b"
    links = CtfSolver._same_origin_links(text, "https://challenge.local")
    assert links == ["https://challenge.local/a", "https://challenge.local/b"]


@pytest.mark.asyncio
async def test_solver_returns_direct_flag_without_runtime() -> None:
    result = await CtfSolver().solve("The answer is CTF{direct_hit}")
    assert result.flag == "CTF{direct_hit}"
    assert result.steps == []
