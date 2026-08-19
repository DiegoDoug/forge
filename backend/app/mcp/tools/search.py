"""forge_search, forge_context (06_API.md SS1). Both call
notes_service.search_notes/documents_service.search_documents directly -
never search_service.global_search, which also returns Secrets (name-only,
but still a leak of the vault's existence/contents-by-name to any MCP
client - 01_SPEC.md SS5.1). project_id, when given, is applied inside the
FTS query itself (before the LIMIT 50 cap), not as a post-filter on the
returned rows - 01_SPEC.md SS5.2."""

from __future__ import annotations

from mcp.server.mcpserver import Context, MCPServer

from app.core.errors import AppError
from app.mcp.auth import require_scope
from app.mcp.tools._common import current_scope, tool_session, validate_project_id
from app.mcp.tools.projects import project_to_mcp_out
from app.services.documents import service as documents_service
from app.services.knowledge import service as knowledge_service
from app.services.notes import service as notes_service
from app.services.projects import service as projects_service

_SNIPPET_LENGTH = 140
_VALID_TYPES = {"note", "document"}


def _note_result(note) -> dict:
    return {
        "id": note.id,
        "type": "note",
        "title": note.title or "Untitled",
        "snippet": note.content[:_SNIPPET_LENGTH],
        "project_id": note.project_id,
        "updated_at": note.updated_at,
    }


def _document_result(document) -> dict:
    return {
        "id": document.id,
        "type": "document",
        "title": document.title or "Untitled",
        "snippet": document.content[:_SNIPPET_LENGTH],
        "project_id": document.project_id,
        "updated_at": document.updated_at,
    }


def _validate_query(query: str) -> None:
    if not query.strip() or len(query) > 200:
        raise AppError("query must be 1-200 characters", status_code=422, code="validation_error")


def _validate_topic(topic: str) -> None:
    # Same guard as _validate_query - topic feeds the identical FTS
    # phrase-prefix construction (f'"{topic}"*'), so the pathological-input
    # concern query's 200-char cap exists for (06_API.md's stated rationale)
    # applies equally here. Found missing by the Milestone 3 Agentic Review
    # (MINOR) - the two tools' input validation had silently drifted apart.
    if not topic.strip() or len(topic) > 200:
        raise AppError("topic must be 1-200 characters", status_code=422, code="validation_error")


def _validate_types(types: list[str] | None) -> set[str]:
    if not types:
        return set(_VALID_TYPES)
    unknown = set(types) - _VALID_TYPES
    if unknown:
        raise AppError(f"Unknown type(s): {sorted(unknown)} - must be 'note' and/or 'document'", status_code=422, code="validation_error")
    return set(types)


def _note_context_result(note, tags: dict[str, list]) -> dict:
    return {
        "id": note.id,
        "title": note.title or "Untitled",
        "snippet": note.content[:_SNIPPET_LENGTH],
        "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags.get(note.id, [])],
        "updated_at": note.updated_at,
    }


def _document_context_result(document, tags: dict[str, list]) -> dict:
    return {
        "id": document.id,
        "title": document.title or "Untitled",
        "snippet": document.content[:_SNIPPET_LENGTH],
        "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags.get(document.id, [])],
        "updated_at": document.updated_at,
    }


def register(server: MCPServer) -> None:
    @server.tool(
        name="forge_search",
        description=(
            "Full-text search across Notes and Documents (never Secrets). Returns "
            "summarized results (title + snippet), capped at 50 per type. Use "
            "types to restrict to just notes or documents, project_id to scope "
            "to one project."
        ),
    )
    async def forge_search(
        ctx: Context,
        query: str,
        types: list[str] | None = None,
        project_id: str | None = None,
    ) -> list[dict]:
        _validate_query(query)
        search_types = _validate_types(types)
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:read")
            # Not strictly mandated by 06_API.md for forge_search (only
            # forge_context's contract states this explicitly), but applied
            # here too for consistency with every other project_id-accepting
            # tool - a bad ID should error, not silently produce
            # unfiltered-looking-scoped-but-actually-empty results.
            await validate_project_id(session, project_id)
            results: list[dict] = []
            if "note" in search_types:
                notes = await notes_service.search_notes(session, query, project_id=project_id)
                results.extend(_note_result(n) for n in notes)
            if "document" in search_types:
                documents = await documents_service.search_documents(session, query, project_id=project_id)
                results.extend(_document_result(d) for d in documents)
            return results

    @server.tool(
        name="forge_context",
        description=(
            "Claude-oriented aggregate retrieval for a topic: the project record "
            "(if project_id given), matching notes/documents with their tags, and "
            "the links between those matched items. Returns summarized content "
            "(snippets, not full bodies) - use forge_get_note/forge_get_document "
            "for full content once you've identified an item of interest."
        ),
    )
    async def forge_context(ctx: Context, topic: str, project_id: str | None = None) -> dict:
        _validate_topic(topic)
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:read")

            project_out = None
            if project_id is not None:
                # get_project itself raises not-found on a bad id (AC13) -
                # no separate validate_project_id call needed here.
                project, counts = await projects_service.get_project(session, project_id)
                project_out = project_to_mcp_out(project, counts)

            notes = await notes_service.search_notes(session, topic, project_id=project_id)
            documents = await documents_service.search_documents(session, topic, project_id=project_id)

            note_tags = await knowledge_service.tags_for_items(session, "note", [n.id for n in notes])
            document_tags = await knowledge_service.tags_for_items(session, "document", [d.id for d in documents])

            items: list[tuple[str, str]] = [("note", n.id) for n in notes] + [("document", d.id) for d in documents]
            item_set = set(items)
            links_by_item = await knowledge_service.list_links_for_items(session, items)
            seen_link_ids: set[str] = set()
            links_out: list[dict] = []
            for item_key, views in links_by_item.items():
                for view in views:
                    other_key = (view.other_type, view.other_id)
                    if other_key not in item_set:
                        # 01_SPEC.md SS5.2 describes this field as "existing
                        # links BETWEEN the matched items" - a link to
                        # something outside notes/documents above would be a
                        # dangling reference with no title/content anywhere
                        # in this same response (Milestone 3 Agentic Review
                        # MAJOR finding). Excluded, not included-with-a-stub:
                        # forge_search/forge_get_note/forge_get_document
                        # already exist for a caller who wants to follow it.
                        continue
                    if view.link_id in seen_link_ids:
                        continue
                    seen_link_ids.add(view.link_id)
                    links_out.append(
                        {
                            "source_type": item_key[0],
                            "source_id": item_key[1],
                            "target_type": view.other_type,
                            "target_id": view.other_id,
                        }
                    )

            return {
                "project": project_out,
                "notes": [_note_context_result(n, note_tags) for n in notes],
                "documents": [_document_context_result(d, document_tags) for d in documents],
                "links": links_out,
            }
