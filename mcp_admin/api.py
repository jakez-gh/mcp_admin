from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from mcp_admin.tools.registry import ToolNode, discover_tools, get_label_path, toggle_tool

DEFAULT_TOOL_DEFS: List[dict] = [
    {
        "name": "messaging",
        "label": "Messaging",
        "children": [
            {"name": "echo", "label": "Echo"},
            {"name": "broadcast", "label": "Broadcast"},
        ],
    },
    {
        "name": "analytics",
        "label": "Analytics",
        "children": [{"name": "report", "label": "Report"}],
    },
]


class ToggleRequest(BaseModel):
    enabled: bool


def create_app(definitions: Optional[List[dict]] = None) -> FastAPI:
    app = FastAPI(title="MCP Admin")
    tool_definitions = DEFAULT_TOOL_DEFS if definitions is None else definitions
    app.state.root = discover_tools(tool_definitions)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/tools")
    def list_tools() -> dict:
        root: ToolNode = app.state.root
        return {"tools": [child.to_dict() for child in root.children]}

    @app.post("/tools/{tool_name}/enable")
    def set_tool_enabled(tool_name: str, request: ToggleRequest) -> dict:
        root: ToolNode = app.state.root
        if not toggle_tool(root, tool_name, request.enabled):
            raise HTTPException(status_code=404, detail="Tool not found")
        return {"name": tool_name, "enabled": request.enabled}

    @app.get("/tools/{tool_name}/labels")
    def tool_labels(tool_name: str) -> dict:
        root: ToolNode = app.state.root
        labels = get_label_path(root, tool_name)
        if not labels:
            raise HTTPException(status_code=404, detail="Tool not found")
        return {"labels": labels}

    return app


app = create_app()
