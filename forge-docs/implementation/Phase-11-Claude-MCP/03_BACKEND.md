# Phase 11 — Backend Design

> **Purpose:** Service-layer reuse map, new modules, config, and deployment wiring.
> **Status:** Draft — pending Authorization.
> **Last Updated:** 2026-08-18

---

## 1. New package layout

```
backend/app/mcp/
    __init__.py
    server.py        # MCP server bootstrap, mounts Streamable HTTP ASGI app at /mcp
    auth.py           # require_mcp_auth dependency, scope-check helper
    tools/
        __init__.py   # tool registry (flat dict: name -> handler), NOT a new capability-registry system
        notes.py       # forge_get_note, forge_create_note, forge_update_note, forge_delete_note
        documents.py   # forge_get_document, forge_create_document, forge_update_document, forge_delete_document
        projects.py    # forge_list_projects, forge_get_project, forge_create_project, forge_update_project
        knowledge.py   # forge_link_items, forge_unlink_items
        search.py      # forge_search, forge_context
        memory.py      # forge_capture_session, forge_capture_decision
    resources.py       # forge://projects, forge://projects/{id}
backend/app/services/mcp/
    __init__.py
    tokens.py          # issue/verify/revoke/list McpToken, scope checks, last_used_at throttling
backend/app/api/routes/
    mcp_tokens.py       # NEW REST route (not an MCP tool): POST/GET/DELETE /api/mcp/tokens — see 01_SPEC.md §4.3.1
```

This mirrors the existing `services/<domain>/service.py` + `api/routes/<domain>.py` split: `app/mcp/tools/*.py` is the thin "router" layer (parses MCP tool input, calls services, shapes MCP output), `services/mcp/tokens.py` is the one genuinely new piece of business logic this phase adds (token lifecycle) — everything else is composition over existing services. `api/routes/mcp_tokens.py` is a REST route (Milestone 1, per `01_SPEC.md` §4.3.1) — provisioning is an admin action taken through the existing REST surface, deliberately not exposed as an MCP tool Claude can call on itself.

## 2. Service-layer reuse map

**Two service-layer signature changes apply across this table, both additive/non-breaking, both required by owner review:**
1. Every service function invoked by a *write* MCP tool that already calls `activity.record(...)` internally (`create_note`, `update_note`, `delete_note`, and the Documents/Projects equivalents) gains an additive `source: str = "ui"` keyword parameter, threaded straight into that internal `activity.record(...)` call. MCP tool handlers pass `source="mcp"`. **No MCP tool handler calls `activity.record(...)` directly** — doing so would double-log every mutation (§4.5 of `01_SPEC.md`).
2. `notes_service.search_notes` and `documents_service.search_documents` gain an additive `project_id: str | None = None` parameter, applied as a query-level filter before the existing `LIMIT 50` (§5.2 of `01_SPEC.md`).

| MCP tool | Calls (exact signatures from repository analysis, as amended) | Notes |
|---|---|---|
| `forge_search` | `notes_service.search_notes(session, query, project_id=...)`, `documents_service.search_documents(session, query, project_id=...)` | Not `search_service.global_search` — see `01_SPEC.md` §5.1. |
| `forge_context` | `projects_service.get_project`, `notes_service.search_notes(..., project_id=...)`, `documents_service.search_documents(..., project_id=...)`, `knowledge_service.list_knowledge`, `knowledge_service.list_links_for_items(session, items)` (new batch method — see below) | Project-scoped at the query, not filtered after retrieval. Links resolved in one batch query, not N+1. |
| `forge_get_note` | `notes_service.get_note(session, note_id)` — **mandatory**, no direct `session.get(Note, ...)` in any tool handler (`01_SPEC.md` §5.3). New one-line addition to `notes/service.py`, matching Documents' existing 404-raising `get_document` shape exactly. | Small, additive, non-breaking service addition. |
| `forge_create_note` | `notes_service.create_note(session, NoteCreateIn(...), source="mcp")` | |
| `forge_update_note` | `notes_service.update_note(session, note_id, NoteUpdateIn(...), source="mcp")` | |
| `forge_delete_note` | 1. `notes_service.get_note(session, note_id)` (existence check, no mutation) 2. `knowledge_service.purge_links_for(session, "note", note_id)` (stages, no commit) 3. `notes_service.delete_note(session, note_id, source="mcp")` (stages + commits both atomically) | Corrected sequence — see `01_SPEC.md` §6. Must not call delete before existence is confirmed. |
| `forge_get_document` | `documents_service.get_document(session, document_id)` | Already 404-raising. |
| `forge_create_document` | `documents_service.create_document(session, DocumentCreateIn(...), source="mcp")` | |
| `forge_update_document` | `documents_service.update_document(session, document_id, DocumentUpdateIn(...), source="mcp")` | |
| `forge_delete_document` | Same 3-step sequence as `forge_delete_note`, against `documents_service`. | Same correction applies. |
| `forge_list_projects` | `projects_service.list_projects(session, archived=...)` | Drop `secret_count` from `ProjectCounts` at output-shaping. |
| `forge_get_project` | `projects_service.get_project(session, project_id)` | Same field drop. |
| `forge_create_project` | `projects_service.create_project(session, ProjectCreateIn(...), source="mcp")` | |
| `forge_update_project` | `projects_service.update_project(session, project_id, ProjectUpdateIn(...), source="mcp")` | |
| `forge_link_items` | `knowledge_service.create_link(session, source_type, source_id, target_type, target_id)` | |
| `forge_unlink_items` | `knowledge_service.delete_link(session, link_id)` | |
| `forge_capture_decision` / `forge_capture_session` | `notes_service.create_note(..., source="mcp")` then `knowledge_service.add_tag(session, "note", note.id, name=..., color=...)` | See `01_SPEC.md` §9. |

### 2.1 New batch method: `knowledge_service.list_links_for_items`

```python
# backend/app/services/knowledge/service.py — additive, internal use (forge_context only in this phase)
async def list_links_for_items(
    session: AsyncSession,
    items: list[tuple[str, str]],   # [(item_type, item_id), ...]
) -> dict[tuple[str, str], list[KnowledgeLinkView]]:
    """One query for a whole result set, avoiding N+1 (up to ~100 individual
    list_links calls per forge_context invocation otherwise)."""
```

Implementation queries `KnowledgeLink` once with an `OR`-chain (or equivalent `IN`-based match) across the normalized `(source_type, source_id)`/`(target_type, target_id)` pairs for every item in `items`, then groups result rows back onto whichever input pair(s) they belong to in Python. Does not change `GET /api/knowledge` or any REST response shape — internal service capability only.

## 3. Auth dependencies

Two separate dependencies — **never merged into one** — reflecting that the bootstrap credential and persistent tokens authorize categorically different things (`01_SPEC.md` §4.3):

```python
# backend/app/mcp/auth.py — shape, not final code

async def require_mcp_auth(
    session: SessionDep,
    authorization: Annotated[str | None, Header()] = None,
) -> McpTokenContext:
    """Accepts ONLY persistent McpToken-table tokens. Never accepts the
    bootstrap token — there is no fallback branch that checks it here."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Missing MCP bearer token")
    token = authorization.removeprefix("Bearer ")
    ctx = await mcp_tokens_service.verify(session, token)   # checks token_hash match + revoked_at IS NULL
    if ctx is None:
        raise UnauthorizedError("Invalid or revoked MCP token")
    await mcp_tokens_service.touch_last_used(session, ctx.token_id)   # throttled — see below, not an unconditional write
    return ctx

def require_scope(scope: str):
    async def _check(ctx: McpTokenContext = Depends(require_mcp_auth)) -> McpTokenContext:
        if scope not in ctx.scopes:
            raise ForbiddenError(f"MCP token lacks required scope: {scope}")
        return ctx
    return _check

async def require_bootstrap_auth(
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """Used ONLY by POST /api/mcp/tokens. Never wired into any /mcp route.
    Checks settings.mcp_bootstrap_enabled first — a hard kill switch, not just
    a comparison the token would fail anyway."""
    if not settings.mcp_bootstrap_enabled:
        raise UnauthorizedError("MCP bootstrap provisioning is disabled")
    if not authorization or authorization.removeprefix("Bearer ") != settings.resolved_mcp_bootstrap_token:
        raise UnauthorizedError("Invalid bootstrap token")
```

`touch_last_used` (in `services/mcp/tokens.py`) implements the write-throttling decision: it issues an `UPDATE` only when `last_used_at IS NULL OR last_used_at < now() - 5 minutes`, so a burst of MCP calls from one active token produces at most one write per 5-minute window, not one write per request — avoiding hot-path write contention on SQLite's single-writer model for a field that only needs staleness-level precision.

Applied per-tool (`Depends(require_scope("forge:write"))`), not once at connection time — see `01_SPEC.md` §4.4 for why. This sits entirely alongside `backend/app/api/deps.py`'s existing `AuthDep`/`require_auth` — neither file is modified by the other; `/mcp` routes never depend on `AuthDep`, `/api/*` routes never depend on `require_mcp_auth`, and no `/mcp` route ever depends on `require_bootstrap_auth` (that dependency is wired into `api/routes/mcp_tokens.py`'s `POST` handler only, alongside `AuthDep` as an alternative — see `01_SPEC.md` §4.3.1 for the "cookie OR bootstrap token" acceptance logic).

`McpTokenContext` is a small dataclass (`token_id`, `scopes: set[str]`) — not the ORM row itself, matching the existing convention of never exposing ORM objects directly (`07_CODING_STANDARDS.md` §1).

## 4. Config additions (`backend/app/core/config.py`)

Extending the existing flat-field, `FORGE_`-prefixed `Settings(BaseSettings)` pattern (mirrors `master_key`/`master_key_file` and the `vision_enabled`-style boolean-toggle precedent):

```python
mcp_enabled: bool = False
mcp_bootstrap_enabled: bool = True   # operator sets false once >=1 persistent token exists — closes POST /api/mcp/tokens entirely
mcp_bootstrap_token: str | None = None
mcp_bootstrap_token_file: str | None = None   # Docker-secrets convention, same _read_secret_file helper as master_key_file
```

`resolved_mcp_bootstrap_token` property follows the same pattern as `resolved_master_key`. `/mcp` is only mounted in `main.py` if `settings.mcp_enabled` is true — instances that upgrade Forge without opting in get no new attack surface. `mcp_bootstrap_enabled` is checked independently of `mcp_enabled` — an operator can disable *provisioning* while leaving already-issued persistent tokens fully functional, or vice versa during initial setup.

## 5. Docker / deployment (documented, not applied during planning)

`docker/nginx.conf` needs one new `location` block, adjacent to the existing `/api/` block:

```nginx
location /mcp {
    proxy_pass http://backend:8000/mcp;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
    proxy_set_header Host $host;
    proxy_buffering off;   # Streamable HTTP may use SSE-flavored responses; avoid buffering them
}
```

`docker-compose.yml` needs `FORGE_MCP_ENABLED`, `FORGE_MCP_BOOTSTRAP_ENABLED`, `FORGE_MCP_BOOTSTRAP_TOKEN_FILE` (or `_TOKEN` for simple non-Docker-secrets setups) added to the `backend` service's environment block, alongside the existing `FORGE_MASTER_KEY`/`FORGE_SESSION_COOKIE_SECURE` entries. No new service, no new container, no new published port — `/mcp` rides the existing `${FORGE_PORT:-8585}` nginx port. `POST /api/mcp/tokens` rides the existing `/api/` nginx location block unchanged (it's an ordinary REST route under `/api/mcp/tokens`, not a new proxy target). These changes are specified here for the implementation task list (`09_IMPLEMENTATION_TASKS.md`); this planning session does not modify `docker/**`, per the brief's instruction. Operational note for `docs/Deployment.md`: after first provisioning a persistent token via `POST /api/mcp/tokens`, the operator should set `FORGE_MCP_BOOTSTRAP_ENABLED=false` and redeploy — this is documented as a required hardening step, not merely optional.

Local development: no change needed beyond the same env vars being set for `uvicorn --reload`, matching the existing no-dev-compose-profile convention in `docs/Development.md`.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
