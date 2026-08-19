"""forge_list_projects, forge_get_project, forge_create_project,
forge_update_project (06_API.md SS1-2). No forge_delete_project - see
01_SPEC.md SS5, "deliberately not included."

Output deliberately omits ``secret_count`` - `services/projects/service.py`
returns a ProjectCounts including it (used by the REST `ProjectOut`/
`ProjectSummaryOut` schemas), but exposing vault size to an MCP client would
leak information about the Secrets vault this phase otherwise structurally
excludes (01_SPEC.md SS2). Built as a plain dict here, not a new Pydantic
schema in schemas/projects.py, since this shape exists only for MCP output
framing, not as a Forge-wide API contract.

``default_provider``/``default_model`` ARE included in output (unlike
``secret_count``) - clarified per the Milestone 2 Agentic Review, which
flagged the original docstring's "excluded from the tool surface" wording as
ambiguous. The exclusion (below, in forge_create_project/forge_update_project)
applies to *write input* only: an MCP caller cannot set a project's AI
defaults via this tool surface. Reading them back is fine - they are plain
string identifiers (e.g. "anthropic"/"claude-3-5-sonnet"), not secrets, and
are already exposed to any authenticated browser session via the existing
REST `ProjectOut`. There is no security reason to hide them from an MCP
read, only a reason not to add an MCP-driven way to change them (which would
need Model Playground's provider/model validation, out of scope here)."""

from __future__ import annotations

from mcp.server.mcpserver import Context, MCPServer

from app.mcp.auth import require_scope
from app.mcp.tools._common import current_scope, filtered_update_kwargs, tool_session
from app.models.project import Project
from app.schemas.projects import ProjectCreateIn, ProjectUpdateIn
from app.services.projects import service as projects_service
from app.services.projects.service import ProjectCounts


def project_to_mcp_out(project: Project, counts: ProjectCounts) -> dict:
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "color": project.color,
        "archived": project.archived,
        "default_provider": project.default_provider,
        "default_model": project.default_model,
        "note_count": counts.note_count,
        "document_count": counts.document_count,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


def register(server: MCPServer) -> None:
    @server.tool(
        name="forge_list_projects",
        description="List projects (with note/document counts) for orientation and navigation.",
    )
    async def forge_list_projects(ctx: Context, archived: bool = False) -> list[dict]:
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:read")
            projects = await projects_service.list_projects(session, archived=archived)
            return [project_to_mcp_out(p, c) for p, c in projects]

    @server.tool(name="forge_get_project", description="Get one project's detail, including note/document counts.")
    async def forge_get_project(ctx: Context, project_id: str) -> dict:
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:read")
            project, counts = await projects_service.get_project(session, project_id)
            return project_to_mcp_out(project, counts)

    @server.tool(name="forge_create_project", description="Create a project - a label Notes/Documents can be scoped to.")
    async def forge_create_project(
        ctx: Context,
        name: str,
        description: str | None = None,
        color: str | None = None,
    ) -> dict:
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:write")
            data = ProjectCreateIn(**filtered_update_kwargs(name=name, description=description, color=color))
            project, counts = await projects_service.create_project(session, data, source="mcp")
            return project_to_mcp_out(project, counts)

    @server.tool(
        name="forge_update_project",
        description=(
            "Partially update a project's name/description/color/archived state "
            "- only the fields you supply change. There is no forge_delete_project; "
            "archive instead."
        ),
    )
    async def forge_update_project(
        ctx: Context,
        project_id: str,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
        archived: bool | None = None,
    ) -> dict:
        async with tool_session() as session:
            scope = await current_scope(ctx, session)
            require_scope(scope, "forge:write")
            data = ProjectUpdateIn(
                **filtered_update_kwargs(name=name, description=description, color=color, archived=archived)
            )
            project, counts = await projects_service.update_project(session, project_id, data, source="mcp")
            return project_to_mcp_out(project, counts)
