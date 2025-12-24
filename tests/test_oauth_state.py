import base64

import pytest

cryptography = pytest.importorskip("cryptography")
from cryptography.fernet import Fernet

from server import config
from server import oauth


def test_state_round_trip() -> None:
    config.GMAIL_TOKEN_ENCRYPTION_KEY = Fernet.generate_key().decode("utf-8")
    state = oauth.generate_state()
    assert oauth.verify_state(state) is True


def test_state_invalid() -> None:
    config.GMAIL_TOKEN_ENCRYPTION_KEY = Fernet.generate_key().decode("utf-8")
    bad_state = base64.urlsafe_b64encode(b"invalid").decode("utf-8")
    assert oauth.verify_state(bad_state) is False
