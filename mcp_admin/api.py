from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from mcp_admin.db import apply_migrations, get_connection
from mcp_admin.repositories import FolderRepository, LabelRepository, ToolRepository
from mcp_admin.tools.registry import ToolNode, discover_tools, get_label_path, toggle_tool

DEFAULT_TOOL_DEFS: list[dict] = [
    {
        "name": "messaging",
        "label": "Messaging",
        "children": [
            {"name": "echo", "label": "Echo"},
            {"name": "broadcast", "label": "Broadcast"},
        ],
    },
    {
        "name": "analytics",
        "label": "Analytics",
        "children": [{"name": "report", "label": "Report"}],
    },
]


class ToggleRequest(BaseModel):
    enabled: bool


class FolderRequest(BaseModel):
    name: str = Field(min_length=1)
    parentId: int | None = None


class LabelRequest(BaseModel):
    name: str = Field(min_length=1)
    parentId: int | None = None


class ToolRequest(BaseModel):
    name: str = Field(min_length=1)
    description: str = ""
    enabled: bool = True
    folderId: int | None = None
    labelIds: list[int] = Field(default_factory=list)


class MoveToolRequest(BaseModel):
    folderId: int | None = None


def _load_folders(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT folders.id, folders.name, folder_tree.parent_id
        FROM folders
        JOIN folder_tree ON folder_tree.folder_id = folders.id
        ORDER BY folders.name;
        """
    ).fetchall()
    folder_map: dict[int, dict] = {
        row["id"]: {
            "id": row["id"],
            "name": row["name"],
            "parentId": row["parent_id"],
        }
        for row in rows
    }
    path_cache: dict[int, str] = {}

    def build_path(folder_id: int) -> str:
        if folder_id in path_cache:
            return path_cache[folder_id]
        folder = folder_map.get(folder_id)
        if folder is None:
            return ""
        if folder["parentId"] is None:
            path_cache[folder_id] = folder["name"]
            return folder["name"]
        parent_path = build_path(folder["parentId"])
        path_cache[folder_id] = f"{parent_path} / {folder['name']}"
        return path_cache[folder_id]

    for folder_id, folder in folder_map.items():
        folder["path"] = build_path(folder_id)

    return list(folder_map.values())


def _load_labels(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT labels.id, labels.name, label_tree.parent_id
        FROM labels
        JOIN label_tree ON label_tree.label_id = labels.id
        ORDER BY labels.name;
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "parentId": row["parent_id"],
        }
        for row in rows
    ]


def _load_tool_labels(conn: sqlite3.Connection) -> dict[int, list[dict]]:
    rows = conn.execute(
        """
        SELECT tool_labels.tool_id, labels.id, labels.name
        FROM tool_labels
        JOIN labels ON labels.id = tool_labels.label_id
        ORDER BY labels.name;
        """
    ).fetchall()
    labels: dict[int, list[dict]] = {}
    for row in rows:
        labels.setdefault(row["tool_id"], []).append({"id": row["id"], "name": row["name"]})
    return labels


def _serialize_tool(
    row: sqlite3.Row,
    *,
    folder_paths: dict[int, str],
    tool_labels: dict[int, list[dict]],
) -> dict:
    labels = tool_labels.get(row["id"], [])
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"] or "",
        "enabled": bool(row["enabled"]),
        "folderId": row["folder_id"],
        "folderPath": folder_paths.get(row["folder_id"]) or "Unassigned",
        "labels": labels,
        "labelIds": [label["id"] for label in labels],
    }


def _fetch_tool(
    conn: sqlite3.Connection,
    tool_id: int,
    *,
    folder_paths: dict[int, str],
    tool_labels: dict[int, list[dict]],
) -> dict | None:
    row = conn.execute(
        """
        SELECT id, name, description, enabled, folder_id
        FROM tools
        WHERE id = ?;
        """,
        (tool_id,),
    ).fetchone()
    if row is None:
        return None
    return _serialize_tool(row, folder_paths=folder_paths, tool_labels=tool_labels)


def _parse_label_filter(label_ids: str | None) -> list[int]:
    if not label_ids:
        return []
    parsed: list[int] = []
    for label_id in label_ids.split(","):
        if not label_id:
            continue
        parsed.append(int(label_id))
    return parsed


def create_app(
    definitions: list[dict] | None = None,
    *,
    db_path: str | Path = ":memory:",
) -> FastAPI:
    app = FastAPI(title="MCP Admin")
    tool_definitions = DEFAULT_TOOL_DEFS if definitions is None else definitions
    app.state.root = discover_tools(tool_definitions)
    conn = get_connection(db_path, check_same_thread=False)
    apply_migrations(conn)
    app.state.conn = conn

    @app.on_event("shutdown")
    def shutdown() -> None:
        app.state.conn.close()

    def folder_paths() -> dict[int, str]:
        folders = _load_folders(conn)
        return {folder["id"]: folder["path"] for folder in folders}

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/tools")
    def list_tools() -> dict:
        root: ToolNode = app.state.root
        return {"tools": [child.to_dict() for child in root.children]}

    @app.post("/tools/{tool_name}/enable")
    def set_tool_enabled(tool_name: str, request: ToggleRequest) -> dict:
        root: ToolNode = app.state.root
        if not toggle_tool(root, tool_name, request.enabled):
            raise HTTPException(status_code=404, detail="Tool not found")
        return {"name": tool_name, "enabled": request.enabled}

    @app.get("/tools/{tool_name}/labels")
    def tool_labels(tool_name: str) -> dict:
        root: ToolNode = app.state.root
        labels = get_label_path(root, tool_name)
        if not labels:
            raise HTTPException(status_code=404, detail="Tool not found")
        return {"labels": labels}

    @app.get("/api/folders")
    def list_folders() -> list[dict]:
        return _load_folders(conn)

    @app.post("/api/folders")
    def create_folder(request: FolderRequest) -> dict:
        parent_id = request.parentId or 1
        repo = FolderRepository(conn)
        try:
            folder_id = repo.create(request.name, parent_id)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail="Parent folder not found") from exc
        row = repo.get(folder_id)
        if row is None:
            raise HTTPException(status_code=500, detail="Folder creation failed")
        return {
            "id": row["id"],
            "name": row["name"],
            "parentId": row["parent_id"],
        }

    @app.put("/api/folders/{folder_id}")
    def update_folder(folder_id: int, request: FolderRequest) -> dict:
        repo = FolderRepository(conn)
        row = repo.get(folder_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Folder not found")
        repo.update(folder_id, request.name)
        if request.parentId is not None and request.parentId != row["parent_id"]:
            try:
                repo.move(folder_id, request.parentId)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except sqlite3.IntegrityError as exc:
                raise HTTPException(status_code=400, detail="Parent folder not found") from exc
        updated = repo.get(folder_id)
        return {
            "id": updated["id"],
            "name": updated["name"],
            "parentId": updated["parent_id"],
        }

    @app.delete("/api/folders/{folder_id}", response_class=Response, status_code=204)
    def delete_folder(folder_id: int) -> Response:
        repo = FolderRepository(conn)
        row = repo.get(folder_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Folder not found")
        try:
            repo.delete(folder_id)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail="Cannot delete root folder") from exc
        return Response(status_code=204)

    @app.get("/api/labels")
    def list_labels() -> list[dict]:
        return _load_labels(conn)

    @app.post("/api/labels")
    def create_label(request: LabelRequest) -> dict:
        parent_id = request.parentId or 1
        repo = LabelRepository(conn)
        try:
            label_id = repo.create(request.name, parent_id)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail="Parent label not found") from exc
        row = repo.get(label_id)
        if row is None:
            raise HTTPException(status_code=500, detail="Label creation failed")
        return {
            "id": row["id"],
            "name": row["name"],
            "parentId": row["parent_id"],
        }

    @app.put("/api/labels/{label_id}")
    def update_label(label_id: int, request: LabelRequest) -> dict:
        repo = LabelRepository(conn)
        row = repo.get(label_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Label not found")
        repo.update(label_id, request.name)
        if request.parentId is not None and request.parentId != row["parent_id"]:
            try:
                repo.move(label_id, request.parentId)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except sqlite3.IntegrityError as exc:
                raise HTTPException(status_code=400, detail="Parent label not found") from exc
        updated = repo.get(label_id)
        return {
            "id": updated["id"],
            "name": updated["name"],
            "parentId": updated["parent_id"],
        }

    @app.delete("/api/labels/{label_id}", response_class=Response, status_code=204)
    def delete_label(label_id: int) -> Response:
        repo = LabelRepository(conn)
        row = repo.get(label_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Label not found")
        try:
            repo.delete(label_id)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail="Cannot delete root label") from exc
        return Response(status_code=204)

    @app.get("/api/tools")
    def list_admin_tools(
        search: str | None = None,
        folderPath: str | None = None,
        labels: str | None = None,
    ) -> list[dict]:
        tool_rows = conn.execute(
            """
            SELECT id, name, description, enabled, folder_id
            FROM tools
            ORDER BY name;
            """
        ).fetchall()
        folder_paths_map = folder_paths()
        tool_labels = _load_tool_labels(conn)
        tools = [
            _serialize_tool(row, folder_paths=folder_paths_map, tool_labels=tool_labels)
            for row in tool_rows
        ]
        if search:
            lowered = search.lower()
            tools = [
                tool
                for tool in tools
                if lowered in tool["name"].lower() or lowered in tool.get("description", "").lower()
            ]
        if folderPath:
            lowered = folderPath.lower()
            tools = [tool for tool in tools if lowered in (tool.get("folderPath") or "").lower()]
        try:
            label_filter = set(_parse_label_filter(labels))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid label filter") from exc
        if label_filter:
            tools = [
                tool
                for tool in tools
                if label_filter.intersection({int(label_id) for label_id in tool["labelIds"]})
            ]
        return tools

    @app.post("/api/tools")
    def create_tool(request: ToolRequest) -> dict:
        repo = ToolRepository(conn)
        folder_id = request.folderId or 1
        try:
            tool_id = repo.create(
                request.name,
                folder_id,
                description=request.description,
                enabled=request.enabled,
            )
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail="Folder not found") from exc
        conn.execute("DELETE FROM tool_labels WHERE tool_id = ?;", (tool_id,))
        for label_id in request.labelIds:
            repo.add_label(tool_id, int(label_id))
        conn.commit()
        tool_labels = _load_tool_labels(conn)
        tool = _fetch_tool(
            conn,
            tool_id,
            folder_paths=folder_paths(),
            tool_labels=tool_labels,
        )
        if tool is None:
            raise HTTPException(status_code=500, detail="Tool creation failed")
        return tool

    @app.put("/api/tools/{tool_id}")
    def update_tool(tool_id: int, request: ToolRequest) -> dict:
        repo = ToolRepository(conn)
        row = repo.get(tool_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Tool not found")
        try:
            repo.update(
                tool_id,
                request.name,
                description=request.description,
                enabled=request.enabled,
                folder_id=request.folderId or row["folder_id"],
            )
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail="Folder not found") from exc
        conn.execute("DELETE FROM tool_labels WHERE tool_id = ?;", (tool_id,))
        for label_id in request.labelIds:
            repo.add_label(tool_id, int(label_id))
        conn.commit()
        tool_labels = _load_tool_labels(conn)
        tool = _fetch_tool(
            conn,
            tool_id,
            folder_paths=folder_paths(),
            tool_labels=tool_labels,
        )
        if tool is None:
            raise HTTPException(status_code=500, detail="Tool update failed")
        return tool

    @app.delete("/api/tools/{tool_id}", response_class=Response, status_code=204)
    def delete_tool(tool_id: int) -> Response:
        repo = ToolRepository(conn)
        row = repo.get(tool_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Tool not found")
        repo.delete(tool_id)
        return Response(status_code=204)

    @app.post("/api/tools/{tool_id}/move")
    def move_tool(tool_id: int, request: MoveToolRequest) -> dict:
        repo = ToolRepository(conn)
        row = repo.get(tool_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Tool not found")
        try:
            repo.move(tool_id, request.folderId or 1)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=400, detail="Folder not found") from exc
        tool_labels = _load_tool_labels(conn)
        tool = _fetch_tool(
            conn,
            tool_id,
            folder_paths=folder_paths(),
            tool_labels=tool_labels,
        )
        if tool is None:
            raise HTTPException(status_code=500, detail="Tool move failed")
        return tool

    return app


app = create_app()
