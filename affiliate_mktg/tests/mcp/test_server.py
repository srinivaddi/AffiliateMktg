import sys
import types
import importlib
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.asyncio

# ✅ Adjust if your module path differs
MODULE_UNDER_TEST = "affiliate_mktg.src.mcp.server"

def _install_stub_module(monkeypatch, full_name: str, **attrs):
    """Install stub module into sys.modules (and parents)."""
    parts = full_name.split(".")
    for i in range(1, len(parts) + 1):
        name = ".".join(parts[:i])
        if name not in sys.modules:
            mod = types.ModuleType(name)
            monkeypatch.setitem(sys.modules, name, mod)

    mod = sys.modules[full_name]
    for k, v in attrs.items():
        setattr(mod, k, v)
    return mod


@pytest.fixture
def tool_module(monkeypatch):
    """
    Import module under test safely:
    - stub FastMCP
    - stub LinksManager
    """
    # ---- stub FastMCP ----
    class FakeFastMCP:
        def __init__(self, *args, **kwargs): pass
        def tool(self, *args, **kwargs):
            def decorator(fn):
                return fn
            return decorator

    _install_stub_module(monkeypatch, "fastmcp", FastMCP=FakeFastMCP)

    # ---- stub SearchInput model ----
    class FakeSearchInput:
        pass

    _install_stub_module(
        monkeypatch,
        "affiliate_mktg.src.core.models",
        SearchInput=FakeSearchInput,
    )

    # ---- stub LinksManager ----
    class FakeLinksManager:
        async def generate_link_post_blog_manual(self, searchInput):
            raise NotImplementedError

    _install_stub_module(
        monkeypatch,
        "affiliate_mktg.src.links.links_manager",
        LinksManager=FakeLinksManager,
    )

    if MODULE_UNDER_TEST in sys.modules:
        del sys.modules[MODULE_UNDER_TEST]

    return importlib.import_module(MODULE_UNDER_TEST)

async def test_tool_success_path(tool_module, monkeypatch):
    """When LinksManager returns success=True"""
    class SuccessLinksManager:
        async def generate_link_post_blog_manual(self, searchInput):
            return {
                "success": True,
                "content": "anything",
            }

    monkeypatch.setattr(tool_module, "LinksManager", SuccessLinksManager)

    result = await tool_module.generate_link_post_blog_manual_tool(
        searchInput=SimpleNamespace()
    )

    assert result == {
        "status": "Processed",
        "success": True,
        "content": "Blog Generated and Posted.",
    }


async def test_tool_processed_but_unsuccessful(tool_module, monkeypatch):
    """Processed but success=False → pass through content"""
    class FailLinksManager:
        async def generate_link_post_blog_manual(self, searchInput):
            return {
                "success": False,
                "content": "Filtered by rules",
            }

    monkeypatch.setattr(tool_module, "LinksManager", FailLinksManager)

    result = await tool_module.generate_link_post_blog_manual_tool(
        searchInput=SimpleNamespace()
    )

    assert result == {
        "status": "Processed",
        "success": False,
        "content": "Filtered by rules",
    }


async def test_tool_exception_path(tool_module, monkeypatch):
    """Exception inside LinksManager → Failure response"""
    class ExplodingLinksManager:
        async def generate_link_post_blog_manual(self, searchInput):
            raise RuntimeError("boom")

    monkeypatch.setattr(tool_module, "LinksManager", ExplodingLinksManager)

    result = await tool_module.generate_link_post_blog_manual_tool(
        searchInput=SimpleNamespace()
    )

    assert result["status"] == "Failure"
    assert result["success"] is False
    assert "NOT Generated and Posted" in result["content"]
    assert "boom" in result["content"]
