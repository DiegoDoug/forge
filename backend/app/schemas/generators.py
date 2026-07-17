from __future__ import annotations

from pydantic import BaseModel, Field


class PasswordGenerateIn(BaseModel):
    length: int = Field(default=20, ge=4, le=256)
    use_upper: bool = True
    use_lower: bool = True
    use_digits: bool = True
    use_symbols: bool = True
    exclude_ambiguous: bool = False


class NanoIdGenerateIn(BaseModel):
    size: int = Field(default=21, ge=1, le=512)
    alphabet: str | None = None


class RandomBytesGenerateIn(BaseModel):
    length: int = Field(default=32, ge=1, le=4096)
    encoding: str = Field(default="hex", pattern="^(hex|base64|base64url)$")


class ApiKeyGenerateIn(BaseModel):
    prefix: str = Field(default="forge", max_length=20)


class JwtSecretGenerateIn(BaseModel):
    length: int = Field(default=64, ge=16, le=512)


class EntropyEstimateIn(BaseModel):
    value: str = Field(max_length=4096)


class GeneratedValueOut(BaseModel):
    value: str


class EntropyOut(BaseModel):
    bits: float
    strength: str
    pool_size: int
