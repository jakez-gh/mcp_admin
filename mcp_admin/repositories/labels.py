from __future__ import annotations

import sqlite3
from collections.abc import Iterable


class LabelRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, name: str, parent_id: int = 1) -> int:
        cur = self.conn.execute(
            "INSERT INTO labels (name) VALUES (?);",
            (name,),
        )
        label_id = cur.lastrowid
        self.conn.execute(
            "INSERT INTO label_tree (label_id, parent_id) VALUES (?, ?);",
            (label_id, parent_id),
        )
        self.conn.commit()
        return int(label_id)

    def get(self, label_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            """
            SELECT labels.id, labels.name, label_tree.parent_id, labels.created_at
            FROM labels
            JOIN label_tree ON label_tree.label_id = labels.id
            WHERE labels.id = ?;
            """,
            (label_id,),
        ).fetchone()

    def list_children(self, parent_id: int) -> Iterable[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT labels.id, labels.name, label_tree.parent_id, labels.created_at
            FROM labels
            JOIN label_tree ON label_tree.label_id = labels.id
            WHERE label_tree.parent_id = ?
            ORDER BY labels.name;
            """,
            (parent_id,),
        ).fetchall()

    def update(self, label_id: int, name: str) -> None:
        self.conn.execute(
            "UPDATE labels SET name = ? WHERE id = ?;",
            (name, label_id),
        )
        self.conn.commit()

    def delete(self, label_id: int) -> None:
        self.conn.execute("DELETE FROM labels WHERE id = ?;", (label_id,))
        self.conn.commit()

    def move(self, label_id: int, new_parent_id: int) -> None:
        if label_id == new_parent_id or self._is_descendant(new_parent_id, label_id):
            raise ValueError("Cannot move label into itself or its descendants")
        self.conn.execute(
            "UPDATE label_tree SET parent_id = ? WHERE label_id = ?;",
            (new_parent_id, label_id),
        )
        self.conn.commit()

    def copy(self, label_id: int, new_parent_id: int) -> int:
        row = self.get(label_id)
        if row is None:
            raise ValueError(f"Label {label_id} not found")
        return self.create(f"{row['name']} (copy)", new_parent_id)

    def _is_descendant(self, candidate_id: int, label_id: int) -> bool:
        row = self.conn.execute(
            """
            WITH RECURSIVE descendants(id) AS (
                SELECT label_id
                FROM label_tree
                WHERE label_id = ?
                UNION ALL
                SELECT label_tree.label_id
                FROM label_tree
                JOIN descendants ON label_tree.parent_id = descendants.id
            )
            SELECT 1
            FROM descendants
            WHERE id = ?
            LIMIT 1;
            """,
            (label_id, candidate_id),
        ).fetchone()
        return row is not None
