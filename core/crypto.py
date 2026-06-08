import os
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_salt() -> bytes:
    return os.urandom(16)


def derive_key(pin: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=pin.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=Type.ID
    )


def encrypt(data: str, key: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce, data.encode(), None)
    return ciphertext, nonce


def decrypt(ciphertext: bytes, nonce: bytes, key: bytes) -> str:
    return AESGCM(key).decrypt(nonce, ciphertext, None).decode()
