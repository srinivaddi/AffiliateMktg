import pytest
from types import SimpleNamespace

from affiliate_mktg.src.mcp.mcp_wrapper import (
    FastMCPWrapper,
    MCPToolInvoker,
)

pytestmark = pytest.mark.asyncio


async def async_tool(*args, **kwargs):
    return {"ok": True, "args": args, "kwargs": kwargs}


async def failing_tool(*args, **kwargs):
    raise RuntimeError("boom")


class ToolWithFn:
    def __init__(self, fn):
        self.fn = fn


class FakeToolManager:
    def __init__(self, tools):
        self._tools = tools


class FakeMCPServer:
    def __init__(self, tools):
        self._tool_manager = FakeToolManager(tools)

async def test_fastmcpwrapper_callable_tool():
    server = FakeMCPServer(
        tools={"my_tool": async_tool}
    )
    wrapper = FastMCPWrapper(server)

    result = await wrapper.call_fastMPC_tool(
        "my_tool", 1, a=2
    )

    assert result["ok"] is True
    assert result["args"] == (1,)
    assert result["kwargs"] == {"a": 2}


async def test_fastmcpwrapper_tool_with_fn():
    server = FakeMCPServer(
        tools={"my_tool": ToolWithFn(async_tool)}
    )
    wrapper = FastMCPWrapper(server)

    result = await wrapper.call_fastMPC_tool("my_tool")

    assert result == {"ok": True, "args": (), "kwargs": {}}


async def test_fastmcpwrapper_tool_not_found():
    server = FakeMCPServer(tools={})
    wrapper = FastMCPWrapper(server)

    result = await wrapper.call_fastMPC_tool("missing")

    assert "error" in result
    assert "Tool 'missing' not found" in result["error"]


async def test_fastmcpwrapper_tool_not_callable():
    server = FakeMCPServer(
        tools={"bad": object()}
    )
    wrapper = FastMCPWrapper(server)

    result = await wrapper.call_fastMPC_tool("bad")

    assert "error" in result
    assert "not callable" in result["error"]


async def test_fastmcpwrapper_tool_raises_exception():
    server = FakeMCPServer(
        tools={"explode": failing_tool}
    )
    wrapper = FastMCPWrapper(server)

    result = await wrapper.call_fastMPC_tool("explode")

    assert result == {"error": "boom"}

async def test_mcptoolinvoker_callable_tool():
    server = FakeMCPServer(
        tools={"my_tool": async_tool}
    )
    invoker = MCPToolInvoker(server)

    result = await invoker.invoke_tool("my_tool", 42)

    assert result["ok"] is True
    assert result["args"] == (42,)


async def test_mcptoolinvoker_tool_with_fn():
    server = FakeMCPServer(
        tools={"my_tool": ToolWithFn(async_tool)}
    )
    invoker = MCPToolInvoker(server)

    result = await invoker.invoke_tool("my_tool")

    assert result["ok"] is True


async def test_mcptoolinvoker_tool_not_found():
    server = FakeMCPServer(tools={})
    invoker = MCPToolInvoker(server)

    with pytest.raises(ValueError) as exc:
        await invoker.invoke_tool("missing")

    assert "Tool 'missing' not found" in str(exc.value)


async def test_mcptoolinvoker_tool_not_callable():
    server = FakeMCPServer(
        tools={"bad": object()}
    )
    invoker = MCPToolInvoker(server)

    with pytest.raises(TypeError) as exc:
        await invoker.invoke_tool("bad")

    assert "not callable" in str(exc.value)