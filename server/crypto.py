from cryptography.fernet import Fernet

from server import config


def get_fernet() -> Fernet:
    if not config.GMAIL_TOKEN_ENCRYPTION_KEY:
        raise RuntimeError("GMAIL_TOKEN_ENCRYPTION_KEY is not set")
    return Fernet(config.GMAIL_TOKEN_ENCRYPTION_KEY)


def encrypt(value: str) -> str:
    fernet = get_fernet()
    return fernet.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt(value: str) -> str:
    fernet = get_fernet()
    return fernet.decrypt(value.encode("utf-8")).decode("utf-8")
