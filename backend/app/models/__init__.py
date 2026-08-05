"""SQLModel table models. Import every module here so Alembic autogenerate
and ``SQLModel.metadata.create_all`` (tests) see the full schema."""

from .activity import ActivityLog
from .app_config import AppConfig
from .document import Document
from .knowledge import DocumentTagLink, KnowledgeLink, NoteTagLink
from .model_playground import PlaygroundResult, PlaygroundRun, ProviderCredential
from .note import Note
from .project import Project
from .project_init import ProjectInitGeneration
from .prompt_studio import Prompt, PromptVersion
from .secrets import Folder, Secret, SecretTagLink, SecretVersion, Tag
from .workbench import WorkbenchLayout

__all__ = [
    "ActivityLog",
    "AppConfig",
    "Document",
    "DocumentTagLink",
    "KnowledgeLink",
    "Note",
    "NoteTagLink",
    "PlaygroundResult",
    "PlaygroundRun",
    "Project",
    "ProviderCredential",
    "ProjectInitGeneration",
    "Prompt",
    "PromptVersion",
    "Folder",
    "Secret",
    "SecretTagLink",
    "SecretVersion",
    "Tag",
    "WorkbenchLayout",
]
