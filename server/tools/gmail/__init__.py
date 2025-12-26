from server.tools.gmail.archive_message import archive_message
from server.tools.gmail.archive_message import metadata as archive_metadata
from server.tools.gmail.list_authenticated_accounts import (
    list_authenticated_accounts,
)
from server.tools.gmail.list_authenticated_accounts import (
    metadata as list_metadata,
)

TOOLS = {
    "archive_message": archive_message,
    "list_authenticated_accounts": list_authenticated_accounts,
}


def tool_metadata() -> list[dict]:
    return [archive_metadata(), list_metadata()]
