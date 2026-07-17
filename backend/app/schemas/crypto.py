from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Base64In(BaseModel):
    text: str
    url_safe: bool = False


class TextOut(BaseModel):
    text: str


class HashIn(BaseModel):
    text: str
    algorithm: str = "sha256"


class HashOut(BaseModel):
    digest: str


class VerifyHashIn(BaseModel):
    text: str
    algorithm: str = "sha256"
    expected: str


class VerifyOut(BaseModel):
    valid: bool


class AesEncryptIn(BaseModel):
    plaintext: str
    passphrase: str = Field(min_length=1)


class AesEncryptOut(BaseModel):
    ciphertext: str
    nonce: str
    salt: str


class AesDecryptIn(BaseModel):
    ciphertext: str
    nonce: str
    salt: str
    passphrase: str


class JwtDecodeIn(BaseModel):
    token: str


class JwtDecodeOut(BaseModel):
    header: dict[str, Any]
    payload: dict[str, Any]


class JwtVerifyIn(BaseModel):
    token: str
    secret: str
    algorithm: str = "HS256"


class JwtVerifyOut(BaseModel):
    valid: bool
    payload: dict[str, Any] | None
    error: str | None = None


class JwtBuildIn(BaseModel):
    payload: dict[str, Any]
    secret: str
    algorithm: str = "HS256"
    expires_in_seconds: int | None = None


class RsaKeypairIn(BaseModel):
    key_size: int = 2048


class KeypairOut(BaseModel):
    private_key: str
    public_key: str


class RsaEncryptIn(BaseModel):
    public_key: str
    plaintext: str


class RsaDecryptIn(BaseModel):
    private_key: str
    ciphertext: str


class EccSignIn(BaseModel):
    private_key: str
    message: str


class EccVerifyIn(BaseModel):
    public_key: str
    message: str
    signature: str
