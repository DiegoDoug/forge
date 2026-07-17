from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthDep
from app.schemas.generators import (
    ApiKeyGenerateIn,
    EntropyEstimateIn,
    EntropyOut,
    GeneratedValueOut,
    JwtSecretGenerateIn,
    NanoIdGenerateIn,
    PasswordGenerateIn,
    RandomBytesGenerateIn,
)
from app.services.generators import service

router = APIRouter(prefix="/generators", tags=["generators"], dependencies=[AuthDep])


@router.post("/password", response_model=GeneratedValueOut)
async def password(body: PasswordGenerateIn) -> GeneratedValueOut:
    return GeneratedValueOut(
        value=service.generate_password(
            body.length, body.use_upper, body.use_lower, body.use_digits, body.use_symbols, body.exclude_ambiguous
        )
    )


@router.post("/uuid4", response_model=GeneratedValueOut)
async def uuid4() -> GeneratedValueOut:
    return GeneratedValueOut(value=service.generate_uuid4())


@router.post("/uuid7", response_model=GeneratedValueOut)
async def uuid7() -> GeneratedValueOut:
    return GeneratedValueOut(value=service.generate_uuid7())


@router.post("/nanoid", response_model=GeneratedValueOut)
async def nanoid(body: NanoIdGenerateIn) -> GeneratedValueOut:
    kwargs = {"size": body.size}
    if body.alphabet:
        kwargs["alphabet"] = body.alphabet
    return GeneratedValueOut(value=service.generate_nanoid(**kwargs))


@router.post("/random-bytes", response_model=GeneratedValueOut)
async def random_bytes(body: RandomBytesGenerateIn) -> GeneratedValueOut:
    return GeneratedValueOut(value=service.generate_random_bytes(body.length, body.encoding))


@router.post("/api-key", response_model=GeneratedValueOut)
async def api_key(body: ApiKeyGenerateIn) -> GeneratedValueOut:
    return GeneratedValueOut(value=service.generate_api_key(body.prefix))


@router.post("/jwt-secret", response_model=GeneratedValueOut)
async def jwt_secret(body: JwtSecretGenerateIn) -> GeneratedValueOut:
    return GeneratedValueOut(value=service.generate_jwt_secret(body.length))


@router.post("/entropy", response_model=EntropyOut)
async def entropy(body: EntropyEstimateIn) -> EntropyOut:
    return EntropyOut(**service.estimate_entropy(body.value))
