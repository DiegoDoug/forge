"""forge_capture_decision, forge_capture_session (06_API.md SS4). Both are
thin wrappers over notes_service.create_note plus knowledge_service.add_tag
with a reserved tag name - not a new persistence mechanism or memory
database (01_SPEC.md SS9). A later Claude session (or this same one) finds
these notes through the ordinary forge_search/forge_context path; nothing
here builds a parallel retrieval mechanism.

Output note: 06_API.md's Output row promises "Full NoteOut of the created
note, including the applied tag" - but NoteOut (schemas/notes.py) has no
tags field at all (confirmed by reading the schema; it was never meant to
carry tags - the REST Notes API doesn't return them inline either). Same
class of "plan describes desired behavior; the underlying type doesn't
actually carry it" gap Milestone 2/3 found for update_note's audit logging
and forge_link_items' idempotency. Resolved here (not deferred to a later
review) by returning NoteOut's own fields plus a tags list, not a bare
NoteOut - the only way to actually satisfy 06_API.md's stated contract."""

from __future__ import annotations

from datetime import datetime, timezone

from mcp.server.mcpserver import Context, MCPServer

from app.core.errors import AppError
from app.mcp.auth import require_scope
from app.mcp.tools._common import current_scope, tool_session, validate_project_id
from app.schemas.notes import NoteCreateIn, NoteOut
from app.services.knowledge import service as knowledge_service
from app.services.notes import service as notes_service

_TITLE_MAX_LENGTH = 200  # NoteCreateIn.title's own limit (schemas/notes.py)
_SUMMARY_MAX_LENGTH = 180  # 06_API.md SS4 - leaves room for either prefix below within _TITLE_MAX_LENGTH
_DECISION_TAG = "ai-decision"
_SESSION_TAG = "ai-session"
# Tag model's own field default (models/secrets.py Tag.color) - reserved
# tags deliberately look like an ordinary default-colored tag, not an
# invented "special" color with no basis anywhere else in the schema.
_RESERVED_TAG_COLOR = "#6366f1"


def _validate_summary(summary: str) -> None:
    if not summary.strip() or len(summary) > _SUMMARY_MAX_LENGTH:
        raise AppError(f"summary must be 1-{_SUMMARY_MAX_LENGTH} characters", status_code=422, code="validation_error")


def _note_with_tags(note, tags) -> dict:
    return {**NoteOut.model_validate(note).model_dump(), "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags]}


async def _capture(ctx: Context, *, title: str, detail: str | None, project_id: str | None, tag_name: str) -> dict:
    async with tool_session() as session:
        scope = await current_scope(ctx, session)
        require_scope(scope, "forge:write")
        await validate_project_id(session, project_id)
        data = NoteCreateIn(title=title[:_TITLE_MAX_LENGTH], content=detail or "", project_id=project_id)
        note = await notes_service.create_note(session, data, source="mcp")
        tags = await knowledge_service.add_tag(session, "note", note.id, tag_id=None, name=tag_name, color=_RESERVED_TAG_COLOR)
        return _note_with_tags(note, tags)


def register(server: MCPServer) -> None:
    @server.tool(
        name="forge_capture_decision",
        description=(
            "Persist an important decision as a retrievable Note, tagged 'ai-decision'. "
            "A thin wrapper over forge_create_note - later forge_search/forge_context calls, "
            "including from a different Claude session, will surface it like any other note. "
            "summary becomes the note's title (prefixed 'Decision: '); detail becomes its body."
        ),
    )
    async def forge_capture_decision(
        ctx: Context, summary: str, detail: str | None = None, project_id: str | None = None
    ) -> dict:
        _validate_summary(summary)
        return await _capture(ctx, title=f"Decision: {summary}", detail=detail, project_id=project_id, tag_name=_DECISION_TAG)

    @server.tool(
        name="forge_capture_session",
        description=(
            "Persist a session summary as a retrievable Note, tagged 'ai-session'. "
            "A thin wrapper over forge_create_note - later forge_search/forge_context calls, "
            "including from a different Claude session, will surface it like any other note. "
            "summary becomes the note's title (prefixed 'Session <date>: '); detail becomes its body."
        ),
    )
    async def forge_capture_session(
        ctx: Context, summary: str, detail: str | None = None, project_id: str | None = None
    ) -> dict:
        _validate_summary(summary)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return await _capture(
            ctx, title=f"Session {today}: {summary}", detail=detail, project_id=project_id, tag_name=_SESSION_TAG
        )
