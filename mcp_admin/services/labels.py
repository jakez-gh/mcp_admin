import sqlite3

from mcp_admin.repositories import LabelRepository


class LabelService:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.labels = LabelRepository(conn)

    def create_label(self, name: str, parent_id: int = 1) -> int:
        return self.labels.create(name, parent_id)

    def rename_label(self, label_id: int, name: str) -> None:
        self.labels.update(label_id, name)

    def delete_label(self, label_id: int) -> None:
        self.labels.delete(label_id)

    def move_label(self, label_id: int, new_parent_id: int) -> None:
        self.labels.move(label_id, new_parent_id)

    def copy_label(self, label_id: int, new_parent_id: int) -> int:
        return self.labels.copy(label_id, new_parent_id)

    def list_children(self, parent_id: int) -> list[sqlite3.Row]:
        return list(self.labels.list_children(parent_id))
