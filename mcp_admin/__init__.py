"""Administration and serving of MCP tools."""

from typing import Any

from .db import apply_migrations, get_connection


def create_app(*args: Any, **kwargs: Any):
    from mcp_admin.api import create_app as _create_app

    return _create_app(*args, **kwargs)

__all__ = ["get_connection", "apply_migrations", "create_app"]
"""Core package for MCP admin tooling."""
