"""Tool implementations for MCP server."""

from server.tools.gmail import tool_metadata as gmail_metadata


def all_tool_metadata() -> list[dict]:
    return gmail_metadata()
