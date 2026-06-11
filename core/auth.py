import os
import sqlite3
import bcrypt
import win32security
import win32con
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "config.db"


def _connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB)


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key   TEXT PRIMARY KEY,
                value BLOB
            )
        """)


def _set(key: str, value: bytes):
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (key, value)
        )


def _get(key: str) -> bytes | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM config WHERE key = ?", (key,)
        ).fetchone()
    return row[0] if row else None


def is_first_launch() -> bool:
    return _get("manager_pin_hash") is None


def verify_windows_password(password: str) -> bool:
    username = os.getenv("USERNAME")
    try:
        token = win32security.LogonUser(
            username, None, password,
            win32con.LOGON32_LOGON_INTERACTIVE,
            win32con.LOGON32_PROVIDER_DEFAULT
        )
        token.Close()
        return True
    except Exception:
        return False


def set_manager_pin(pin: str):
    hashed = bcrypt.hashpw(pin.encode(), bcrypt.gensalt())
    _set("manager_pin_hash", hashed)


def verify_manager_pin(pin: str) -> bool:
    stored = _get("manager_pin_hash")
    if stored is None:
        return False
    return bcrypt.checkpw(pin.encode(), stored)


def set_salts(vault_salt: bytes, decoy_salt: bytes):
    _set("vault_salt", vault_salt)
    _set("decoy_salt", decoy_salt)


def get_salts() -> tuple[bytes | None, bytes | None]:
    return _get("vault_salt"), _get("decoy_salt")