PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS folder_tree (
    folder_id INTEGER PRIMARY KEY,
    parent_id INTEGER,
    FOREIGN KEY(folder_id) REFERENCES folders(id) ON DELETE CASCADE,
    FOREIGN KEY(parent_id) REFERENCES folders(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS label_tree (
    label_id INTEGER PRIMARY KEY,
    parent_id INTEGER,
    FOREIGN KEY(label_id) REFERENCES labels(id) ON DELETE CASCADE,
    FOREIGN KEY(parent_id) REFERENCES labels(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    folder_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(folder_id) REFERENCES folders(id)
);

CREATE TABLE IF NOT EXISTS tool_labels (
    tool_id INTEGER NOT NULL,
    label_id INTEGER NOT NULL,
    PRIMARY KEY (tool_id, label_id),
    FOREIGN KEY(tool_id) REFERENCES tools(id) ON DELETE CASCADE,
    FOREIGN KEY(label_id) REFERENCES labels(id) ON DELETE CASCADE
);

CREATE TRIGGER IF NOT EXISTS folders_prevent_root_delete
BEFORE DELETE ON folders
WHEN OLD.id = 1
BEGIN
    SELECT RAISE(ABORT, 'cannot delete root folder');
END;

CREATE TRIGGER IF NOT EXISTS folders_reparent_children
BEFORE DELETE ON folders
BEGIN
    UPDATE folder_tree
    SET parent_id = (SELECT parent_id FROM folder_tree WHERE folder_id = OLD.id)
    WHERE parent_id = OLD.id;

    UPDATE tools
    SET folder_id = (SELECT parent_id FROM folder_tree WHERE folder_id = OLD.id)
    WHERE folder_id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS labels_prevent_root_delete
BEFORE DELETE ON labels
WHEN OLD.id = 1
BEGIN
    SELECT RAISE(ABORT, 'cannot delete root label');
END;

CREATE TRIGGER IF NOT EXISTS labels_reparent_children
BEFORE DELETE ON labels
BEGIN
    UPDATE label_tree
    SET parent_id = (SELECT parent_id FROM label_tree WHERE label_id = OLD.id)
    WHERE parent_id = OLD.id;
END;

INSERT INTO folders (id, name) VALUES (1, 'root');
INSERT INTO folder_tree (folder_id, parent_id) VALUES (1, NULL);

INSERT INTO labels (id, name) VALUES (1, 'root');
INSERT INTO label_tree (label_id, parent_id) VALUES (1, NULL);
