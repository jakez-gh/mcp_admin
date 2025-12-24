import sqlite3
from typing import List, Optional

from server import config
from server.crypto import decrypt, encrypt


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS gmail_tokens (
    email TEXT PRIMARY KEY,
    refresh_token_encrypted TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class TokenRecord:
    def __init__(self, email: str, has_token: bool) -> None:
        self.email = email
        self.has_token = has_token

    def to_dict(self) -> dict:
        return {"email": self.email, "has_token": self.has_token}



def init_db() -> None:
    with sqlite3.connect(config.DB_PATH) as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()



def store_refresh_token(email: str, refresh_token: str) -> None:
    encrypted = encrypt(refresh_token)
    with sqlite3.connect(config.DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO gmail_tokens (email, refresh_token_encrypted)
            VALUES (?, ?)
            ON CONFLICT(email)
            DO UPDATE SET refresh_token_encrypted = excluded.refresh_token_encrypted,
                          updated_at = CURRENT_TIMESTAMP
            """,
            (email, encrypted),
        )
        conn.commit()



def list_accounts() -> List[TokenRecord]:
    with sqlite3.connect(config.DB_PATH) as conn:
        rows = conn.execute("SELECT email, refresh_token_encrypted FROM gmail_tokens").fetchall()
    return [TokenRecord(email=row[0], has_token=bool(row[1])) for row in rows]



def get_refresh_token(email: str) -> Optional[str]:
    with sqlite3.connect(config.DB_PATH) as conn:
        row = conn.execute(
            "SELECT refresh_token_encrypted FROM gmail_tokens WHERE email = ?",
            (email,),
        ).fetchone()
    if not row or not row[0]:
        return None
    return decrypt(row[0])



def token_status() -> str:
    accounts = list_accounts()
    if not accounts:
        return "disconnected"
    if any(account.has_token for account in accounts):
        return "connected"
    return "disconnected"
