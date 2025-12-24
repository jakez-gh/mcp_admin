"""Core package for MCP admin tooling."""

from typing import Any


def create_app(*args: Any, **kwargs: Any):
    from mcp_admin.api import create_app as _create_app

    return _create_app(*args, **kwargs)


__all__ = ["create_app"]
