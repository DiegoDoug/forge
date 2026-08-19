"""forge_get_note, forge_create_note, forge_update_note, forge_delete_note
(06_API.md SS1-2). Every handler: current_scope() -> require_scope() ->
call the same services/notes/service.py functions the REST routes call ->
shape a NoteOut. No handler here reaches the database directly - every row
fetch goes through notes_service (01_SPEC.md SS5.3, AC20)."""

from __future__ import annotations

from mcp.server.mcpserver import Context, MCPServer
from pydantic import StrictBool

from app.core.errors import AppError
from app.mcp.auth import require_scope
from app.mcp.tools._common import current_scope, filtered_update_kwargs, tool_session, validate_project_id
from app.schemas.notes import NoteCreateIn, NoteOut, NoteUpdateIn
from app.services.knowledge import service as knowledge_service
from app.services.notes import service as notes_service


def register(server: MCPServer) -> None:
    @server.tool(name="forge_get_note")
    async def forge_get_note(ctx: Context, note_id: str) -> NoteOut:
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:read")
            note = await notes_service.get_note(session, note_id)
            return NoteOut.model_validate(note)

    @server.tool(name="forge_create_note")
    async def forge_create_note(
        ctx: Context,
        title: str,
        content: str | None = None,
        color: str | None = None,
        project_id: str | None = None,
    ) -> NoteOut:
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:write")
            await validate_project_id(session, project_id)
            data = NoteCreateIn(**filtered_update_kwargs(title=title, content=content, color=color, project_id=project_id))
            note = await notes_service.create_note(session, data, source="mcp")
            return NoteOut.model_validate(note)

    @server.tool(name="forge_update_note")
    async def forge_update_note(
        ctx: Context,
        note_id: str,
        title: str | None = None,
        content: str | None = None,
        color: str | None = None,
        project_id: str | None = None,
        pinned: bool | None = None,
        archived: bool | None = None,
    ) -> NoteOut:
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:write")
            await validate_project_id(session, project_id)
            data = NoteUpdateIn(
                **filtered_update_kwargs(
                    title=title, content=content, color=color, project_id=project_id, pinned=pinned, archived=archived
                )
            )
            note = await notes_service.update_note(session, note_id, data)
            return NoteOut.model_validate(note)

    @server.tool(name="forge_delete_note")
    async def forge_delete_note(ctx: Context, note_id: str, confirm: StrictBool) -> dict:
        # StrictBool (not bool) is load-bearing, not decorative: a plain
        # `bool` type hint lets Pydantic's lax validation coerce "true",
        # "1", "yes", or the integer 1 into Python True, silently defeating
        # the "structural confirmation only" guarantee this tool depends on
        # - an MCP client that mistakenly (or maliciously) sent a
        # string/int would have authorized a permanent delete anyway.
        # Caught by the Milestone 2 Agentic Review (BLOCKER); verified fixed
        # by a dedicated regression test exercising exactly these coerced
        # values. StrictBool rejects all of them at the schema-validation
        # layer, before this handler body ever runs.
        if confirm is not True:
            # Belt-and-braces runtime check for the one case StrictBool
            # itself doesn't reject: confirm: false is valid input, just
            # not sufficient to authorize deletion - never inferred from
            # anything but this exact structured field (01_SPEC.md SS6).
            raise AppError(
                "Deletion requires confirm: true in the structured tool call - "
                "it is never inferred from conversation context",
                status_code=422,
                code="validation_error",
            )
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:delete")
            # Existence check BEFORE any mutation is staged (01_SPEC.md SS6,
            # AC7a) - a delete against a bad ID must not purge links for
            # something that was never confirmed to exist.
            await notes_service.get_note(session, note_id)
            await knowledge_service.purge_links_for(session, "note", note_id)
            await notes_service.delete_note(session, note_id, source="mcp")
            return {"deleted": True, "id": note_id}
