from pathlib import Path

import pytest

cryptography = pytest.importorskip("cryptography")
from cryptography.fernet import Fernet  # noqa: E402

from server import config, storage  # noqa: E402
from server.tools.gmail import tool_metadata  # noqa: E402


def test_tool_metadata_includes_token_status(tmp_path: Path) -> None:
    config.DB_PATH = str(tmp_path / "tools.sqlite")
    config.GMAIL_TOKEN_ENCRYPTION_KEY = Fernet.generate_key().decode("utf-8")

    storage.init_db()
    metadata = tool_metadata()

    assert metadata[0]["token_status"] == "disconnected"
    assert metadata[1]["token_status"] == "disconnected"
