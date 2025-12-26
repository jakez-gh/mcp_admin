import importlib
from pathlib import Path

import pytest

from server import config, storage
from server.tools.gmail import tool_metadata

pytest.importorskip("cryptography")
Fernet = importlib.import_module("cryptography.fernet").Fernet


def test_tool_metadata_includes_token_status(tmp_path: Path) -> None:
    config.DB_PATH = str(tmp_path / "tools.sqlite")
    config.GMAIL_TOKEN_ENCRYPTION_KEY = Fernet.generate_key().decode("utf-8")

    storage.init_db()
    metadata = tool_metadata()

    assert metadata[0]["token_status"] == "disconnected"
    assert metadata[1]["token_status"] == "disconnected"
