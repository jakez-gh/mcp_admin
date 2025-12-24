import sqlite3
import unittest

from mcp_admin.db import apply_migrations, get_connection
from mcp_admin.repositories import FolderRepository, LabelRepository, ToolRepository


class MigrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = get_connection(":memory:")
        apply_migrations(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def test_root_folder_and_label_exist(self) -> None:
        folder = self.conn.execute("SELECT id, name FROM folders WHERE id = 1;").fetchone()
        label = self.conn.execute("SELECT id, name FROM labels WHERE id = 1;").fetchone()
        self.assertIsNotNone(folder)
        self.assertIsNotNone(label)
        self.assertEqual(folder["name"], "root")
        self.assertEqual(label["name"], "root")

    def test_delete_root_folder_is_blocked(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("DELETE FROM folders WHERE id = 1;")

    def test_delete_root_label_is_blocked(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("DELETE FROM labels WHERE id = 1;")


class FolderBehaviorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = get_connection(":memory:")
        apply_migrations(self.conn)
        self.folders = FolderRepository(self.conn)
        self.tools = ToolRepository(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def test_delete_folder_reparents_children_and_tools(self) -> None:
        parent_id = self.folders.create("parent")
        child_id = self.folders.create("child", parent_id)
        grandchild_id = self.folders.create("grandchild", child_id)
        tool_id = self.tools.create("tool", child_id)

        self.folders.delete(child_id)

        child_row = self.folders.get(child_id)
        self.assertIsNone(child_row)
        grandchild_row = self.folders.get(grandchild_id)
        self.assertEqual(grandchild_row["parent_id"], parent_id)
        tool_row = self.tools.get(tool_id)
        self.assertEqual(tool_row["folder_id"], parent_id)

    def test_copy_folder_creates_new_entry(self) -> None:
        folder_id = self.folders.create("original")
        copy_id = self.folders.copy(folder_id, 1)
        self.assertNotEqual(folder_id, copy_id)
        copy_row = self.folders.get(copy_id)
        self.assertEqual(copy_row["parent_id"], 1)
        self.assertIn("copy", copy_row["name"])


class LabelBehaviorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = get_connection(":memory:")
        apply_migrations(self.conn)
        self.labels = LabelRepository(self.conn)
        self.tools = ToolRepository(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def test_delete_label_reparents_children(self) -> None:
        parent_id = self.labels.create("parent")
        child_id = self.labels.create("child", parent_id)
        grandchild_id = self.labels.create("grandchild", child_id)

        self.labels.delete(child_id)

        child_row = self.labels.get(child_id)
        self.assertIsNone(child_row)
        grandchild_row = self.labels.get(grandchild_id)
        self.assertEqual(grandchild_row["parent_id"], parent_id)

    def test_copy_tool_includes_labels(self) -> None:
        tool_id = self.tools.create("tool")
        label_id = self.labels.create("label")
        self.tools.add_label(tool_id, label_id)

        copy_id = self.tools.copy(tool_id, 1)

        labels = self.tools.list_labels(copy_id)
        self.assertEqual([row["id"] for row in labels], [label_id])


if __name__ == "__main__":
    unittest.main()
