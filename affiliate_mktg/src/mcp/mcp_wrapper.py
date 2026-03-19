"""MCP tool invoker for calling FastMCP tools from the Starlette API."""


class FastMCPWrapper:
    def __init__(self, mcp_server):
        self._server = mcp_server

    async def call_fastMPC_tool(self, tool_name: str, *args, **kwargs):
        try:
            tool_func = getattr(
                self._server._tool_manager, "_tools", {}
            ).get(tool_name)

            if not tool_func:
                raise ValueError(f"Tool '{tool_name}' not found.")

            if callable(tool_func):
                return await tool_func(*args, **kwargs)

            if hasattr(tool_func, "fn") and callable(tool_func.fn):
                return await tool_func.fn(*args, **kwargs)

            raise TypeError(f"Tool '{tool_name}' is not callable.")
        except Exception as e:
            return {"error": str(e)}


class MCPToolInvoker:
    def __init__(self, mcp_server):
        self._tool_manager = mcp_server._tool_manager

    async def invoke_tool(self, tool_name: str, *args, **kwargs):
        tool = self._tool_manager._tools.get(tool_name)

        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found.")

        if callable(tool):
            return await tool(*args, **kwargs)

        if hasattr(tool, "fn") and callable(tool.fn):
            return await tool.fn(*args, **kwargs)

        raise TypeError(f"Tool '{tool_name}' is not callable.")
