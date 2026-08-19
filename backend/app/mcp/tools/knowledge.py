"""forge_link_items, forge_unlink_items (06_API.md SS3). Both call
services/knowledge/service.py directly - the one documented, narrow
exception to "every tool calls its own domain's service" (see
test_mcp_tools_static_checks.py's _FORBIDDEN_IMPORTS comment), since linking
is inherently cross-item and knowledge_service already owns that logic for
the REST API too."""

from __future__ import annotations

from mcp.server.mcpserver import Context, MCPServer

from app.core.errors import AppError
from app.mcp.auth import require_scope
from app.mcp.tools._common import current_scope, tool_session
from app.services.knowledge import service as knowledge_service

_VALID_ITEM_TYPES = {"note", "document"}


def register(server: MCPServer) -> None:
    @server.tool(
        name="forge_link_items",
        description=(
            "Create an explicit link between two notes/documents (any combination). "
            "Linking is undirected in the product - source/target only distinguish "
            "which item you're linking from. Re-linking an already-linked pair (in "
            "either direction) returns the existing link, not an error."
        ),
    )
    async def forge_link_items(
        ctx: Context, source_type: str, source_id: str, target_type: str, target_id: str
    ) -> dict:
        if source_type not in _VALID_ITEM_TYPES or target_type not in _VALID_ITEM_TYPES:
            raise AppError(
                "source_type/target_type must be 'note' or 'document'", status_code=422, code="validation_error"
            )
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:write")
            try:
                link = await knowledge_service.create_link(session, source_type, source_id, target_type, target_id)
            except AppError as exc:
                if exc.code != "knowledge_link_duplicate":
                    raise
                # Corrected per re-reading the actual service behavior
                # (06_API.md/07_TESTING.md SS2 require "relinking an
                # already-linked pair returns the existing link," but
                # create_link's real implementation raises a 409 to protect
                # the unique constraint - that error is for the REST API's
                # own duplicate-prevention UX, not this tool's documented
                # idempotency contract). Fetch and return the existing link
                # instead of propagating the error.
                existing = await knowledge_service.list_links(session, source_type, source_id)
                link = next(v for v in existing if v.other_type == target_type and v.other_id == target_id)
            return {
                "id": link.link_id,
                "source_type": source_type,
                "source_id": source_id,
                "target_type": link.other_type,
                "target_id": link.other_id,
                "created_at": link.created_at,
            }

    @server.tool(
        name="forge_unlink_items",
        description="Remove a link by its id (from forge_link_items/forge_context). Does not delete the linked items themselves.",
    )
    async def forge_unlink_items(ctx: Context, link_id: str) -> dict:
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:write")
            await knowledge_service.delete_link(session, link_id)
            return {"unlinked": True, "id": link_id}
