from __future__ import annotations

from pydantic import BaseModel, Field


class MasterPasswordIn(BaseModel):
    master_password: str = Field(min_length=8, max_length=256)


class ChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=8, max_length=256)
    new_password: str = Field(min_length=8, max_length=256)


class SetupStatusOut(BaseModel):
    setup_completed: bool


class SessionOut(BaseModel):
    authenticated: bool
