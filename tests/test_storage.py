from pathlib import Path

from cryptography.fernet import Fernet

from server import config, storage


def test_store_and_fetch_refresh_token(tmp_path: Path) -> None:
    config.DB_PATH = str(tmp_path / "tokens.sqlite")
    config.GMAIL_TOKEN_ENCRYPTION_KEY = Fernet.generate_key().decode("utf-8")

    storage.init_db()
    storage.store_refresh_token("user@example.com", "refresh-token")

    token = storage.get_refresh_token("user@example.com")
    assert token == "refresh-token"


def test_list_accounts(tmp_path: Path) -> None:
    config.DB_PATH = str(tmp_path / "accounts.sqlite")
    config.GMAIL_TOKEN_ENCRYPTION_KEY = Fernet.generate_key().decode("utf-8")

    storage.init_db()
    storage.store_refresh_token("user@example.com", "refresh-token")

    accounts = storage.list_accounts()
    assert accounts[0].email == "user@example.com"
    assert accounts[0].has_token is True
