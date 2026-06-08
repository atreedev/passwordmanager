from pathlib import Path
from core.crypto import encrypt, decrypt, derive_key

BASE   = Path(__file__).parent.parent / "data"
VAULT  = BASE / "vault"
DECOY  = BASE / "decoy"

SENTINEL = "UNLOCKED"


def _path(vault_dir: Path, service: str) -> Path:
    return vault_dir / f"{service}.enc"


def write_sentinel(vault_dir: Path, key: bytes):
    vault_dir.mkdir(parents=True, exist_ok=True)
    ciphertext, nonce = encrypt(SENTINEL, key)
    (vault_dir / "sentinel.enc").write_bytes(nonce + ciphertext)


def try_unlock(vault_dir: Path, key: bytes) -> bool:
    sentinel = vault_dir / "sentinel.enc"
    if not sentinel.exists():
        return False
    try:
        raw = sentinel.read_bytes()
        return decrypt(raw[12:], raw[:12], key) == SENTINEL
    except Exception:
        return False


def resolve_vault(pin: str, vault_salt: bytes, decoy_salt: bytes):
    vault_key = derive_key(pin, vault_salt)
    if try_unlock(VAULT, vault_key):
        return VAULT, vault_key

    decoy_key = derive_key(pin, decoy_salt)
    if try_unlock(DECOY, decoy_key):
        return DECOY, decoy_key

    return None, None


def write_entry(vault_dir: Path, service: str, data: str, key: bytes):
    vault_dir.mkdir(parents=True, exist_ok=True)
    ciphertext, nonce = encrypt(data, key)
    _path(vault_dir, service).write_bytes(nonce + ciphertext)


def read_entry(vault_dir: Path, service: str, key: bytes) -> str:
    raw = _path(vault_dir, service).read_bytes()
    return decrypt(raw[12:], raw[:12], key)


def list_entries(vault_dir: Path) -> list[str]:
    if not vault_dir.exists():
        return []
    return [f.stem for f in vault_dir.glob("*.enc") if f.stem != "sentinel"]


def delete_entry(vault_dir: Path, service: str):
    p = _path(vault_dir, service)
    if p.exists():
        p.unlink()