from __future__ import annotations

import sqlite3
from typing import Iterable


class FolderRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, name: str, parent_id: int = 1) -> int:
        cur = self.conn.execute(
            "INSERT INTO folders (name) VALUES (?);",
            (name,),
        )
        folder_id = cur.lastrowid
        self.conn.execute(
            "INSERT INTO folder_tree (folder_id, parent_id) VALUES (?, ?);",
            (folder_id, parent_id),
        )
        self.conn.commit()
        return int(folder_id)

    def get(self, folder_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            """
            SELECT folders.id, folders.name, folder_tree.parent_id, folders.created_at
            FROM folders
            JOIN folder_tree ON folder_tree.folder_id = folders.id
            WHERE folders.id = ?;
            """,
            (folder_id,),
        ).fetchone()

    def list_children(self, parent_id: int) -> Iterable[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT folders.id, folders.name, folder_tree.parent_id, folders.created_at
            FROM folders
            JOIN folder_tree ON folder_tree.folder_id = folders.id
            WHERE folder_tree.parent_id = ?
            ORDER BY folders.name;
            """,
            (parent_id,),
        ).fetchall()

    def update(self, folder_id: int, name: str) -> None:
        self.conn.execute(
            "UPDATE folders SET name = ? WHERE id = ?;",
            (name, folder_id),
        )
        self.conn.commit()

    def delete(self, folder_id: int) -> None:
        self.conn.execute("DELETE FROM folders WHERE id = ?;", (folder_id,))
        self.conn.commit()

    def move(self, folder_id: int, new_parent_id: int) -> None:
        if folder_id == new_parent_id or self._is_descendant(new_parent_id, folder_id):
            raise ValueError("Cannot move folder into itself or its descendants")
        self.conn.execute(
            "UPDATE folder_tree SET parent_id = ? WHERE folder_id = ?;",
            (new_parent_id, folder_id),
        )
        self.conn.commit()

    def copy(self, folder_id: int, new_parent_id: int) -> int:
        row = self.get(folder_id)
        if row is None:
            raise ValueError(f"Folder {folder_id} not found")
        return self.create(f"{row['name']} (copy)", new_parent_id)

    def _is_descendant(self, candidate_id: int, folder_id: int) -> bool:
        row = self.conn.execute(
            """
            WITH RECURSIVE descendants(id) AS (
                SELECT folder_id
                FROM folder_tree
                WHERE folder_id = ?
                UNION ALL
                SELECT folder_tree.folder_id
                FROM folder_tree
                JOIN descendants ON folder_tree.parent_id = descendants.id
            )
            SELECT 1
            FROM descendants
            WHERE id = ?
            LIMIT 1;
            """,
            (folder_id, candidate_id),
        ).fetchone()
        return row is not None
