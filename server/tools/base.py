from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Tool:
    name: str
    description: str
    folder_id: str
    labels: list[str] = field(default_factory=list)
    enabled: bool = True
    hidden: bool = False


class BaseTool:
    metadata: Tool

    def __init__(self, metadata: Tool) -> None:
        self.metadata = metadata

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Tools must implement run().")

    def as_mcp_tool(self) -> dict[str, Any]:
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "folder_id": self.metadata.folder_id,
            "labels": list(self.metadata.labels),
            "enabled": self.metadata.enabled,
            "hidden": self.metadata.hidden,
        }
