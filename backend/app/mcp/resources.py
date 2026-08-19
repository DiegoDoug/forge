"""forge://projects, forge://projects/{project_id} (06_API.md SS5). Live
query on every read, no caching/subscription - the same "no new persistence
layer" discipline 01_SPEC.md SS9 states for the memory-capture tools,
applied here to resources instead.

Scope enforcement (forge:read) is fully verifiable for
forge://projects/{project_id}: it is a resource *template* (its URI has a
variable), and this MCP SDK version (mcp 2.0.0) injects Context into
template resource functions exactly like it does tool functions -
current_scope()/require_scope() below work identically to every tool
handler in app/mcp/tools/.

forge://projects (no URI variable, per 06_API.md SS5's literal URI and its
"auto-discovery: yes" requirement) is a **documented SDK limitation, not an
oversight**: mcp.server.mcpserver.server.MCPServer.resource's own decorator
explicitly raises "Context injection for static resources is not
supported" if a static (non-template) resource function declares a Context
parameter, and FunctionResource.fn (mcp/server/mcpserver/resources/types.py)
is typed Callable[[], Any] - called with zero arguments, always, for every
read, by every caller, regardless of that caller's token or its scopes.
There is no per-request hook into a static resource's read() in this SDK
version's public API - confirmed by reading FunctionResource.read() and
MCPServer.read_resource() directly, not assumed. Reshaping this resource
into a template (e.g. an always-omitted fake query variable) would also
change its wire discovery path from resources/list to
resources/templates/list, breaking 06_API.md SS5's explicit "auto-discovery:
yes - small, bounded list" requirement for this exact resource.

Net effect: forge://projects is reachable by any validly-authenticated MCP
token (McpBearerAuthMiddleware still requires one - the same connection-level
gate every /mcp request goes through), regardless of that token's granted
scopes - not full parity with forge_list_projects, which the tool layer CAN
and does scope-check. The data this resource exposes (project
name/description/color/counts - project_to_mcp_out already excludes
secret_count) is the same non-sensitive shape a forge:write-only or
forge:delete-only token's holder could learn other ways in this phase's own
tool surface regardless (e.g. forge_create_project's own not-found/duplicate
errors on a project_id leak whether a given id exists). Flagged here for
Milestone 4's Agentic Review rather than silently built around - see
CURRENT_STATE.md and VERIFICATION_CONTRACT.md."""

from __future__ import annotations

from mcp.server.mcpserver import Context, MCPServer

from app.mcp.auth import require_scope
from app.mcp.tools._common import current_scope, tool_session
from app.mcp.tools.projects import project_to_mcp_out
from app.services.projects import service as projects_service


def register(server: MCPServer) -> None:
    @server.resource(
        "forge://projects",
        name="forge-projects",
        title="Forge Projects",
        description=(
            "All non-archived projects, with note/document counts - a cheap orientation "
            "view for a client that auto-discovers resources."
        ),
        mime_type="application/json",
    )
    async def forge_projects_resource() -> list[dict]:
        async with tool_session() as session:
            projects = await projects_service.list_projects(session, archived=False)
            return [project_to_mcp_out(p, c) for p, c in projects]

    @server.resource(
        "forge://projects/{project_id}",
        name="forge-project",
        title="Forge Project",
        description="One project's detail, including note/document counts.",
        mime_type="application/json",
    )
    async def forge_project_resource(project_id: str, ctx: Context) -> dict:
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:read")
            project, counts = await projects_service.get_project(session, project_id)
            return project_to_mcp_out(project, counts)
