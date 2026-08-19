"""MCP server bootstrap (Phase 11, Milestone 1). Builds the Streamable HTTP
ASGI app and mounts it inside the existing FastAPI process at /mcp,
iff FORGE_MCP_ENABLED is true (01_SPEC.md SS1, SS3; ADR-0018).

Zero tools/resources are registered in Milestone 1 - see IMPLEMENT.md.
Milestone 2 registers the first tools via ``server.tool()``/
``server.add_tool()`` on the MCPServer this module builds.
"""

from __future__ import annotations

from fastapi import FastAPI
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette

from app.core.config import get_settings
from app.core.version import VERSION
from app.mcp import resources as resources_module
from app.mcp.auth import McpBearerAuthMiddleware
from app.mcp.tools import documents as documents_tools
from app.mcp.tools import knowledge as knowledge_tools
from app.mcp.tools import memory as memory_tools
from app.mcp.tools import notes as notes_tools
from app.mcp.tools import projects as projects_tools
from app.mcp.tools import search as search_tools

MCP_MOUNT_PATH = "/mcp"

_INSTRUCTIONS = (
    "Forge is a self-hosted personal knowledge base (Notes, Documents, "
    "Projects, Knowledge Hub). Tools: forge_get/create/update/delete_note, "
    "the same four for documents, forge_list/get/create/update_project "
    "(no project delete), forge_search/forge_context for retrieval, "
    "forge_link_items/forge_unlink_items for the knowledge graph, and "
    "forge_capture_decision/forge_capture_session for persisting memory "
    "across sessions (both are Notes tagged ai-decision/ai-session - find "
    "them again later via forge_search/forge_context, no special tool "
    "needed). Resources: forge://projects (list), forge://projects/{id} "
    "(detail). Deletes require confirm: true and are permanent - there is "
    "no trash. Secrets/Settings/Crypto are never reachable through this "
    "server."
)


def build_mcp_server() -> MCPServer:
    server = MCPServer(
        name="forge",
        title="Forge",
        version=VERSION,
        instructions=_INSTRUCTIONS,
    )
    # Flat, explicit registration list (01_SPEC.md SS7) - not a dynamic
    # plugin-discovery system; sufficient at this tool count.
    notes_tools.register(server)
    documents_tools.register(server)
    projects_tools.register(server)
    search_tools.register(server)
    knowledge_tools.register(server)
    memory_tools.register(server)
    resources_module.register(server)
    return server


def build_mcp_asgi_app(server: MCPServer | None = None) -> Starlette:
    """The raw (unauthenticated) Starlette app the MCP SDK builds. Kept
    reachable separately from the authenticated, mountable app so
    main.py's lifespan can chain its `.router.lifespan_context` - a mounted
    sub-app does not automatically receive ASGI lifespan events; the parent
    must enter it explicitly (verified empirically against this SDK version;
    without this chaining the StreamableHTTP session manager never starts
    and every request hangs)."""
    server = server or build_mcp_server()
    return server.streamable_http_app(
        # Mounted at MCP_MOUNT_PATH by the parent app (app.mount), so this
        # app's own internal route path must be "/" - otherwise the
        # effective path would be /mcp/mcp, not /mcp.
        streamable_http_path="/",
        # Plain JSON responses instead of SSE-framed ones for non-streaming
        # requests. Milestone 1 has zero tools and no server-initiated
        # streaming need; this keeps the transport trivially testable with a
        # plain HTTP client while remaining valid Streamable HTTP per the
        # current MCP spec (json_response is a response-framing choice for
        # non-streaming exchanges, not a different transport - streaming
        # responses, if ever needed by a later milestone's tool, still use
        # SSE regardless of this flag).
        json_response=True,
        # DNS-rebinding protection (Host/Origin header allowlisting) is the
        # SDK's default defense for an unauthenticated local dev MCP server
        # reachable from a browser tab via loopback. It doesn't fit Forge's
        # actual deployment model (docs/Deployment.md: LAN IP, Tailscale
        # hostname, or a reverse-proxied domain - never a fixed allowlist of
        # Host headers), and it sits *behind* McpBearerAuthMiddleware in this
        # stack - our own bearer-token check is the real authorization
        # boundary here, not the SDK's Host-header heuristic, and an
        # attacker's webpage cannot produce a valid bearer token regardless
        # of which Host header it sends. Disabling this SDK-level check is a
        # deliberate, documented trade-off, not an oversight - see
        # 01_SPEC.md SS3 and this milestone's Agentic Review notes.
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )


def build_authenticated_mcp_app() -> tuple[Starlette, McpBearerAuthMiddleware]:
    raw_app = build_mcp_asgi_app()
    return raw_app, McpBearerAuthMiddleware(raw_app)


def mount_mcp_app(app: FastAPI) -> Starlette | None:
    """Mounts the MCP app at MCP_MOUNT_PATH iff FORGE_MCP_ENABLED is true.
    Returns the raw (pre-middleware) Starlette app so main.py's lifespan can
    chain its lifespan context, or None if MCP is disabled - nothing is
    mounted at all in that case, so a disabled instance has no new attack
    surface (01_SPEC.md SS3)."""
    settings = get_settings()
    if not settings.mcp_enabled:
        return None
    raw_app, wrapped = build_authenticated_mcp_app()
    app.mount(MCP_MOUNT_PATH, wrapped)
    return raw_app
