import sqlite3
from pathlib import Path
from typing import Iterable

BASE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = BASE_DIR / "migrations"


def get_connection(path: str | Path = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _ensure_schema_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY
        );
        """
    )


def _applied_migrations(conn: sqlite3.Connection) -> set[str]:
    _ensure_schema_table(conn)
    rows = conn.execute("SELECT version FROM schema_migrations;").fetchall()
    return {row["version"] for row in rows}


def _migration_files() -> Iterable[Path]:
    if not MIGRATIONS_DIR.exists():
        return []
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def apply_migrations(conn: sqlite3.Connection) -> None:
    applied = _applied_migrations(conn)
    for migration in _migration_files():
        if migration.name in applied:
            continue
        sql = migration.read_text()
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_migrations (version) VALUES (?);",
            (migration.name,),
        )
    conn.commit()
