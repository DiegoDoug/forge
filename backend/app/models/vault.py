from datetime import datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

from .base import new_id, utcnow


class SecretType(str, Enum):
    password = "password"
    api_key = "api_key"
    ssh_key = "ssh_key"
    jwt_secret = "jwt_secret"
    oauth_secret = "oauth_secret"
    env_var = "env_var"
    note = "note"
    other = "other"


class SecretTagLink(SQLModel, table=True):
    __tablename__ = "secret_tag_links"

    secret_id: str = Field(foreign_key="secrets.id", primary_key=True)
    tag_id: str = Field(foreign_key="tags.id", primary_key=True)


class Folder(SQLModel, table=True):
    __tablename__ = "folders"

    id: str = Field(default_factory=new_id, primary_key=True)
    name: str = Field(index=True, max_length=100)
    parent_id: str | None = Field(default=None, foreign_key="folders.id", index=True)
    created_at: datetime = Field(default_factory=utcnow)

    secrets: list["Secret"] = Relationship(back_populates="folder")


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: str = Field(default_factory=new_id, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=50)
    color: str = Field(default="#6366f1", max_length=20)

    secrets: list["Secret"] = Relationship(back_populates="tags", link_model=SecretTagLink)


class Secret(SQLModel, table=True):
    """A vault entry. ``encrypted_value``/``encrypted_metadata`` are opaque
    PyNaCl SecretBox ciphertext — plaintext never touches the database."""

    __tablename__ = "secrets"

    id: str = Field(default_factory=new_id, primary_key=True)
    name: str = Field(index=True, max_length=200)
    type: SecretType = Field(default=SecretType.other, index=True)
    folder_id: str | None = Field(default=None, foreign_key="folders.id", index=True)

    encrypted_value: bytes
    encrypted_metadata: bytes | None = Field(default=None)

    favorite: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    folder: Folder | None = Relationship(back_populates="secrets")
    tags: list[Tag] = Relationship(back_populates="secrets", link_model=SecretTagLink)
    versions: list["SecretVersion"] = Relationship(
        back_populates="secret",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "SecretVersion.created_at.desc()"},
    )


class SecretVersion(SQLModel, table=True):
    """Immutable snapshot of a secret's value, written whenever it changes."""

    __tablename__ = "secret_versions"

    id: str = Field(default_factory=new_id, primary_key=True)
    secret_id: str = Field(foreign_key="secrets.id", index=True)
    encrypted_value: bytes
    created_at: datetime = Field(default_factory=utcnow)

    secret: Secret = Relationship(back_populates="versions")
