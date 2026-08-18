# Phase 11 — MCP Contract (Tools & Resources)

> **Purpose:** The precise MCP tool and resource contract — this is the "API" this phase ships, in the sense `06_API.md` normally documents REST endpoints.
> **Status:** Draft — pending Authorization.
> **Last Updated:** 2026-08-18

---

## 0. Conventions used below

- **Underlying service** cites the exact function from the backend research (`services/<domain>/service.py`), so implementation has no ambiguity about what to call.
- **Output shape** is "full" (returns the same fields the REST `*Out` schema would) or "summarized" (a reduced projection built for MCP, to keep tool outputs small — search/context results are summarized; single-item gets are full).
- All tools validate input against a JSON Schema derived from the existing Pydantic `*In` schemas where one exists (`schemas/notes.py`, `schemas/documents.py`, etc.) — no duplicate validation model is hand-written where an existing one already fits.
- All error responses use MCP's standard tool-error shape with a message drawn from the same exceptions the REST layer already raises (`UnauthorizedError`, 404-equivalent "not found", Pydantic validation errors) — no new error taxonomy.

## 1. Read tools

### `forge_search`

| | |
|---|---|
| Purpose | Full-text search across Notes and Documents (never Secrets). |
| Class / scope | read / `forge:read` |
| Input | `{ query: string (required, 1-200 chars), types?: ("note"\|"document")[], project_id?: string }` |
| Output | Summarized list: `[{ id, type, title, snippet, project_id, updated_at }]`, capped at 50 per type (matches the existing FTS query's `LIMIT 50`). |
| Underlying service | `notes_service.search_notes(session, query, project_id=...)`, `documents_service.search_documents(session, query, project_id=...)` — called directly, **not** `search_service.global_search` (§5.1 of `01_SPEC.md` — excludes Secrets structurally). `project_id`, when given, is applied inside the FTS query itself (before the `LIMIT 50` cap), not as a post-filter — see `01_SPEC.md` §5.2. |
| Underlying REST API | None directly — analogous to `GET /api/search` but deliberately narrower (no Secrets). |
| Validation | `query` non-empty, ≤200 chars (guards against pathological FTS phrase-prefix input). |
| Errors | Empty `query` → validation error. No results → empty array, not an error. |
| Idempotent | Yes (read-only). |
| Destructive | No. |
| Confirmation | None. |

### `forge_context`

| | |
|---|---|
| Purpose | Claude-oriented aggregate retrieval: project + matched notes/documents + their tags + their existing links, for a topic. |
| Class / scope | read / `forge:read` |
| Input | `{ topic: string (required), project_id?: string }` |
| Output | `{ project: ProjectOut \| null, notes: [{id,title,snippet,tags,updated_at}], documents: [{id,title,snippet,tags,updated_at}], links: [{source_type,source_id,target_type,target_id}] }` — summarized, not full content (use `forge_get_note`/`forge_get_document` for full body once an item of interest is identified, to keep this tool's output bounded). |
| Underlying service | `projects_service.get_project` (if `project_id`), `notes_service.search_notes(..., project_id=...)`/`documents_service.search_documents(..., project_id=...)` (query-scoped, same correction as `forge_search`), `knowledge_service.list_knowledge`/tag lookups, `knowledge_service.list_links_for_items(session, items)` — **one batch call**, not one `list_links` call per matched item (N+1 correction, `01_SPEC.md` §5.2, `03_BACKEND.md` §2.1). |
| Underlying REST API | None directly — new composition, analogous in spirit to `GET /api/knowledge` but topic-driven rather than filter-driven. |
| Validation | `topic` non-empty. `project_id`, if given, must resolve via `get_project` or the tool returns a clear "project not found" error rather than silently ignoring the filter. |
| Errors | Invalid `project_id` → explicit error (not silently dropped — an LLM given a stale ID should be told, not given unfiltered results it will misattribute to that project). |
| Idempotent | Yes. |
| Destructive | No. |
| Confirmation | None. |
| Note | Does not include topic-filtered "recent activity" in v1 — see `01_SPEC.md` §5.2. |

### `forge_get_note`

| | |
|---|---|
| Purpose | Full content of one note. |
| Class / scope | read / `forge:read` |
| Input | `{ note_id: string }` |
| Output | Full: `{id, title, content, color, project_id, pinned, archived, pos_x, pos_y, width, height, z_index, created_at, updated_at}` — the existing `NoteOut` shape. |
| Underlying service | `notes_service.get_note(session, note_id)` — **required**, not optional. Notes currently has no dedicated get function (Documents does); this phase adds a one-line, 404-raising addition matching `documents_service.get_document`'s exact shape. A direct `session.get(Note, note_id)` in the tool handler is **not permitted** — the `MCP → service → model` principle admits no ORM-bypass exceptions (`01_SPEC.md` §5.3, resolved per owner review). |
| Errors | Unknown ID → not-found error. |
| Idempotent | Yes. Destructive | No. Confirmation | None. |

### `forge_get_document`

| | |
|---|---|
| Purpose | Full content of one document. |
| Class / scope | read / `forge:read` |
| Input | `{ document_id: string }` |
| Output | Full `DocumentOut` shape (`id, title, content, pinned, project_id, created_at, updated_at`). |
| Underlying service | `documents_service.get_document(session, document_id)` — already raises 404-equivalent on missing. |
| Idempotent | Yes. Destructive | No. Confirmation | None. |

### `forge_list_projects`

| | |
|---|---|
| Purpose | List projects (with counts) for orientation/navigation. |
| Class / scope | read / `forge:read` |
| Input | `{ archived?: boolean = false }` |
| Output | `[{id, name, description, color, archived, note_count, document_count}]` (secret_count omitted — Secrets out of scope, would leak vault size). |
| Underlying service | `projects_service.list_projects(session, archived=...)` — `secret_count` field from `ProjectCounts` is dropped at the MCP output-shaping step, not exposed. |
| Idempotent | Yes. Destructive | No. Confirmation | None. |

### `forge_get_project`

| | |
|---|---|
| Purpose | Single project detail with counts. |
| Class / scope | read / `forge:read` |
| Input | `{ project_id: string }` |
| Output | Same shape as one list item above, full detail. |
| Underlying service | `projects_service.get_project(session, project_id)`. |
| Errors | Unknown ID → not-found. |
| Idempotent | Yes. Destructive | No. Confirmation | None. |

## 2. Write tools

### `forge_create_note`

| | |
|---|---|
| Purpose | Create a note. |
| Class / scope | write / `forge:write` |
| Input | `{ title: string(≤200), content?: string, color?: string(≤20), project_id?: string }` — mirrors `NoteCreateIn`; `pos_x/pos_y/width/height` are omitted from the MCP input (UI-placement concerns an LLM has no meaningful input for) and left to their existing model defaults. |
| Output | Full `NoteOut` of the created row. |
| Underlying service | `notes_service.create_note(session, NoteCreateIn(...), source="mcp")` — `source` threads into the service's own internal `activity.record(...)` call; the tool handler does not call `activity.record` itself (`01_SPEC.md` §4.5). |
| Validation | Same as `NoteCreateIn` (title required, ≤200 chars). Unknown `project_id` → not-found error, not a silently-orphaned note. |
| Errors | Validation error on bad input; not-found on bad `project_id`. |
| Idempotent | No (repeated calls create distinct notes — matches existing REST `POST` semantics). |
| Destructive | No. Confirmation | None. |
| Audit | `ActivityLog` entry, `source="mcp"`, action `created`. |

### `forge_update_note`

| | |
|---|---|
| Purpose | Partial update of a note, including archive/pin toggling. |
| Class / scope | write / `forge:write` |
| Input | `{ note_id: string, title?, content?, color?, project_id?, pinned?, archived?, z_index? }` — mirrors `NoteUpdateIn`, all fields optional, only supplied fields change (`exclude_unset=True`, matching existing PATCH semantics). |
| Output | Full `NoteOut` of the updated row. |
| Underlying service | `notes_service.update_note(session, note_id, NoteUpdateIn(...), source="mcp")`. |
| Errors | Unknown `note_id` → not-found. |
| Idempotent | Yes (same input twice = same end state). |
| Destructive | No (archiving is reversible via a second update). Confirmation | None. |
| Audit | `ActivityLog`, `source="mcp"`, action `updated`. |

### `forge_delete_note`

| | |
|---|---|
| Purpose | Permanently delete a note. |
| Class / scope | delete / `forge:delete` |
| Input | `{ note_id: string, confirm: true }` — `confirm` is a required literal `true` (JSON Schema `const: true`); omission or `false` fails schema validation before the handler body runs at all, and before any DB access. Confirmation is never inferred from conversation context — the handler only ever sees this structured argument (`01_SPEC.md` §6). |
| Output | `{ deleted: true, id: note_id }`. |
| Underlying service | Sequenced, existence-checked, atomic (`01_SPEC.md` §6, `03_BACKEND.md` §2): 1) `notes_service.get_note(session, note_id)` — raises not-found, no mutation staged; 2) `knowledge_service.purge_links_for(session, "note", note_id)` — stages, no commit; 3) `notes_service.delete_note(session, note_id, source="mcp")` — stages the delete and commits, flushing steps 2 and 3 together in one transaction. Replicates `api/routes/notes.py`'s existing delete orchestration with an added existence check the route layer itself doesn't need (the route's URL path already 404s on a bad ID before reaching the handler; an MCP tool handler must do that check explicitly). |
| Errors | Unknown `note_id` → not-found from step 1, before any link purge is staged. Missing/false `confirm` → validation error naming the required field. |
| Idempotent | Delete-of-already-deleted → not-found error, not a silent success. |
| Destructive | **Yes — irreversible, no trash.** Confirmation | **Required** (`confirm: true`). |
| Audit | `ActivityLog`, `source="mcp"`, action `deleted`, summary = the note's title (never full content). |

### `forge_create_document` / `forge_update_document` / `forge_delete_document`

Identical shape to the Notes trio above, substituting `documents_service.create_document(..., source="mcp")` / `update_document(..., source="mcp")` / the same 4-step existence-checked delete sequence (`documents_service.get_document` → `purge_links_for(session, "document", document_id)` → `documents_service.delete_document(session, document_id, source="mcp")`), `DocumentCreateIn`/`DocumentUpdateIn`. `forge_create_document`'s `content` field is HTML (matches the existing rich-text editor content format — Claude-authored content must be valid HTML, not Markdown, or the Documents editor will render it incorrectly; tool description must say this explicitly).

### `forge_list_projects` write counterparts

### `forge_create_project`

| | |
|---|---|
| Purpose | Create a project. |
| Class / scope | write / `forge:write` |
| Input | `{ name: string, description?: string, color?: string, default_provider?: string, default_model?: string }` — mirrors `ProjectCreateIn`. |
| Output | Full project detail (§1 shape). |
| Underlying service | `projects_service.create_project(session, ProjectCreateIn(...), source="mcp")`. |
| Idempotent | No. Destructive | No. Confirmation | None. |
| Audit | `ActivityLog`, `source="mcp"`, action `created`. |

### `forge_update_project`

| | |
|---|---|
| Purpose | Update project fields, including `archived`. |
| Class / scope | write / `forge:write` |
| Input | `{ project_id, name?, description?, color?, archived?, default_provider?, default_model? }`. |
| Output | Full project detail. |
| Underlying service | `projects_service.update_project(session, project_id, ProjectUpdateIn(...), source="mcp")`. |
| Errors | Unknown `project_id` → not-found. |
| Idempotent | Yes. Destructive | No. Confirmation | None. |
| Audit | `ActivityLog`, `source="mcp"`, action `updated`. |

**No `forge_delete_project` in this phase** — see `01_SPEC.md` §5, "deliberately not included."

## 3. Knowledge graph tools

### `forge_link_items`

| | |
|---|---|
| Purpose | Create an explicit link between two knowledge items. |
| Class / scope | write / `forge:write` |
| Input | `{ source_type: "note"\|"document", source_id: string, target_type: "note"\|"document", target_id: string }` |
| Output | The created `KnowledgeLinkView` (`{id, source_type, source_id, target_type, target_id, created_at}`). |
| Underlying service | `knowledge_service.create_link(session, source_type, source_id, target_type, target_id)` — service already normalizes pair order, so A→B and B→A resolve to the same row; re-linking an existing pair should surface that as "already linked," not a duplicate-row error leaking implementation detail. |
| Errors | Either ID not found → not-found error naming which side. Self-link (`source_id == target_id` and same type) → validation error. |
| Idempotent | Effectively yes (re-linking returns the existing link, per the service's normalization). |
| Destructive | No. Confirmation | None. |

### `forge_unlink_items`

| | |
|---|---|
| Purpose | Remove a link (does not delete the linked items). |
| Class / scope | write / `forge:write` |
| Input | `{ link_id: string }` |
| Output | `{ unlinked: true, id: link_id }`. |
| Underlying service | `knowledge_service.delete_link(session, link_id)`. |
| Errors | Unknown `link_id` → not-found. |
| Idempotent | No (second call → not-found, matches delete semantics generally). |
| Destructive | Low-risk (removes an association, not content) — no `confirm` field required, unlike item deletion. |

## 4. Memory workflow tools (Milestone 4)

### `forge_capture_decision` / `forge_capture_session`

| | |
|---|---|
| Purpose | Persist an important decision or session summary as retrievable knowledge. |
| Class / scope | write / `forge:write` |
| Input | `{ summary: string(≤180, leaves room for the "Decision: "/"Session <date>: " prefix within the 200-char title limit), detail?: string, project_id?: string }` |
| Output | Full `NoteOut` of the created note, including the applied tag. |
| Underlying service | `notes_service.create_note(..., source="mcp")` + `knowledge_service.add_tag(session, "note", note.id, name="ai-decision"|"ai-session", color=<reserved>)` — see `01_SPEC.md` §9. |
| Errors | Same as `forge_create_note`. |
| Idempotent | No. Destructive | No. Confirmation | None. |
| Audit | `ActivityLog`, `source="mcp"`, action `created`, entity_type `note` — logged once, inside `create_note`, not a second time by this tool handler. |
| Discoverability requirement | A note created by either of these tools must be retrievable by an ordinary later `forge_search`/`forge_context` call — no special-cased retrieval path. This is the acceptance test that proves memory capture is genuinely integrated into the knowledge substrate rather than a parallel storage mechanism (`08_ACCEPTANCE.md` AC14/AC15). |

## 4a. Token provisioning (REST, not an MCP tool)

`POST /api/mcp/tokens`, `GET /api/mcp/tokens`, `DELETE /api/mcp/tokens/{id}` — full contract in `01_SPEC.md` §4.3.1. Documented here for completeness of "the contract this phase ships," but these are ordinary REST routes under the existing `/api/*` surface, authenticated by `AuthDep` (browser session) or `require_bootstrap_auth` (bootstrap token, provisioning only) — **never** callable as an MCP tool, and never reachable via `require_mcp_auth`. This is a deliberate asymmetry: Claude can use a persistent token, but cannot mint or revoke tokens for itself.

## 5. Resources

**Decision: expose exactly two resources — `forge://projects` and `forge://projects/{id}`.** Projects are the natural, small, stable navigational root (bounded count, unlike Notes/Documents which can be numerous) — a client that auto-discovers resources gets a cheap orientation view without Claude needing to know to call `forge_list_projects` first.

**Rejected: `forge://notes/{id}`, `forge://documents/{id}`, `forge://knowledge/{id}` as individually-addressable resources.** Notes and Documents are numerous and per-item resources would either require enumerating all of them (poor for auto-discovery, and a potential context-flooding risk if a client eagerly loads every discovered resource) or would only be reachable by an ID the client already has from a tool call — at which point `forge_get_note`/`forge_get_document` already serve the need with no duplicate code path. `forge://knowledge/{id}` has no natural referent — "Knowledge" is a query/aggregation view (§1.3 of `01_SPEC.md`'s backend research), not an addressable entity with a stable ID.

| Resource | Source of truth | Auth | Update semantics | Auto-discovery |
|---|---|---|---|---|
| `forge://projects` | `projects_service.list_projects(archived=False)` | `forge:read` | Live query on each read, not cached/subscribed. | Yes — small, bounded list. |
| `forge://projects/{id}` | `projects_service.get_project(id)` | `forge:read` | Live query on each read. | On demand once an ID is known (from the list resource or a tool call). |

## 6. Prompts

No MCP prompts are defined in this phase. The brief's session/decision-capture workflow is served by ordinary tool calls (§4 above); no reusable prompt template was identified during repository analysis as adding value beyond what clear tool descriptions already provide. Revisit if Milestone 4 usage shows a repeated multi-tool sequence worth templating.

## 7. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
