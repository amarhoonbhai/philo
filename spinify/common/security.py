import os
from typing import Optional

# Optional Fernet-like very-light wrapper (no external deps to keep it simple).
# If you want real Fernet, install `cryptography` and replace these with Fernet.
# For now we do XOR with ENV key (not bulletproof, but better than plain text).
# Set ENCRYPT_KEY to a random long string.

KEY = os.getenv("ENCRYPT_KEY", "")

def _xor(data: bytes, key: bytes) -> bytes:
    if not key: return data
    k = key * (len(data) // len(key) + 1)
    return bytes([a ^ b for a, b in zip(data, k[:len(data)])])

def encrypt_text(txt: str) -> str:
    return _xor(txt.encode("utf-8"), KEY.encode("utf-8")).hex()

def decrypt_text(hex_txt: str) -> str:
    try:
        raw = bytes.fromhex(hex_txt)
        return _xor(raw, KEY.encode("utf-8")).decode("utf-8")
    except Exception:
        # fallback: maybe it was stored plain
        return hex_txt
