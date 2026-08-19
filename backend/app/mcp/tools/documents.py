"""forge_get_document, forge_create_document, forge_update_document,
forge_delete_document (06_API.md SS1-2). Identical shape to notes.py's
trio, substituting services/documents/service.py. ``content`` is HTML
(the rich-text editor's storage format), not Markdown - stated in each
tool's docstring since that's what an LLM caller needs told, not just
documented in 06_API.md."""

from __future__ import annotations

from mcp.server.mcpserver import Context, MCPServer
from pydantic import StrictBool

from app.core.errors import AppError
from app.mcp.auth import require_scope
from app.mcp.tools._common import current_scope, filtered_update_kwargs, tool_session, validate_project_id
from app.schemas.documents import DocumentCreateIn, DocumentOut, DocumentUpdateIn
from app.services.documents import service as documents_service
from app.services.knowledge import service as knowledge_service


def register(server: MCPServer) -> None:
    @server.tool(name="forge_get_document", description="Get the full content of one document by id.")
    async def forge_get_document(ctx: Context, document_id: str) -> DocumentOut:
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:read")
            document = await documents_service.get_document(session, document_id)
            return DocumentOut.model_validate(document)

    @server.tool(
        name="forge_create_document",
        description=(
            "Create a document, optionally scoped to a project. content must be "
            "valid HTML (the Documents editor's storage format) - not Markdown. "
            "Plain text is also valid HTML (no markup required), but Markdown "
            "syntax will render literally, not formatted."
        ),
    )
    async def forge_create_document(
        ctx: Context,
        title: str,
        content: str | None = None,
        project_id: str | None = None,
    ) -> DocumentOut:
        """content must be valid HTML (the Documents editor's storage
        format) - not Markdown. Plain text is also valid HTML (no markup
        required), but Markdown syntax will render literally, not formatted."""
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:write")
            await validate_project_id(session, project_id)
            data = DocumentCreateIn(**filtered_update_kwargs(title=title, content=content, project_id=project_id))
            document = await documents_service.create_document(session, data, source="mcp")
            return DocumentOut.model_validate(document)

    @server.tool(
        name="forge_update_document",
        description=(
            "Partially update a document - only the fields you supply change, "
            "everything else is left untouched. content, if supplied, must be "
            "valid HTML, not Markdown (see forge_create_document)."
        ),
    )
    async def forge_update_document(
        ctx: Context,
        document_id: str,
        title: str | None = None,
        content: str | None = None,
        project_id: str | None = None,
        pinned: bool | None = None,
    ) -> DocumentOut:
        """content, if supplied, must be valid HTML - see forge_create_document."""
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:write")
            await validate_project_id(session, project_id)
            data = DocumentUpdateIn(
                **filtered_update_kwargs(title=title, content=content, project_id=project_id, pinned=pinned)
            )
            document = await documents_service.update_document(session, document_id, data)
            return DocumentOut.model_validate(document)

    @server.tool(
        name="forge_delete_document",
        description=(
            "Permanently delete a document - irreversible, there is no trash. "
            "Requires confirm: true (a literal boolean, never inferred from "
            "conversation) or the call fails validation and nothing is deleted."
        ),
    )
    async def forge_delete_document(ctx: Context, document_id: str, confirm: StrictBool) -> dict:
        # StrictBool is load-bearing - see forge_delete_note's identical
        # comment in notes.py for why a plain `bool` silently accepted
        # "true"/"1"/1 as authorization (Milestone 2 Agentic Review BLOCKER).
        if confirm is not True:
            raise AppError(
                "Deletion requires confirm: true in the structured tool call - "
                "it is never inferred from conversation context",
                status_code=422,
                code="validation_error",
            )
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:delete")
            await documents_service.get_document(session, document_id)
            await knowledge_service.purge_links_for(session, "document", document_id)
            await documents_service.delete_document(session, document_id, source="mcp")
            return {"deleted": True, "id": document_id}
