import sqlite3

from mcp_admin.repositories import FolderRepository, ToolRepository


class FolderService:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.folders = FolderRepository(conn)
        self.tools = ToolRepository(conn)

    def create_folder(self, name: str, parent_id: int = 1) -> int:
        return self.folders.create(name, parent_id)

    def rename_folder(self, folder_id: int, name: str) -> None:
        self.folders.update(folder_id, name)

    def delete_folder(self, folder_id: int) -> None:
        self.folders.delete(folder_id)

    def move_folder(self, folder_id: int, new_parent_id: int) -> None:
        self.folders.move(folder_id, new_parent_id)

    def copy_folder(self, folder_id: int, new_parent_id: int) -> int:
        return self.folders.copy(folder_id, new_parent_id)

    def list_children(self, parent_id: int) -> list[sqlite3.Row]:
        return list(self.folders.list_children(parent_id))

    def list_tools(self, folder_id: int) -> list[sqlite3.Row]:
        return list(self.tools.list_in_folder(folder_id))
