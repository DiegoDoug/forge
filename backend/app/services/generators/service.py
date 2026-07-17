"""Cryptographically secure value generators. Every function uses the
``secrets``/``os.urandom`` CSPRNG — never ``random``."""

from __future__ import annotations

import base64
import math
import os
import secrets
import time
import uuid

from app.core.errors import AppError

AMBIGUOUS = "Il1O0"
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWER = "abcdefghijklmnopqrstuvwxyz"
DIGITS = "0123456789"
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?/"

NANOID_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"


def generate_password(
    length: int = 20,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    if not 4 <= length <= 256:
        raise AppError("Password length must be between 4 and 256")

    pools = []
    if use_upper:
        pools.append(UPPER)
    if use_lower:
        pools.append(LOWER)
    if use_digits:
        pools.append(DIGITS)
    if use_symbols:
        pools.append(SYMBOLS)
    if not pools:
        raise AppError("Select at least one character set")

    if exclude_ambiguous:
        pools = ["".join(c for c in pool if c not in AMBIGUOUS) for pool in pools]

    alphabet = "".join(pools)
    # Guarantee at least one character from each selected pool.
    required = [secrets.choice(pool) for pool in pools]
    remaining = [secrets.choice(alphabet) for _ in range(length - len(required))]
    chars = required + remaining
    secrets_rng = secrets.SystemRandom()
    secrets_rng.shuffle(chars)
    return "".join(chars)


def generate_uuid4() -> str:
    return str(uuid.uuid4())


def generate_uuid7() -> str:
    unix_ts_ms = int(time.time() * 1000)
    ts_bytes = unix_ts_ms.to_bytes(6, "big")
    rand_bytes = os.urandom(10)
    b = bytearray(ts_bytes + rand_bytes)
    b[6] = (b[6] & 0x0F) | 0x70  # version 7
    b[8] = (b[8] & 0x3F) | 0x80  # RFC 4122 variant
    return str(uuid.UUID(bytes=bytes(b)))


def generate_nanoid(size: int = 21, alphabet: str = NANOID_ALPHABET) -> str:
    if not 1 <= size <= 512:
        raise AppError("NanoID size must be between 1 and 512")
    if len(alphabet) < 2:
        raise AppError("Alphabet must contain at least 2 characters")
    return "".join(secrets.choice(alphabet) for _ in range(size))


def generate_random_bytes(length: int = 32, encoding: str = "hex") -> str:
    if not 1 <= length <= 4096:
        raise AppError("Byte length must be between 1 and 4096")
    raw = secrets.token_bytes(length)
    if encoding == "hex":
        return raw.hex()
    if encoding == "base64":
        return base64.b64encode(raw).decode("ascii")
    if encoding == "base64url":
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    raise AppError("encoding must be one of: hex, base64, base64url")


def generate_api_key(prefix: str = "forge") -> str:
    safe_prefix = "".join(c for c in prefix if c.isalnum() or c in "-_")[:20] or "key"
    return f"{safe_prefix}_{secrets.token_urlsafe(32)}"


def generate_jwt_secret(length: int = 64) -> str:
    return generate_random_bytes(length, "base64url")


def estimate_entropy(value: str) -> dict:
    if not value:
        return {"bits": 0.0, "strength": "empty", "pool_size": 0}

    pool_size = 0
    if any(c in UPPER for c in value):
        pool_size += len(UPPER)
    if any(c in LOWER for c in value):
        pool_size += len(LOWER)
    if any(c in DIGITS for c in value):
        pool_size += len(DIGITS)
    if any(c in SYMBOLS for c in value):
        pool_size += len(SYMBOLS)
    other = set(value) - set(UPPER + LOWER + DIGITS + SYMBOLS)
    if other:
        pool_size += len(other)

    bits = len(value) * math.log2(max(pool_size, 1))
    if bits < 28:
        strength = "very weak"
    elif bits < 36:
        strength = "weak"
    elif bits < 60:
        strength = "reasonable"
    elif bits < 128:
        strength = "strong"
    else:
        strength = "very strong"

    return {"bits": round(bits, 1), "strength": strength, "pool_size": pool_size}
