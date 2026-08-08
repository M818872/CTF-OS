from app.tools.registry import get_tool, list_tools


def test_specialist_capabilities_are_registered() -> None:
    names = {tool.name for tool in list_tools()}
    assert "crypto.decode" in names
    assert "web.inspect" in names
    assert "forensics.identify" in names
    assert "reverse.strings" in names
    assert "network.identify" in names
    assert "stego.identify" in names
    assert "osint.collect" in names
    assert "mobile.identify" in names
    assert "blockchain.inspect" in names
    assert "pwn.identify" in names
    assert "misc.transform" in names


def test_crypto_decode_is_deterministic() -> None:
    tool = get_tool("crypto.decode")
    assert tool is not None
    result = tool.handler("SGVsbG8=")
    assert result.status == "completed"
    assert result.data["candidates"]["base64"] == "Hello"


def test_web_inspect_does_not_make_network_request() -> None:
    tool = get_tool("web.inspect")
    assert tool is not None
    result = tool.handler("https://example.org:8443/a?q=1")
    assert result.data["host"] == "example.org"
    assert result.data["port"] == 8443
