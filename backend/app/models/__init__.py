"""SQLModel table models. Import every module here so Alembic autogenerate
and ``SQLModel.metadata.create_all`` (tests) see the full schema."""

from .activity import ActivityLog
from .app_config import AppConfig
from .document import Document
from .note import Note
from .vault import Folder, Secret, SecretTagLink, SecretVersion, Tag

__all__ = [
    "ActivityLog",
    "AppConfig",
    "Document",
    "Note",
    "Folder",
    "Secret",
    "SecretTagLink",
    "SecretVersion",
    "Tag",
]
