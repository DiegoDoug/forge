"""Encryption at rest, master-password hashing, and session tokens.

Two distinct secrets are in play:

- ``FORGE_MASTER_KEY`` (operator-supplied, env/Docker secret): stretched into
  a 32-byte symmetric key via BLAKE2b and used with PyNaCl's SecretBox to
  encrypt vault secrets at rest, and to sign session tokens. It never leaves
  the server process and is never stored in the database.
- The **master password** (user-supplied, set on first run): gates access to
  the UI/API for this single-user instance. Only its Argon2id hash is
  persisted, via PyNaCl's ``pwhash``.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from functools import lru_cache

import nacl.exceptions
import nacl.pwhash
import nacl.secret
import nacl.utils

from .config import get_settings


def _derive_key(secret: str) -> bytes:
    return hashlib.blake2b(secret.encode("utf-8"), digest_size=nacl.secret.SecretBox.KEY_SIZE).digest()


@lru_cache
def _root_key() -> bytes:
    return _derive_key(get_settings().resolved_master_key)


class VaultCrypto:
    """Encrypts/decrypts bytes at rest using the server's root key."""

    def __init__(self) -> None:
        self._box = nacl.secret.SecretBox(_root_key())

    def encrypt(self, plaintext: bytes) -> bytes:
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        return self._box.encrypt(plaintext, nonce)

    def decrypt(self, blob: bytes) -> bytes:
        return self._box.decrypt(blob)

    def encrypt_str(self, plaintext: str) -> bytes:
        return self.encrypt(plaintext.encode("utf-8"))

    def decrypt_str(self, blob: bytes) -> str:
        return self.decrypt(blob).decode("utf-8")


@lru_cache
def get_vault_crypto() -> VaultCrypto:
    return VaultCrypto()


# --- Master password hashing (Argon2id via libsodium) -----------------------


def hash_master_password(password: str) -> str:
    return nacl.pwhash.argon2id.str(password.encode("utf-8")).decode("ascii")


def verify_master_password(password: str, password_hash: str) -> bool:
    try:
        return nacl.pwhash.verify(password_hash.encode("ascii"), password.encode("utf-8"))
    except nacl.exceptions.InvalidkeyError:
        return False


# --- Session tokens -----------------------------------------------------
# Simple HMAC-signed, server-verified opaque token: "<expiry>.<hmac>". There
# is exactly one user, so the token carries no identity, only a validity
# window. Stateless (no server-side session table) since revocation only
# ever needs to invalidate everything, which changing the master password
# already achieves (it changes the HMAC key material's source string).


def _session_secret(password_hash: str) -> bytes:
    return hashlib.blake2b(
        _root_key() + password_hash.encode("utf-8"), digest_size=32
    ).digest()


def issue_session_token(password_hash: str, ttl_minutes: int) -> str:
    expiry = int(time.time()) + ttl_minutes * 60
    payload = str(expiry).encode("utf-8")
    sig = hmac.new(_session_secret(password_hash), payload, hashlib.sha256).hexdigest()
    return f"{expiry}.{sig}"


def verify_session_token(token: str, password_hash: str) -> bool:
    try:
        expiry_str, sig = token.split(".", 1)
        expiry = int(expiry_str)
    except (ValueError, AttributeError):
        return False
    if expiry < int(time.time()):
        return False
    expected = hmac.new(_session_secret(password_hash), expiry_str.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)

