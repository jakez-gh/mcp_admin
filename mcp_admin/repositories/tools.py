from __future__ import annotations

import sqlite3
from collections.abc import Iterable


class ToolRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(
        self,
        name: str,
        folder_id: int = 1,
        description: str = "",
        enabled: bool = True,
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO tools (name, description, enabled, folder_id) VALUES (?, ?, ?, ?);",
            (name, description, int(enabled), folder_id),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get(self, tool_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            """
            SELECT id, name, description, enabled, folder_id, created_at
            FROM tools
            WHERE id = ?;
            """,
            (tool_id,),
        ).fetchone()

    def list_in_folder(self, folder_id: int) -> Iterable[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT id, name, description, enabled, folder_id, created_at
            FROM tools
            WHERE folder_id = ?
            ORDER BY name;
            """,
            (folder_id,),
        ).fetchall()

    def update(
        self,
        tool_id: int,
        name: str,
        *,
        description: str | None = None,
        enabled: bool | None = None,
        folder_id: int | None = None,
    ) -> None:
        current = self.get(tool_id)
        if current is None:
            raise ValueError(f"Tool {tool_id} not found")
        next_description = description if description is not None else current["description"]
        next_enabled = int(enabled) if enabled is not None else current["enabled"]
        next_folder_id = folder_id if folder_id is not None else current["folder_id"]
        self.conn.execute(
            """
            UPDATE tools
            SET name = ?, description = ?, enabled = ?, folder_id = ?
            WHERE id = ?;
            """,
            (name, next_description, next_enabled, next_folder_id, tool_id),
        )
        self.conn.commit()

    def delete(self, tool_id: int) -> None:
        self.conn.execute("DELETE FROM tools WHERE id = ?;", (tool_id,))
        self.conn.commit()

    def move(self, tool_id: int, new_folder_id: int) -> None:
        self.conn.execute(
            "UPDATE tools SET folder_id = ? WHERE id = ?;",
            (new_folder_id, tool_id),
        )
        self.conn.commit()

    def copy(self, tool_id: int, target_folder_id: int) -> int:
        row = self.get(tool_id)
        if row is None:
            raise ValueError(f"Tool {tool_id} not found")
        cur = self.conn.execute(
            "INSERT INTO tools (name, description, enabled, folder_id) VALUES (?, ?, ?, ?);",
            (f"{row['name']} (copy)", row["description"], row["enabled"], target_folder_id),
        )
        new_tool_id = int(cur.lastrowid)
        labels = self.conn.execute(
            "SELECT label_id FROM tool_labels WHERE tool_id = ?;",
            (tool_id,),
        ).fetchall()
        for label in labels:
            self.conn.execute(
                "INSERT INTO tool_labels (tool_id, label_id) VALUES (?, ?);",
                (new_tool_id, label["label_id"]),
            )
        self.conn.commit()
        return new_tool_id

    def add_label(self, tool_id: int, label_id: int) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO tool_labels (tool_id, label_id) VALUES (?, ?);",
            (tool_id, label_id),
        )
        self.conn.commit()

    def remove_label(self, tool_id: int, label_id: int) -> None:
        self.conn.execute(
            "DELETE FROM tool_labels WHERE tool_id = ? AND label_id = ?;",
            (tool_id, label_id),
        )
        self.conn.commit()

    def list_labels(self, tool_id: int) -> Iterable[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT labels.id, labels.name
            FROM labels
            JOIN tool_labels ON tool_labels.label_id = labels.id
            WHERE tool_labels.tool_id = ?
            ORDER BY labels.name;
            """,
            (tool_id,),
        ).fetchall()
