from __future__ import annotations

from pydantic import BaseModel, Field


class CronParseIn(BaseModel):
    expression: str = Field(min_length=1, max_length=200)
    count: int = Field(default=5, ge=1, le=25)


class CronParseOut(BaseModel):
    description: str
    next_runs: list[str]
