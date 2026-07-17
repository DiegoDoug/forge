"""Base64, hashing, AES-256-GCM, RSA, ECDSA, and JWT tools.

These are user-facing developer utilities, distinct from ``app.core.security``
which protects the vault at rest — nothing here touches the master key.
"""

from __future__ import annotations

import base64
import hashlib
import secrets as pysecrets
from datetime import datetime, timedelta, timezone

import jwt as pyjwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.errors import AppError

HASH_ALGORITHMS = {"md5", "sha1", "sha256", "sha384", "sha512", "blake2b", "blake2s"}
JWT_ALGORITHMS = {"HS256", "HS384", "HS512"}

# --- Base64 ------------------------------------------------------------


def base64_encode(text: str, url_safe: bool = False) -> str:
    raw = text.encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw) if url_safe else base64.b64encode(raw)
    return encoded.decode("ascii")


def base64_decode(text: str, url_safe: bool = False) -> str:
    try:
        decoder = base64.urlsafe_b64decode if url_safe else base64.b64decode
        padded = text + "=" * (-len(text) % 4)
        return decoder(padded).decode("utf-8")
    except Exception as exc:
        raise AppError(f"Invalid base64 input: {exc}") from exc


# --- Hashing -------------------------------------------------------------


def hash_text(text: str, algorithm: str = "sha256") -> str:
    if algorithm not in HASH_ALGORITHMS:
        raise AppError(f"Unsupported hash algorithm. Choose one of: {', '.join(sorted(HASH_ALGORITHMS))}")
    return hashlib.new(algorithm, text.encode("utf-8")).hexdigest()


def verify_hash(text: str, algorithm: str, expected_hex: str) -> bool:
    return pysecrets.compare_digest(hash_text(text, algorithm), expected_hex.lower().strip())


# --- AES-256-GCM (passphrase stretched via PBKDF2-SHA256) --------------


def _derive_aes_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=310_000)
    return kdf.derive(passphrase.encode("utf-8"))


def aes_encrypt(plaintext: str, passphrase: str) -> dict:
    salt = pysecrets.token_bytes(16)
    nonce = pysecrets.token_bytes(12)
    key = _derive_aes_key(passphrase, salt)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
    return {
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "salt": base64.b64encode(salt).decode("ascii"),
    }


def aes_decrypt(ciphertext_b64: str, nonce_b64: str, salt_b64: str, passphrase: str) -> str:
    try:
        salt = base64.b64decode(salt_b64)
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        key = _derive_aes_key(passphrase, salt)
        return AESGCM(key).decrypt(nonce, ciphertext, None).decode("utf-8")
    except Exception as exc:
        raise AppError("Decryption failed: wrong passphrase or corrupted data") from exc


# --- JWT -----------------------------------------------------------------


def jwt_decode_unverified(token: str) -> dict:
    try:
        header = pyjwt.get_unverified_header(token)
        payload = pyjwt.decode(token, options={"verify_signature": False})
    except Exception as exc:
        raise AppError(f"Invalid JWT: {exc}") from exc
    return {"header": header, "payload": payload}


def jwt_verify(token: str, secret: str, algorithm: str = "HS256") -> dict:
    if algorithm not in JWT_ALGORITHMS:
        raise AppError(f"Unsupported JWT algorithm. Choose one of: {', '.join(sorted(JWT_ALGORITHMS))}")
    try:
        payload = pyjwt.decode(token, secret, algorithms=[algorithm])
        return {"valid": True, "payload": payload, "error": None}
    except pyjwt.InvalidTokenError as exc:
        return {"valid": False, "payload": None, "error": str(exc)}


def jwt_build(payload: dict, secret: str, algorithm: str = "HS256", expires_in_seconds: int | None = None) -> str:
    if algorithm not in JWT_ALGORITHMS:
        raise AppError(f"Unsupported JWT algorithm. Choose one of: {', '.join(sorted(JWT_ALGORITHMS))}")
    claims = dict(payload)
    if expires_in_seconds:
        claims["exp"] = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
    return pyjwt.encode(claims, secret, algorithm=algorithm)


# --- RSA (OAEP encryption) ----------------------------------------------


def rsa_generate_keypair(key_size: int = 2048) -> dict:
    if key_size not in (2048, 3072, 4096):
        raise AppError("RSA key size must be 2048, 3072, or 4096")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return {"private_key": private_pem.decode(), "public_key": public_pem.decode()}


def rsa_encrypt(public_pem: str, plaintext: str) -> str:
    try:
        public_key = serialization.load_pem_public_key(public_pem.encode())
        ciphertext = public_key.encrypt(
            plaintext.encode("utf-8"),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )
        return base64.b64encode(ciphertext).decode("ascii")
    except Exception as exc:
        raise AppError(f"RSA encryption failed: {exc}") from exc


def rsa_decrypt(private_pem: str, ciphertext_b64: str) -> str:
    try:
        private_key = serialization.load_pem_private_key(private_pem.encode(), password=None)
        plaintext = private_key.decrypt(
            base64.b64decode(ciphertext_b64),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )
        return plaintext.decode("utf-8")
    except Exception as exc:
        raise AppError(f"RSA decryption failed: {exc}") from exc


# --- ECDSA (P-256 sign/verify) ------------------------------------------


def ecc_generate_keypair() -> dict:
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return {"private_key": private_pem.decode(), "public_key": public_pem.decode()}


def ecc_sign(private_pem: str, message: str) -> str:
    try:
        private_key = serialization.load_pem_private_key(private_pem.encode(), password=None)
        signature = private_key.sign(message.encode("utf-8"), ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(signature).decode("ascii")
    except Exception as exc:
        raise AppError(f"ECDSA signing failed: {exc}") from exc


def ecc_verify(public_pem: str, message: str, signature_b64: str) -> bool:
    try:
        public_key = serialization.load_pem_public_key(public_pem.encode())
        public_key.verify(base64.b64decode(signature_b64), message.encode("utf-8"), ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False
