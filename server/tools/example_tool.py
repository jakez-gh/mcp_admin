from __future__ import annotations

from typing import Any, Dict

from server.tools.base import BaseTool, Tool


class ExampleEchoTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            Tool(
                name="example.echo",
                description="Echoes the payload back to the caller.",
                folder_id="examples",
                labels=["demo"],
                enabled=True,
                hidden=False,
            )
        )

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"echo": payload}
