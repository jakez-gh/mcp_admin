import sqlite3

from mcp_admin.repositories import ToolRepository


class ToolService:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.tools = ToolRepository(conn)

    def create_tool(self, name: str, folder_id: int = 1) -> int:
        return self.tools.create(name, folder_id)

    def rename_tool(self, tool_id: int, name: str) -> None:
        self.tools.update(tool_id, name)

    def delete_tool(self, tool_id: int) -> None:
        self.tools.delete(tool_id)

    def move_tool(self, tool_id: int, new_folder_id: int) -> None:
        self.tools.move(tool_id, new_folder_id)

    def copy_tool(self, tool_id: int, target_folder_id: int) -> int:
        return self.tools.copy(tool_id, target_folder_id)

    def add_label(self, tool_id: int, label_id: int) -> None:
        self.tools.add_label(tool_id, label_id)

    def remove_label(self, tool_id: int, label_id: int) -> None:
        self.tools.remove_label(tool_id, label_id)

    def list_labels(self, tool_id: int) -> list[sqlite3.Row]:
        return list(self.tools.list_labels(tool_id))
