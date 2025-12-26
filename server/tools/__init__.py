from server.tools.gmail import tool_metadata as gmail_metadata


def all_tool_metadata() -> list[dict]:
    """Tool implementations for MCP server."""
    return gmail_metadata()
