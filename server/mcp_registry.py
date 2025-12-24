from __future__ import annotations

from typing import Dict, List

from server.tools.base import BaseTool


class MCPRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.metadata.name] = tool

    def register_many(self, tools: List[BaseTool]) -> None:
        for tool in tools:
            self.register(tool)

    def list_tools(self) -> List[Dict[str, object]]:
        return [tool.as_mcp_tool() for tool in self._tools.values()]

    def tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)
