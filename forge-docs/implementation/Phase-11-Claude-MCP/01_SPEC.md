# Phase 11 — Claude MCP / Second Brain — Specification

> **Purpose:** The architecture decision, MCP contract shape, security model, and milestone plan for Phase 11.
> **Scope:** This phase only.
> **Status:** Draft — pending Authorization.
> **Last Updated:** 2026-08-18

---

## 1. Architecture decision

### 1.1 Options evaluated

**Option A — MCP integrated into the Forge backend.** The MCP server runs as a module inside the existing FastAPI process (`backend/app/mcp/`), mounted as an ASGI sub-application (or a dedicated route group) at `/mcp`, sharing the same `AsyncSession` factory, the same `services/*` modules, and the same `backend/app/core/config.py` settings object as the REST API.

**Option B — a separate MCP process/container**, talking to Forge either through the existing REST API over HTTP, or directly to the SQLite database file.

### 1.2 Decision: Option A

**Rejected: Option B, direct-DB variant.** SQLite is file-based with a single writer at a time; Forge already owns the one process that opens it (`backend/app/database/`, engine created once at `main.py` startup, migrations run synchronously before serving — see `03_BACKEND.md` §1). A second process opening the same file introduces a second migration owner, a second connection-pool/locking domain, and a second place that must reimplement every invariant the service layer enforces (e.g. `knowledge_service.purge_links_for` orphan prevention, `ActivityLog` audit writes, Pydantic validation). This is exactly the "second implementation of Forge's business logic" the planning brief prohibits.

**Rejected: Option B, REST-API-client variant.** This avoids the DB-sharing problem but replaces direct service calls with HTTP calls to Forge's own REST API — meaning the MCP process would need its own copy of the browser-session auth flow (cookie jar, `/auth/unlock`) or a second auth bypass, doubles network hops for every tool call, and still needs its own Docker service, health check, and restart/redeploy story. It also does not reduce blast radius: whoever holds valid MCP credentials already has the same effective access as a browser session with `forge:write`/`forge:delete` scope, since both ultimately reach the same service layer and the same database. Isolation would be theatrical, not real.

**Chosen: Option A**, on this evidence:

- `forge-docs/03_ARCHITECTURE.md` explicitly describes Forge as **one modular monolith** — "one FastAPI process, one Next.js process, one SQLite database... no microservices" — and Phase 11 has no evidence-backed reason to be the first phase to break that invariant.
- The planning brief's core principle — "MCP tools should ultimately call the same service layer used by the existing application" — is satisfied *structurally*, not by convention, only if MCP code runs in the same process and imports the same `services/*` modules directly. A separate process reaching the same services means either duplicating them or calling back over HTTP, both of which the brief rules out.
- Forge's deployment model (`docker-compose.yml`, `docker/nginx.conf` — see Docker research) already proxies `/api/*` to the backend container; adding `/mcp` to that same proxy map is a one-line nginx change, not a new service, new Docker network, new health check, or new inter-service credential.
- Auth reuse: Forge's entire security model (`FORGE_MASTER_KEY`, Argon2id password hash, HMAC session tokens — `backend/app/core/security.py`) lives inside the backend process. An MCP token scheme that needs to sit *beside* (not replace) that model is far simpler to build as a second FastAPI dependency in the same process than as a cross-process trust handshake.
- `codegraph`/service-reuse precedent: every existing Forge feature (Notes, Documents, Projects, Knowledge) is a `services/<domain>/service.py` module called by both `api/routes/<domain>.py` and (per Model Playground, Prompt Studio) internal cross-feature callers. MCP tool handlers are simply one more caller of that same pattern.

**Trade-off accepted:** a vulnerability in the MCP library or a bug in a tool handler runs with the same process privileges as the REST API, rather than in an isolated sandbox. This is mitigated, not eliminated, by: (a) excluding Secrets/crypto entirely from the MCP surface (§2), (b) a scoped bearer-token model distinct from the browser session (§4), and (c) an MCP-specific audit trail (§8, reusing `ActivityLog`). If a future phase's threat model demands process isolation, `backend/app/mcp/` is factored as its own package specifically so it could be extracted into Option B later without rewriting tool logic — but that is not attempted now, per the brief's instruction not to add speculative future-proofing.

### 1.3 Rejected alternative recap (for the ADR)

| | Option A (chosen) | Option B (separate process) |
|---|---|---|
| Service-layer reuse | Direct import, structurally enforced | Requires HTTP re-entry or duplicated logic |
| Deployment | +1 nginx location block | +1 Docker service, network, health check |
| Auth | +1 FastAPI dependency, same process | Cross-process trust handshake needed |
| Isolation / blast radius | Shares process with REST API | Nominally separate, but same DB/services = same effective trust boundary |
| Consistency with `03_ARCHITECTURE.md` | Matches documented monolith invariant | Would be the first exception, unjustified by evidence |

This decision requires a new ADR (`decisions/00XX-mcp-server-integrated-not-separate-process.md`) before Authorization — see §7.

## 2. Product boundary — what is explicitly excluded and why

Framing (per the brief): this is **not** "give Claude CRUD access to Forge" — it is "make Forge the persistent knowledge substrate for Claude, exposed through a scoped MCP interface." CRUD is the mechanism; retrieval, organization, and memory are the product. `forge_context` (§5.2) and session/decision capture (§9) are the parts of this phase that are actually new *product* surface — the CRUD tools exist to support them, not the other way around.

Excluded from this phase, with the evidence-based reason:

- **`services/secrets/service.py` (the vault) and everything downstream of `get_vault_crypto()`.** `get_secret(..., reveal=True)` returns plaintext decrypted via the single symmetric `FORGE_MASTER_KEY`-derived key protecting the *entire* vault — there is no per-secret or per-scope key. One over-broad or compromised MCP tool call could exfiltrate every stored password, API key, and SSH key in one loop over `list_secrets()` + `get_secret(reveal=True)`. Unlike Notes/Documents (content the user already intends to discuss with an AI, per Model Playground/Prompt Studio's existing purpose), Secrets content is meant to *never* leave the vault's boundary. `forge:secrets` exists as a named scope in the authorization model (§4.4) so the boundary is visible and extensible, but zero tools in this phase check for it.
- **`services/crypto/service.py`.** Lower risk than Secrets (stateless, no persistence) but its functions accept/return raw key material, passphrases, and plaintext as plain arguments — exposing it via MCP would put raw RSA private keys or AES passphrases into MCP transport logs/conversation transcripts if a user ever pasted one through Claude. Deferred, not partially exposed.
- **Settings, backup/import/export, master-password operations (`api/routes/settings.py`, `api/routes/auth.py`).** These control the security posture of the whole instance (master password rotation invalidates every session token — `core/security.py`); an MCP tool that could change them would let a compromised Claude session lock the owner out or weaken the instance. No product need for Claude to manage these is stated in the brief.
- **Embeddings / vector search.** The existing SQLite FTS5 virtual tables (`notes_fts`, `documents_fts` — external-content, trigger-synced, `alembic/versions/0001`/`0002`) already provide phrase-prefix full-text search across Notes and Documents, and `services/knowledge/service.py`'s `list_knowledge()` already provides tag/project/type-filtered aggregation on top of it. Nothing in the repository (no `docs/Roadmap.md` gap, no ADR, no existing partial implementation) indicates FTS5 is insufficient for `forge_search`/`forge_context`. ADR-0015 ("Knowledge Hub reuses FTS5 rather than building a new index") is the direct precedent this phase follows again.
- **A new "memory database."** Session/decision capture (§9) is Notes with a reserved tag convention. No new model, table, or migration beyond `mcp_tokens` (§4.3, §4 of `04_DATABASE.md`) is introduced by this phase.
- **OAuth 2.0 for MCP client authentication.** Claude Code supports OAuth for remote MCP servers, but it requires standing up an authorization server, which is disproportionate for a single-tenant, self-hosted instance whose entire security model is already "one operator, one master key." A static, revocable bearer token (§4) fits the existing trust model; OAuth is recorded as a future hardening option in §7's open questions, not built here.

## 3. MCP transport

**Decision: Streamable HTTP**, per the current MCP specification (2025-11-25 revision; HTTP+SSE was deprecated March 2025 and should not be built against for a new server). Mounted at `/mcp` inside the FastAPI app, reachable through the existing nginx reverse proxy the same way `/api/*` is today (`docker/nginx.conf`).

**Rejected: local stdio.** Stdio requires the MCP client (Claude Code / Claude Desktop) to spawn Forge's MCP server as a local subprocess with direct filesystem access — this bypasses the entire cookie/token auth model this phase is building, only works when Claude runs on the same machine as the Forge backend, and does not match Forge's actual deployment model, which (per `docs/Deployment.md`) is explicitly designed to be reached from other devices on a LAN or through a tunnel, not just localhost. A persistent, remotely-reachable "second brain" needs a persistent, remotely-reachable transport.

**Client configuration** (external fact, Claude Code docs, fetched live during this planning session): a remote Streamable HTTP MCP server is added with `claude mcp add --transport http <name> <url> --header "Authorization: Bearer <token>"`. This is the intended connection method for Phase 11's server once a token exists (§4).

**Deployment implications** (§ builds on Docker research):
- Local development: `uvicorn --reload` already serves the whole FastAPI app; `/mcp` is reachable at `http://localhost:8000/mcp` with no new dev process, matching `docs/Development.md`'s existing "no dev-mode compose profile" convention.
- Production: `docker/nginx.conf` gains one location block, `location /mcp { proxy_pass http://backend:8000/mcp; ... }`, mirroring the existing `/api/*` block including the `Upgrade`/`Connection` headers already present for HMR (Streamable HTTP's SSE-flavored responses benefit from the same no-buffering treatment). No TLS is terminated by Forge itself today (`docs/Deployment.md` — "Forge doesn't terminate TLS... put it behind Caddy/Traefik/Cloudflare Tunnel/Tailscale"); the MCP endpoint inherits whatever TLS boundary the operator already puts in front of Forge. This is documented, not silently assumed — see `03_BACKEND.md` §5 and the Docker/production risk in `08_ACCEPTANCE.md`.
- `FORGE_MCP_ENABLED` (default `false`) gates whether `/mcp` is mounted at all, so instances that don't want this surface exposed don't get it merely by upgrading.

## 4. Authentication & authorization

### 4.1 Why the existing session model cannot be reused as-is

`backend/app/core/security.py`'s session tokens are **stateless HMACs** (`"<expiry>.<hmac>"`, no server-side session table) signed with a key derived from `FORGE_MASTER_KEY` + the master password's Argon2id hash. They are delivered exclusively via an `httponly` `Set-Cookie` (`forge_session`), verified by `require_auth`/`AuthDep` (`backend/app/api/deps.py`) which is applied as a router-level dependency on 16 of 17 route modules. This works because there is exactly one user and exactly one trust boundary: the browser holding a valid cookie.

An MCP client is not a browser — it sends an `Authorization` header, not a cookie, and a persistent MCP connection is expected to remain valid across many Claude sessions over weeks or months, independent of whether a human has the Forge UI open. Reusing the cookie session directly (e.g. by having Claude somehow acquire and replay a session cookie) was considered and rejected: it would require exposing raw session tokens outside the browser's cookie jar, and — because the existing token has no identity or scope, only a validity window — it would give the MCP connection **exactly** the same blanket access as the browser, with no way to scope it down to `forge:read` or exclude Secrets. This directly conflicts with §2's requirement to exclude Secrets structurally.

### 4.2 Decision: a second, parallel bearer-token scheme

A new `Authorization: Bearer <token>` scheme, checked by a new dependency (`require_mcp_auth`, `backend/app/mcp/auth.py`) applied only to `/mcp` routes — **not** a replacement for `AuthDep`, which continues to govern the REST API and browser UI unchanged. The two schemes coexist; a request to `/api/*` still needs the cookie, a request to `/mcp` needs the bearer token.

### 4.3 Token model

Forge has no existing per-credential revocation mechanism — session tokens are only invalidated wholesale by rotating the master password (see §4.1). Phase 11 introduces the first individually-revocable credential in the codebase, and — per owner review of this spec (2026-08-18) — the bootstrap credential and the credential Claude actually uses are **two distinct, non-interchangeable things**. A bootstrap token sitting permanently in deployment config, usable by Claude as its everyday credential, would be a permanent root credential undermining the entire point of a revocable/scoped token model. The flow is:

```text
FORGE_MCP_BOOTSTRAP_TOKEN
        │
        ▼
one-time/admin provisioning credential
   (accepted ONLY by the token-provisioning route, never by /mcp itself)
        │
        ▼
POST /api/mcp/tokens  →  creates a persistent McpToken row, returns raw token ONCE
        │
        ▼
Claude is configured with the persistent token (never the bootstrap token)
        │
        ├── revoke  (DELETE /api/mcp/tokens/{id})
        └── rotate  (revoke old + provision new — no in-place rotation in this phase)
```

- New model `McpToken` (`backend/app/models/mcp_token.py`, table `mcp_tokens`): `id` (UUID hex, `new_id()` per `models/base.py` convention), `name` (human label, e.g. "Claude Code — dev laptop"), `token_hash` (the token is generated once, shown once, stored only as a salted hash — never the plaintext, mirroring how `AppConfig.master_password_hash` never stores the master password itself), `scopes` (comma-separated or JSON list of `read`/`write`/`delete`; `secrets` is a valid stored value but no tool checks for it in this phase), `created_at`, `last_used_at` (nullable — see the throttling rule below), `revoked_at` (nullable — presence means revoked).
- **Bootstrap credential (`FORGE_MCP_BOOTSTRAP_TOKEN` / `_FILE`, mirroring the existing `master_key`/`master_key_file` Docker-secret convention)** authenticates to exactly one thing: `POST /api/mcp/tokens` (§4.3.1 below). It is checked by a separate dependency, `require_bootstrap_auth`, which is **never** part of `require_mcp_auth`'s accepted-credential set — a request to any MCP tool or resource presenting the bootstrap token instead of a persistent token is rejected exactly as if no credential were presented at all. This is the structural guarantee that the bootstrap token cannot become Claude's runtime credential by accident.
- **`mcp_bootstrap_enabled: bool = True`** (new config field) — the operator is expected to set this `false` (or unset the token/file) once at least one persistent token has been provisioned, closing the provisioning route entirely. `require_bootstrap_auth` checks this flag first, before comparing the token, so disabling it is a true kill switch, not merely a recommendation. Documented as a required post-provisioning step in `docs/Security.md`, and checked by a Milestone 1 acceptance test (§new AC below) that the provisioning route is unreachable once disabled.
- **This exists in Milestone 1, not deferred to Milestone 5.** The provisioning route is the minimum needed to make the Milestone 1 vertical slice (`09_IMPLEMENTATION_TASKS.md` — connect, authenticate, handshake) actually usable end-to-end without hand-inserting a database row. Milestone 5 adds only the *polish* layer on top of what already exists: rotation ergonomics and (pending the owner's §4.6 decision) a UI.
- Revocation is immediate: `require_mcp_auth` checks `revoked_at IS NULL` on every request (no caching that would delay revocation taking effect).
- **`last_used_at` write-throttling — explicit decision.** SQLite is a single-writer database; updating `last_used_at` on every `/mcp` request would put a write on the hot path of every tool call, including pure reads, for a field whose only purpose is operator visibility ("is this token still in use?"). Decision: `require_mcp_auth` updates `last_used_at` **only if it is `NULL` or more than 5 minutes stale** — a coalesced/throttled write, not a per-request one. This bounds write frequency to at most once per 5-minute window per active token regardless of call volume, and is exact enough for its actual purpose (staleness detection for revocation hygiene, not precise usage analytics).

#### 4.3.1 `POST /api/mcp/tokens` (new REST route, not an MCP tool)

Deliberately a REST route under the existing `/api/*` surface, not an MCP tool exposed to Claude — provisioning a credential is an administrative action the human owner performs (via `curl`/an admin script/a future UI), never something Claude calls on itself. Accepts **either** a valid `forge_session` cookie (`AuthDep` — the owner, logged into the Forge UI, provisioning a token for their own Claude session) **or** a valid, enabled bootstrap token (`require_bootstrap_auth` — for headless/first-run provisioning before any UI session exists, e.g. a Docker entrypoint script). Input: `{ name: string, scopes: string[] }`. Output: `{ id, name, scopes, token: "<raw token, shown exactly once>" }` — the raw value is never retrievable again after this response. Companion routes: `GET /api/mcp/tokens` (list — id/name/scopes/created_at/last_used_at/revoked_at, never `token_hash`), `DELETE /api/mcp/tokens/{id}` (revoke — sets `revoked_at`, does not hard-delete the row, so revocation history survives for audit purposes).

### 4.4 Scopes

| Scope | Grants | Used by (this phase) |
|---|---|---|
| `forge:read` | `forge_search`, `forge_context`, `forge_get_note`, `forge_get_document`, `forge_list_projects`, `forge_get_project` | Milestones 2–4 |
| `forge:write` | `forge_create_note`, `forge_update_note`, `forge_create_document`, `forge_update_document`, `forge_create_project`, `forge_update_project`, `forge_link_items`, `forge_unlink_items`, `forge_capture_session`, `forge_capture_decision` | Milestones 2–4 |
| `forge:delete` | `forge_delete_note`, `forge_delete_document` | Milestone 2 |
| `forge:secrets` | *(reserved — no tool in this phase requires or checks it)* | none |

A token's `scopes` list is checked per-tool at the top of every handler (`require_scope("forge:write")` style guard, consistent with how `AuthDep` is applied per-router today) — not just at connection time, so a `forge:read`-only token gets a clean MCP-level authorization error on any write attempt rather than the tool silently no-op-ing.

### 4.5 Audit logging

**Correction from the original draft, per owner review:** `backend/app/services/activity.py`'s `record()` function is **not** called a second time by the MCP layer. Repository research already established that `notes_service.create_note`/`update_note`/`delete_note` (and the Documents/Projects equivalents) call `activity.record(...)` themselves, internally, as part of the same service function the MCP tool handler calls. If an MCP tool handler *also* called `activity.record(...)` after invoking the service, every MCP-originated mutation would produce **two** `ActivityLog` rows — one from the service's own call (mislabeled `source="ui"` by default) and one from the MCP layer. That is a duplicate-record bug baked into the original plan, now corrected:

- Every service function that currently calls `activity.record(...)` internally (`create_note`, `update_note`, `delete_note`, the Documents/Projects equivalents) gains one additive keyword parameter, `source: str = "ui"`, threaded straight through to the `activity.record(...)` call already inside it. This is a non-breaking signature change — every existing caller (routes, tests) is unaffected by the default.
- MCP tool handlers pass `source="mcp"` into the service call itself (e.g. `notes_service.create_note(session, data, source="mcp")`) and never call `activity.record(...)` directly. The MCP layer produces **exactly one** `ActivityLog` row per mutation, identical in shape to the REST-originated row except for `source`.
- `ActivityLog` currently has no `source` field at all (everything today is implicitly "the one user via the UI"); Phase 11 adds one additive column, `source` (server-side default `"ui"` for existing rows and every existing call site, `"mcp"` only where a service call explicitly passes it).
- Reads are **not** logged into `ActivityLog` (it has never recorded `viewed` actions for GET-equivalent operations at the route layer either, despite `ActivityAction` defining a `viewed` enum member — confirmed unused for reads in current routes); Phase 11 does not change that convention by default, but see `08_ACCEPTANCE.md` §6 for the open question of whether AI-driven reads deserve different treatment.
- What must never be logged: secret values (moot — Secrets is out of scope), full note/document content (only the existing `summary` truncated-to-300-chars pattern), or the raw bearer token (bootstrap or persistent).

### 4.6 Open question flagged for the owner

Whether Milestone 5 needs a minimal Settings-page UI for creating/revoking MCP tokens, or whether a CLI/admin script is sufficient for a single-operator instance, is **not decided by this planning session** — it depends on how comfortable the owner is running a one-off Python script against the production container versus wanting a UI parity with how Secrets/folders are managed today. See `08_ACCEPTANCE.md` §6 (Open Questions). (The provisioning *mechanism*, `POST /api/mcp/tokens`, is decided and built in Milestone 1 per §4.3.1 regardless of this open question — what remains open is only whether a human-facing UI wraps it.)

### 4.7 Resource authorization is a service-layer property, not a scope property — added per owner review

The MCP scope model (§4.4) answers "is this token allowed to call this *class* of tool at all" — it does not, by itself, answer "is this token allowed to touch *this specific* project/note/document." In Forge's current single-user model those two questions happen to have the same answer (there is exactly one trust boundary, so any `forge:read` token can legitimately read any project), but the *mechanism* by which that access is granted must not be "the caller supplied a valid-looking ID." Every MCP tool handler in this phase already goes through a service function (`projects_service.get_project`, `notes_service.get_note`, etc.) that performs its own existence/lookup check and raises not-found on a bad ID — **never** a raw `session.get(Model, id)` bypassing that layer (see §5.3 below). This is stated here as an explicit, permanent architectural rule, not merely a byproduct of code reuse: scope answers "what kind of thing," the service layer answers "which specific thing, and does it actually exist" — and that second check must never be replaced by "possession of an ID implies authorization." This is what would let Forge evolve past single-user without every MCP tool having to be rewritten — the service layer is already the seam where a future per-user/per-project ownership check would be added, and Phase 11 must not build anything that bypasses that seam.

### 4.8 Milestone 1 scope adjustment — provisioning route included

Per §4.3/§4.3.1, Milestone 1 (`09_IMPLEMENTATION_TASKS.md`) now includes the `McpToken` provisioning REST route (`POST/GET/DELETE /api/mcp/tokens`) as a required task, not deferred to Milestone 5 — Milestone 1's vertical slice cannot be exercised end-to-end (bootstrap → real credential → connect) without it. Milestone 5 retains only rotation ergonomics and the still-open UI question (§4.6).

## 5. MCP tool design — summary (full contract in `06_API.md`)

Deliberately small and semantic, not a mechanical mirror of the 17 REST route modules. Full per-tool schemas, validation, and error behavior are in `06_API.md`. Summary:

| Tool | Class | Scope | Milestone |
|---|---|---|---|
| `forge_search` | read | `forge:read` | 3 |
| `forge_context` | read | `forge:read` | 3 |
| `forge_get_note` | read | `forge:read` | 2 |
| `forge_create_note` | write | `forge:write` | 2 |
| `forge_update_note` | write | `forge:write` | 2 |
| `forge_delete_note` | delete | `forge:delete` | 2 |
| `forge_get_document` | read | `forge:read` | 2 |
| `forge_create_document` | write | `forge:write` | 2 |
| `forge_update_document` | write | `forge:write` | 2 |
| `forge_delete_document` | delete | `forge:delete` | 2 |
| `forge_list_projects` | read | `forge:read` | 2 |
| `forge_get_project` | read | `forge:read` | 2 |
| `forge_create_project` | write | `forge:write` | 2 |
| `forge_update_project` | write | `forge:write` | 2 |
| `forge_link_items` | write | `forge:write` | 3 |
| `forge_unlink_items` | write | `forge:write` | 3 |
| `forge_capture_session` | write | `forge:write` | 4 |
| `forge_capture_decision` | write | `forge:write` | 4 |

**Deliberately not included**: `forge_delete_project` (Projects unscope rather than delete children on the existing `delete_project`, which is a wide-blast-radius operation for an LLM to trigger with no additional review — if wanted later, it is a Milestone-5-or-later addition, not default surface), any folder/tag-management tools beyond what `forge_link_items`/tagging-via-note-update needs, and anything mechanically mirroring Secrets/Settings/Crypto/Converters/Ingest/Generators/Model Playground/Prompt Studio routes — none of those are "knowledge substrate" capabilities per the brief's product framing.

### 5.1 `forge_search`

Calls `notes_service.search_notes(query)` and `documents_service.search_documents(query)` directly — **not** `services/search/service.py`'s `global_search()`, because `global_search` also queries and returns Secrets (name-only, but still a leak of the vault's existence/contents-by-name to any MCP client). Building `forge_search` on the two FTS functions directly enforces the Secrets exclusion structurally, at the call-site, rather than by trusting a post-hoc filter. `forge_search` accepts an optional `project_id` and threads it into `search_notes`/`search_documents` exactly as described in §5.2 below — the same constrained-at-the-query, not filtered-after, principle applies here too.

### 5.2 `forge_context`

The Claude-oriented aggregate retrieval tool. Composes, for a given `topic` (free text) and optional `project_id`:
- The project record (`projects_service.get_project`) if `project_id` given.
- Top FTS5 matches from Notes and Documents for `topic` (same functions as `forge_search`).
- Tags on those matched items and on the project, via `knowledge_service.list_knowledge`/tag lookups.
- Existing links between the matched items, via a **batch** link lookup (see below).

**Project scoping — corrected per owner review.** The original draft's plan was: run an unscoped FTS query (top ~50 results), then filter to `project_id` in application code. That is wrong for two reasons: it can silently produce incomplete context (a project with more than ~50 matching items across Notes+Documents could lose relevant results to the global cap before project filtering even runs), and it does unnecessary retrieval. Corrected design: `notes_service.search_notes` and `documents_service.search_documents` both gain an additive `project_id: str | None = None` parameter, applied as an `AND notes.project_id = :project_id` (respectively `documents.project_id`) clause inside the existing FTS5 query, **before** the `LIMIT 50`/`LIMIT 50` cap is applied — so a project-scoped `forge_context`/`forge_search` call is constrained at the database query itself, not after retrieval. This is a small, additive signature change to two existing service functions (default `None` preserves every existing caller's behavior unchanged), not a new query mechanism. New acceptance criterion: see `08_ACCEPTANCE.md` AC13a.

**Batch link retrieval — corrected per owner review.** The original draft called `knowledge_service.list_links` once per matched item, which is an N+1 pattern (up to 50 notes + 50 documents = up to 100 individual queries for a single `forge_context` call). Corrected design: `services/knowledge/service.py` gains one additive, narrowly-scoped internal method, `list_links_for_items(session, items: list[tuple[str, str]]) -> dict[tuple[str, str], list[KnowledgeLinkView]]`, that retrieves links for a whole collection of `(item_type, item_id)` pairs in a single query (an `OR`-chain or `IN`-based match against `KnowledgeLink`'s normalized `source_type/source_id`/`target_type/target_id` columns, grouped by which input pair each result row belongs to). This does **not** change the public REST API or `GET /api/knowledge` — it is an internal service capability used only by `forge_context` in this phase. `forge_context`'s implementation task (`09_IMPLEMENTATION_TASKS.md` M3-T2) now depends on this method existing, not on N calls to the existing single-item `list_links`.

**Explicitly not included in `forge_context`'s v1 output**: "recent activity" as framed in the brief's example (a topic-filtered activity feed). `ActivityLog` has no full-text or topic-query capability — it only supports lookup by `entity_type`/`entity_id`. A per-result "recent activity for this specific note/document" enrichment (querying `ActivityLog` by the entity IDs already returned from the FTS match, not by topic) is feasible and is deferred to Milestone 4 as a documented enhancement once the base shape of `forge_context` is proven — it is not fabricated as a v1 field the underlying data can't actually support.

**Ranking**: whatever FTS5's built-in `rank` ordering already provides (`ORDER BY rank`, per the existing `search_notes`/`search_documents` queries) — no new ranking/scoring model is introduced.

### 5.3 `forge_get_note` — service method mandated, no ORM bypass (resolved per owner review)

The original draft left two implementation options open: a direct `session.get(Note, note_id)` in the MCP tool handler, or an additive `notes_service.get_note(...)` matching the pattern Documents already has. **Resolved: only the service-method option is permitted.** The architectural principle this whole phase is built on is `MCP → service → model`, never `MCP → ORM` — allowing even one tool handler to reach the ORM directly would make that handler a documented exception to the phase's own core premise, and exceptions like that are how "MCP calls the same service layer" quietly erodes into "MCP mostly calls the same service layer." `notes_service.get_note(session, note_id)` is a small, additive, 404-raising function matching `documents_service.get_document`'s existing shape exactly — there is no cost to requiring it. `06_API.md` and `03_BACKEND.md` are updated to state this as the only implementation.

## 6. CRUD safety

- **Destructive tools**: `forge_delete_note`, `forge_delete_document`. Both require an explicit `confirm: true` argument in the tool's input schema (the tool call fails with a validation error, not a silent no-op, if omitted) — the confirmation step lives in the MCP tool's input contract, not as a separate "propose then confirm" round trip, since MCP's synchronous request/response model has no notion of the server prompting the caller mid-call. This mirrors how a destructive CLI flag (`--force`) requires explicit intent rather than being implicit in the tool's existence.
- **Confirmation is structural, never inferred — per owner review, stated as a hard rule, not a guideline.** The MCP tool handler authorizes deletion if and only if the request's parsed, structured input contains the literal JSON `"confirm": true`. Nothing else counts: not the natural-language content of the surrounding Claude conversation, not a prior tool call in the same session, not a phrase like "yes delete it" appearing anywhere in context the MCP server has no visibility into anyway (the MCP server only ever sees the structured tool-call arguments, never the conversation). This is enforced by the input schema itself (`confirm` is a required field of type `const: true`, so a call missing it or passing `false` fails JSON Schema validation before the handler body runs at all) — there is no code path where a handler could be tempted to "interpret" intent, because malformed/absent confirmation never reaches handler code.
- **No soft delete exists to fall back on.** Notes and Documents are hard-deleted at the DB level (`await session.delete(...)`, no `deleted_at` column, no trash) — confirmed for both `notes_service.delete_note` and `documents_service.delete_document`. This phase does **not** add soft-delete to the underlying model (that would be a Notes/Documents feature change, out of scope for an MCP-interface phase) — the mitigation is entirely on the MCP side: `confirm: true`, scope-gating (`forge:delete` must be explicitly granted to a token, separate from `forge:write`), and an `ActivityLog` entry recording exactly what was deleted (title/summary, per the existing 300-char-summary convention) so the record of *what existed* survives even though the content does not.
- **Delete sequence — corrected per owner review to check existence before mutating anything.** The original draft called `purge_links_for` immediately, without first confirming the target exists — meaning a delete call against a bad ID could stage link deletions before the handler discovered there was nothing to delete. Corrected sequence, all four steps against the same `AsyncSession`:

  ```text
  1. target = await notes_service.get_note(session, note_id)   # raises not-found; NO mutation staged yet
  2. await knowledge_service.purge_links_for(session, "note", note_id)   # stages link deletes, no commit (existing service contract)
  3. await notes_service.delete_note(session, note_id, source="mcp")     # stages the note delete AND commits — one commit flushes both #2 and #3 together
  4. activity.record(...) already happened inside step 3 (source="mcp" threaded through, per §4.5) — no separate MCP-side audit call
  ```

  Because step 2 only stages pending changes on the session (per `purge_links_for`'s existing "no commit — caller commits" contract) and step 3's single `commit()` flushes everything pending on the session at once, steps 2–3 are already atomic in the existing service design — no new transaction-management code is needed, only reordering so existence is confirmed (step 1) before any mutation is staged (steps 2–3). If step 1 raises not-found, steps 2–4 never run and nothing is written. `forge_delete_document` follows the identical sequence against `documents_service`.
- **`forge_delete_note`/`forge_delete_document` MUST call `knowledge_service.purge_links_for(item_type, item_id)` before the delete**, exactly as `api/routes/notes.py`/`api/routes/documents.py` already do at the route layer — this is not optional cleanup, it prevents orphaned `knowledge_links` rows (§1 risk). MCP tool handlers replicate this orchestration explicitly, documented inline with a comment pointing at the route file it mirrors, since the service layer does not enforce it itself (this is an existing, documented architectural choice in Forge — see `services/knowledge/service.py`'s `purge_links_for` docstring — not something Phase 11 is introducing).
- **`forge_update_note`/`forge_update_document` are non-destructive** (partial updates via `model_dump(exclude_unset=True)`, same as the existing PATCH routes) and need no confirmation.
- **Archiving is offered as the safer default** where it fits: `forge_update_note`'s existing `archived` field (already part of `NoteUpdateIn`) lets Claude "soft remove" a note from default views without data loss — tool descriptions should steer Claude toward archive-then-delete-on-explicit-request rather than defaulting to delete for anything resembling "clean this up."
- **Idempotency**: create tools are not idempotent (no client-supplied idempotency key in this phase — matches existing REST routes, which also lack one). Update/delete tools are naturally idempotent at the HTTP-semantics level (deleting an already-deleted ID, or updating with the same values, produces the same end state) but will surface a 404-equivalent MCP error on a second delete of the same ID, not a silent success — consistent with `get_document`'s existing 404 behavior.

## 7. Required ADRs and architecture registry updates

- **New ADR**: "MCP server integrated into the Forge backend, not a separate process" (§1 of this doc, formalized).
- **New ADR**: "MCP authentication is a second bearer-token scheme, not reused browser sessions or OAuth" (§4 of this doc, formalized) — this is the kind of decision `09_CLAUDE_CODE_RULES.md` §3 flags as needing a `decisions/` entry (new cross-cutting security concept).
- **ADR-0004 ("interactive workflows, not automation") reconciliation.** Phase 11 is inherently about an external agent acting inside Forge outside a human's direct interactive session. The new ADRs above should explicitly reconcile with ADR-0004 (cite it, explain why an MCP-driven write is different from the automation ADR-0004 defaults against — chiefly: every MCP write is scoped, token-gated, audited, and initiated by a human's own Claude conversation, not a cron job or webhook), rather than silently overriding it.
- **`forge-docs/architecture/CAPABILITY_REGISTRY.md` / ADR-0008.** ADR-0008 (capability/panel registry generalization) is currently "Proposed, not Accepted," waiting for a second concrete use case beyond Phase 01's Panel Registry to justify promotion. MCP tools are a plausible second use case (both are "expose a capability under a name, with metadata, through a uniform interface"). This planning session does **not** promote ADR-0008 or build a registry — that would be scope creep beyond what Phase 11 needs (a flat Python dict mapping tool names to handlers is sufficient for ~18 tools). The connection is recorded here for whoever revisits ADR-0008 next, not acted on.
- **Roadmap**: `forge-docs/02_ROADMAP.md` §3 needs a new Phase 11 row once Authorized (not added by this planning session — the roadmap is currently frozen-phase history plus one TODO for owner ratification of ordering; adding an unauthorized phase's row is left for the Authorization step itself, consistent with how Phase 09 required explicit owner ratification before its row was added).

## 8. Audit logging — see §4.5.

## 9. Session / decision capture

`forge_capture_session` and `forge_capture_decision` are **thin wrappers around `forge_create_note`** (which itself wraps `notes_service.create_note`), not a new tool implementation or persistence model:

- `forge_capture_decision(summary, detail?, project_id?)` creates a Note titled `Decision: <summary>` (truncated to the existing 200-char title limit), body = `detail`, and applies a reserved tag `ai-decision` via `knowledge_service.add_tag` (tags are a pre-existing shared vocabulary — `models/knowledge.py`'s `Tag`/`NoteTagLink` — reusing it needs no schema change).
- `forge_capture_session(summary, detail?, project_id?)` creates a Note titled `Session <YYYY-MM-DD>: <summary>`, tagged `ai-session`.
- A later Claude session retrieves these exactly like any other knowledge: `forge_search`/`forge_context` naturally surface them (they're indexed in `notes_fts` like any note), or a future Milestone-4-or-later convenience could add a `tag_ids` filter shortcut — not built in this phase beyond what `knowledge_service.list_knowledge(tag_ids=[...])` already supports, which is sufficient (`forge_context` can pass the reserved tag names through its existing tag-lookup path).

This satisfies the brief's instruction to prefer reuse over "a new memory database" directly — there is no new table, no new model, and no new retrieval mechanism; only a tagging convention plus two thin, purpose-named tool wrappers so Claude doesn't have to remember the raw tag-string convention itself.

## 10. Cross-references

- [README.md](README.md)
- [03_BACKEND.md](03_BACKEND.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../decisions/0004-interactive-workflows-not-automation.md](../../decisions/0004-interactive-workflows-not-automation.md)
- [../../decisions/0008-capability-registry-direction.md](../../decisions/0008-capability-registry-direction.md)
- [../../decisions/0010-fdk-verification-automation-exception.md](../../decisions/0010-fdk-verification-automation-exception.md)
- [../../decisions/0011-model-playground-provider-credential-security.md](../../decisions/0011-model-playground-provider-credential-security.md)
- [../../decisions/0015-knowledge-hub-reuses-fts5.md](../../decisions/0015-knowledge-hub-reuses-fts5.md)
- [../../architecture/CAPABILITY_REGISTRY.md](../../architecture/CAPABILITY_REGISTRY.md)
