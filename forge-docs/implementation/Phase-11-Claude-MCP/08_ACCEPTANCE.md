# Phase 11 — Acceptance Criteria

> **Purpose:** Objective, checkable acceptance criteria for Phase 11.
> **Status:** Draft — pending Authorization.
> **Last Updated:** 2026-08-18

---

## 1. Connectivity & auth

- [ ] AC1 — Given `FORGE_MCP_ENABLED=true` and a **persistent** MCP token provisioned via `POST /api/mcp/tokens`, Claude Code can connect to `/mcp` via Streamable HTTP using `claude mcp add --transport http`. (Corrected: "bootstrap or issued" was the original wording; per owner review, the bootstrap token must never be Claude's connection credential — see AC1a.)
- [ ] AC1a — Given the raw bootstrap token (`FORGE_MCP_BOOTSTRAP_TOKEN`), presenting it directly to `/mcp` (any tool, any resource) is rejected exactly as if no credential were presented — the bootstrap token authenticates `POST /api/mcp/tokens` only, never `/mcp` itself.
- [ ] AC1b — `POST /api/mcp/tokens`, authenticated with a valid bootstrap token, creates a persistent `McpToken` and returns the raw value exactly once; a subsequent `GET /api/mcp/tokens` for that token never returns the raw value, only metadata (id/name/scopes/timestamps).
- [ ] AC1c — Given `mcp_bootstrap_enabled=false`, `POST /api/mcp/tokens` rejects even a correct bootstrap token — the config flag is a true kill switch, checked before the token comparison.
- [ ] AC2 — Given `FORGE_MCP_ENABLED=false` (default), `/mcp` is unreachable through both direct backend access and the nginx proxy.
- [ ] AC3 — Given a missing or malformed `Authorization` header, every `/mcp` tool call is rejected before any service/DB access occurs.
- [ ] AC4 — Given a revoked persistent MCP token, the connection can no longer perform any protected operation, immediately (no caching delay).
- [ ] AC4a — `last_used_at` is updated at most once per 5-minute window per token under repeated/rapid tool calls (write-throttling behavior, not an update on every request) — verified by call count vs. write count, not merely by the field eventually being non-null.
- [ ] AC5 — Given a token with only `forge:read`, any write or delete tool call is rejected with the underlying data provably unchanged.

## 2. Knowledge CRUD

- [ ] AC6 — Given `forge:write`, Claude can create, read (full content), and update Notes and Documents through MCP tools, and the resulting rows are indistinguishable in the database from ones created via the REST API (same schema, same `ActivityLog` pattern except `source="mcp"`).
- [ ] AC7 — Given `forge:delete` and `confirm: true`, Claude can delete a Note or Document, and its `knowledge_links` rows are purged (no orphans left behind).
- [ ] AC7a — A delete call against a nonexistent `note_id`/`document_id` (with valid `confirm: true`) returns a not-found error and stages **zero** database changes — verified by asserting no `knowledge_links` rows are touched for an ID that never existed, proving the existence check runs before link purging, not after or concurrently.
- [ ] AC8 — Given `forge:delete` but `confirm` omitted or `false`, the delete tool call fails validation and nothing is deleted. No natural-language phrasing in surrounding context (which the MCP server cannot see regardless) can substitute for the literal structured field.
- [ ] AC9 — Given `forge:write`, Claude can create/update Projects, and Notes/Documents can be scoped to a project via MCP the same way the UI scopes them.
- [ ] AC10 — No MCP tool exposes `Secret` data, `secret_count`, or any crypto-service primitive, under any scope combination including a token that (mistakenly or maliciously) carries `forge:secrets`.

## 3. Search & context

- [ ] AC11 — Given a project, `forge_context` returns the project record, matching Notes/Documents, their tags, and their existing links — every field returned is backed by an existing Forge query (no fabricated/synthetic field).
- [ ] AC12 — `forge_search` never returns Secret names or metadata, even though the underlying `search_service.global_search` (which this tool deliberately does not call) does include them for the REST API's own `/api/search`.
- [ ] AC13 — An invalid `project_id` passed to `forge_context` produces an explicit error, not silently-unfiltered results.
- [ ] AC13a — Given a project with more matching Notes/Documents for a topic than the 50-per-type cap, `forge_context`/`forge_search` with `project_id` set returns results constrained to that project from the query itself — verified by a project containing >50 matching items across both types where an unscoped-then-filtered implementation would provably drop relevant results the query-scoped implementation does not.
- [ ] AC13b — `forge_context`'s link lookup issues a bounded, small number of queries regardless of result-set size (one batch query via `list_links_for_items`, not one per matched item) — verified by query-count assertion at, e.g., 50+50 matched items, not merely by correct output.

## 4. Memory workflows

- [ ] AC14 — A decision captured via `forge_capture_decision` in one Claude session is retrievable via `forge_search`/`forge_context` in a later, independent Claude session (proves cross-session continuity end-to-end, not just that the write succeeded).
- [ ] AC15 — Captured session/decision notes carry the reserved tag (`ai-decision`/`ai-session`) and are otherwise ordinary Notes — visible in the existing Notes board and Knowledge Hub UI with no special-casing required there.

## 5. Regression, audit, deployment

- [ ] AC16 — Existing Forge REST APIs (`/api/*`) behave unchanged — full existing backend test suite remains green.
- [ ] AC17 — Existing Forge tests remain green after this phase's migration is applied (up/down/up).
- [ ] AC18 — Production Docker deployment exposes `/mcp` correctly through nginx when enabled, and every MCP-originated **create and delete** mutation appears in `ActivityLog` with `source="mcp"`, **exactly once per mutation** — not two (verifies the activity-log dedup correction in `01_SPEC.md` §4.5 — no MCP tool handler calls `activity.record` directly, only the service layer does, with `source` threaded through). **Note/Document updates are a documented exception**: `notes_service.update_note`/`documents_service.update_document` have never logged to `ActivityLog` for any caller (REST or MCP) — see `01_SPEC.md` §4.5's Milestone 2 correction and Open Question below. `forge_update_note`/`forge_update_document` therefore produce zero `ActivityLog` rows, matching existing behavior exactly; `forge_update_project` does log (the underlying `update_project` already did, for every caller). **Knowledge-graph link create/delete are a second documented exception (found during Milestone 3, by the Agentic Review)**: `knowledge_service.create_link`/`delete_link` have never logged for any caller either; `forge_link_items`/`forge_unlink_items` therefore also produce zero `ActivityLog` rows, matching existing REST behavior — see `01_SPEC.md` §4.5's Milestone 3 correction and the new Open Question below.
- [ ] AC19 — A `forge_session` browser cookie cannot authenticate to `/mcp`, and an MCP bearer token cannot authenticate to `/api/*` — the two auth schemes are provably independent.
- [ ] AC20 — No MCP tool handler contains a direct `session.get(<Model>, ...)` or equivalent raw-ORM call — every tool reaches data exclusively through a `services/*` function (static/import-graph check across `backend/app/mcp/tools/**`, not just a code-review spot-check).

## 6. Open questions requiring a human decision (not resolved by this planning session)

- [ ] Does Milestone 5 need a Settings-page UI wrapping `POST/GET/DELETE /api/mcp/tokens`, or is `curl`/an admin script against that route acceptable for this single-operator instance? (The provisioning *mechanism* itself is decided and built in Milestone 1, per `01_SPEC.md` §4.3.1 — this question is only about a human-facing UI layer on top of it.) (`01_SPEC.md` §4.6)
- [ ] **New, found during Milestone 2 implementation**: should `notes_service.update_note`/`documents_service.update_document` gain `ActivityLog` logging (matching `update_project`'s existing behavior) as a deliberate REST-facing feature improvement in a future phase, or is the current asymmetry (Project updates logged, Note/Document updates not) an acceptable, pre-existing product characteristic Phase 11 should simply preserve rather than "fix" as an unplanned side effect? Not decided by this implementation session — changing it would alter existing UI-facing behavior (every note/document edit would start appearing in Recent Activity) and needs an explicit product decision, not an incidental one made while wiring `source="mcp"` through. (`01_SPEC.md` §4.5)
- [ ] Should `forge_delete_project` be added in a later phase, and if so, does Projects need a "confirm cascade" pattern given it currently *unscopes* rather than deletes children? (Out of scope for Phase 11 as specified.)
- [ ] Is OAuth 2.0 worth building for MCP auth in a future hardening phase, or does the static bearer-token model remain the long-term answer for a self-hosted single-tenant tool? (`01_SPEC.md` §2)
- [ ] Should ADR-0008 (Capability Registry) be promoted from Proposed to Accepted using MCP tools as its second concrete use case, or is the flat tool-registry dict in `app/mcp/tools/__init__.py` sufficient indefinitely? (`01_SPEC.md` §7)
- [ ] Should reads (`forge_search`, `forge_context`, `forge_get_*`) be logged to `ActivityLog` at all, given the existing UI/REST layer has never logged `viewed` actions either — is this consistency worth preserving, or does an AI-driven read deserve visibility the UI's own reads never got? (`01_SPEC.md` §4.5)
- [ ] **New, found during Milestone 3 implementation (Agentic Review)**: should `knowledge_service.create_link`/`delete_link` gain `ActivityLog` logging (matching `create_note`/`delete_note`'s existing behavior) as a deliberate REST-facing feature improvement in a future phase? Unlike a single note's title edit, a knowledge-graph mutation changes the *relationships* between pieces of knowledge — arguably a case where audit visibility has more product value than the update_note/update_document asymmetry this section already tracks, precisely because it's the kind of low-visibility, easy-to-do-repeatedly action `01_SPEC.md` §7's ADR-0004 reconciliation argument ("every MCP write is scoped, token-gated, audited") depends on holding true. Not decided by this implementation session — changing it would alter existing REST-facing behavior (every link create/delete would start appearing in Recent Activity) for every caller, not just MCP ones. (`01_SPEC.md` §4.5)

## 7. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [06_API.md](06_API.md)
- [07_TESTING.md](07_TESTING.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
