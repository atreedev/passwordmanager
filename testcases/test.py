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
