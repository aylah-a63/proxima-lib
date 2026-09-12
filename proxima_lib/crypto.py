import os
import keyring
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"PRXM"
_VERSION = b"\x01"
_SERVICE = "proxima"
_KEY_ENTRY = "persona-key"


def _get_or_create_key() -> bytes:
    stored = keyring.get_password(_SERVICE, _KEY_ENTRY)
    if stored:
        return bytes.fromhex(stored)
    key = os.urandom(32)
    keyring.set_password(_SERVICE, _KEY_ENTRY, key.hex())
    return key


def encrypt_per(plaintext: bytes) -> bytes:
    key = _get_or_create_key()
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext, None)
    return MAGIC + _VERSION + nonce + ct


def decrypt_per(data: bytes) -> bytes:
    if data[:4] != MAGIC:
        raise ValueError("Not an encrypted proxima persona file")
    if data[4:5] != _VERSION:
        raise ValueError(f"Unsupported persona file version: {data[4]}")
    key = _get_or_create_key()
    nonce = data[5:17]
    ct = data[17:]
    return AESGCM(key).decrypt(nonce, ct, None)
