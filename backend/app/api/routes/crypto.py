from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep
from app.schemas.crypto import (
    AesDecryptIn,
    AesEncryptIn,
    AesEncryptOut,
    Base64In,
    EccSignIn,
    EccVerifyIn,
    HashIn,
    HashOut,
    JwtBuildIn,
    JwtDecodeIn,
    JwtDecodeOut,
    JwtVerifyIn,
    JwtVerifyOut,
    KeypairOut,
    RsaDecryptIn,
    RsaEncryptIn,
    RsaKeypairIn,
    TextOut,
    VerifyHashIn,
    VerifyOut,
)
from app.services.crypto import service

router = APIRouter(prefix="/crypto", tags=["crypto"], dependencies=[AuthDep])


@router.post("/base64/encode", response_model=TextOut)
async def base64_encode(body: Base64In) -> TextOut:
    return TextOut(text=service.base64_encode(body.text, body.url_safe))


@router.post("/base64/decode", response_model=TextOut)
async def base64_decode(body: Base64In) -> TextOut:
    return TextOut(text=service.base64_decode(body.text, body.url_safe))


@router.post("/hash", response_model=HashOut)
async def hash_text(body: HashIn) -> HashOut:
    return HashOut(digest=service.hash_text(body.text, body.algorithm))


@router.post("/hash/verify", response_model=VerifyOut)
async def verify_hash(body: VerifyHashIn) -> VerifyOut:
    return VerifyOut(valid=service.verify_hash(body.text, body.algorithm, body.expected))


@router.post("/aes/encrypt", response_model=AesEncryptOut)
async def aes_encrypt(body: AesEncryptIn) -> AesEncryptOut:
    return AesEncryptOut(**service.aes_encrypt(body.plaintext, body.passphrase))


@router.post("/aes/decrypt", response_model=TextOut)
async def aes_decrypt(body: AesDecryptIn) -> TextOut:
    return TextOut(text=service.aes_decrypt(body.ciphertext, body.nonce, body.salt, body.passphrase))


@router.post("/jwt/decode", response_model=JwtDecodeOut)
async def jwt_decode(body: JwtDecodeIn) -> JwtDecodeOut:
    return JwtDecodeOut(**service.jwt_decode_unverified(body.token))


@router.post("/jwt/verify", response_model=JwtVerifyOut)
async def jwt_verify(body: JwtVerifyIn) -> JwtVerifyOut:
    return JwtVerifyOut(**service.jwt_verify(body.token, body.secret, body.algorithm))


@router.post("/jwt/build", response_model=TextOut)
async def jwt_build(body: JwtBuildIn) -> TextOut:
    return TextOut(text=service.jwt_build(body.payload, body.secret, body.algorithm, body.expires_in_seconds))


@router.post("/rsa/keypair", response_model=KeypairOut)
async def rsa_keypair(body: RsaKeypairIn) -> KeypairOut:
    return KeypairOut(**service.rsa_generate_keypair(body.key_size))


@router.post("/rsa/encrypt", response_model=TextOut)
async def rsa_encrypt(body: RsaEncryptIn) -> TextOut:
    return TextOut(text=service.rsa_encrypt(body.public_key, body.plaintext))


@router.post("/rsa/decrypt", response_model=TextOut)
async def rsa_decrypt(body: RsaDecryptIn) -> TextOut:
    return TextOut(text=service.rsa_decrypt(body.private_key, body.ciphertext))


@router.post("/ecc/keypair", response_model=KeypairOut)
async def ecc_keypair() -> KeypairOut:
    return KeypairOut(**service.ecc_generate_keypair())


@router.post("/ecc/sign", response_model=TextOut)
async def ecc_sign(body: EccSignIn) -> TextOut:
    return TextOut(text=service.ecc_sign(body.private_key, body.message))


@router.post("/ecc/verify", response_model=VerifyOut)
async def ecc_verify(body: EccVerifyIn) -> VerifyOut:
    return VerifyOut(valid=service.ecc_verify(body.public_key, body.message, body.signature))
