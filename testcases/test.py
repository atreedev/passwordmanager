import sys
sys.path.append('..')

from core.crypto import generate_salt, derive_key, encrypt, decrypt

salt = generate_salt()
key = derive_key("101010", salt)

ciphertext, nonce = encrypt("gmail@example.com | hunter2", key)
print("Encrypted:", ciphertext.hex())

result = decrypt(ciphertext, nonce, key)
print("Decrypted:", result)

wrong_key = derive_key("999999", salt)
try:
    decrypt(ciphertext, nonce, wrong_key)
    print("FAIL: wrong key should not decrypt")
except Exception:
    print("PASS: wrong key correctly rejected")


from pathlib import Path
from core.vault import (
    write_sentinel, try_unlock, resolve_vault,
    write_entry, read_entry, list_entries, delete_entry,
    VAULT, DECOY
)

print("\n--- Vault Tests ---")

vault_salt = generate_salt()
decoy_salt = generate_salt()

real_key  = derive_key("010101", vault_salt)
fake_key  = derive_key("101010", decoy_salt)

write_sentinel(VAULT, real_key)
write_sentinel(DECOY, fake_key)

assert try_unlock(VAULT, real_key),  "FAIL: real key should unlock vault"
assert not try_unlock(VAULT, fake_key), "FAIL: fake key should not unlock vault"
print("PASS: sentinel unlock logic correct")

vault_dir, key = resolve_vault("010101", vault_salt, decoy_salt)
assert vault_dir == VAULT
print("PASS: real pin routes to vault/")

vault_dir, key = resolve_vault("101010", vault_salt, decoy_salt)
assert vault_dir == DECOY
print("PASS: fake pin routes to decoy/")

vault_dir, key = resolve_vault("010101", vault_salt, decoy_salt)
write_entry(vault_dir, "gmail", "test@gmail.com | pass123", key)
result = read_entry(vault_dir, "gmail", key)
assert result == "test@gmail.com | pass123"
print("PASS: write and read entry correct")

entries = list_entries(vault_dir)
assert "gmail" in entries
assert "sentinel" not in entries
print("PASS: list_entries excludes sentinel")

delete_entry(vault_dir, "gmail")
assert not (vault_dir / "gmail.enc").exists()
print("PASS: delete entry works")