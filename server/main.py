from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from server.mcp_registry import MCPRegistry
from server.tool_loader import instantiate_tools


def create_app() -> FastAPI:
    app = FastAPI(title="MCP Tool Server")
    registry = MCPRegistry()
    registry.register_many(instantiate_tools())

    @app.get("/mcp/tools")
    def list_tools() -> Dict[str, Any]:
        return {"tools": registry.list_tools()}

    @app.post("/mcp/tools/{tool_name}")
    def run_tool(tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        tool = registry.tool(tool_name)
        if tool is None:
            raise HTTPException(status_code=404, detail="Tool not found")
        return tool.run(payload)

    return app


app = create_app()
