from app.runtime.kali_catalog import KALI_TOOLS, get_kali_tool, list_kali_tools


def test_kali_catalog_has_expected_domains() -> None:
    categories = {tool.category for tool in KALI_TOOLS}
    assert {"network", "web", "forensics", "reverse", "pwn", "crypto", "stego", "mobile"} <= categories


def test_kali_tool_lookup() -> None:
    tool = get_kali_tool("nmap")
    assert tool is not None
    assert tool.binary == "nmap"
    assert tool.category == "network"


def test_kali_category_filter() -> None:
    tools = list_kali_tools("reverse")
    assert tools
    assert all(tool.category == "reverse" for tool in tools)


def test_kali_catalog_names_are_unique() -> None:
    names = [tool.name for tool in KALI_TOOLS]
    assert len(names) == len(set(names))
