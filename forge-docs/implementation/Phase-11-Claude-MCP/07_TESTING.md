# Phase 11 — Testing Strategy

> **Purpose:** Tests required at each level, per the planning brief's testing requirements.
> **Status:** Draft — pending Authorization.
> **Last Updated:** 2026-08-18

---

## 0. Conventions

Follows `07_CODING_STANDARDS.md` §4: new service logic gets unit tests under `backend/tests/`; new routes/tool handlers get at least one integration test through the real handler→service→test-db path. No frontend test framework exists (open repo-wide TODO, not something Phase 11 fixes) — this phase has no committed frontend surface in Milestones 1–4 regardless (see `01_SPEC.md` §4.6 on the deferred token UI).

## 1. Unit tests

- `services/mcp/tokens.py`: issue → hash stored, plaintext never persisted; verify → correct token passes, wrong token fails, revoked token fails, expired-if-applicable fails; revoke → subsequent verify fails; scope parsing (`"read,write"` → `{"read","write"}`).
- `app/mcp/auth.py`: `require_mcp_auth` — missing header, malformed header (`"Bearer"` with no token, wrong scheme), valid token, revoked token. `require_scope` — token with/without the required scope.
- Tool input validation: each tool's JSON-Schema-equivalent validation (e.g. `forge_delete_note` rejects missing/false `confirm`; `forge_search` rejects empty `query`).
- `activity.record(..., source="mcp")` — new column populated correctly; existing call sites default to `"ui"` unchanged (regression-adjacent, see §4).

## 2. Integration tests

- MCP → services → DB, per tool: each of the 18 tools in `06_API.md`, happy path plus its documented error path (not-found, validation, scope-denied).
- `forge_delete_note`/`forge_delete_document` specifically: assert `knowledge_links` rows referencing the deleted item are gone after delete (regression guard for the `purge_links_for` trap — this is the single highest-value integration test in the phase, since it protects against silent orphan-row accumulation).
- `forge_context`: assert it returns `null` project (not an error) when `project_id` omitted, and an explicit not-found error (not empty/silently-ignored results) when `project_id` is invalid.
- `forge_link_items`: assert relinking an already-linked pair (in either direction, A→B or B→A) returns the existing link rather than erroring or duplicating, matching the service's normalization.
- Project-scoping: creating a note/document with a `project_id` and then confirming it appears in that project's counts via `forge_get_project`.
- Migration: see `04_DATABASE.md` §5.

## 3. Security tests

- Missing `Authorization` header on `/mcp` → 401-equivalent, no tool executes.
- Malformed / garbage bearer token → 401-equivalent.
- Valid but revoked token → 401-equivalent, even if it was valid moments before revocation (no caching delay).
- Token with only `forge:read` attempting any write/delete tool → 403-equivalent, and the underlying write/delete does **not** happen (assert DB state unchanged, not just that an error was returned).
- Cross-project leakage: `forge_context`/`forge_search` results are not implicitly scoped by project unless `project_id` is passed — confirm this is documented behavior (Forge has no per-project access control today, only organizational grouping — `01_SPEC.md`'s backend research on `delete_project`'s unscope-not-delete behavior confirms Projects are a label, not a security boundary) rather than assuming isolation that doesn't exist elsewhere in Forge either.
- Confirm **zero** MCP tool or resource can reach `services/secrets/service.py`, `services/crypto/service.py`, `services/settings/service.py`, or `services/settings/backup.py` — a static test (import-graph check, e.g. asserting `backend/app/mcp/` has no import of `services.secrets`, `services.crypto`, or `services.settings`) plus a runtime test attempting to smuggle a secrets read through `forge_search`/`forge_context` and confirming no secret data appears in output.
- Attempt to use a `forge:read`-scoped token against `/api/*` REST routes (should fail — `AuthDep` never accepts an MCP bearer token) and a valid `forge_session` cookie against `/mcp` (should fail — `require_mcp_auth` never accepts a cookie), proving the two auth schemes are genuinely independent, not silently interchangeable.

## 4. Regression

Existing Forge test suite (`backend/tests/`) must remain green, unchanged, after this phase — Phase 11 adds files, it does not modify existing route/service test files except the one additive-column touch to any test that constructs `ActivityLog` rows directly (if any do; most likely none do, since `activity.record()` is the only construction path used in tests today per the researched call-site pattern). Existing REST API behavior (`/api/*`) must be provably unchanged — no route file outside `api/routes/` gets touched by this phase, and no existing route's dependency list changes.

## 5. MCP contract tests

- Tool names match `06_API.md` exactly (prevents drift between docs and implementation).
- Each tool's declared input schema round-trips: valid example inputs pass, one deliberately-invalid example per required field fails with a clear message.
- Resource URIs (`forge://projects`, `forge://projects/{id}`) resolve and return the documented shape.
- Transport-level: a Streamable HTTP client can connect, list tools/resources, and call at least one tool end-to-end (smoke test, not exhaustive — exhaustive coverage is the integration-test layer above).

## 6. Deployment tests

- `docker compose up --build` with `FORGE_MCP_ENABLED=false` (default): `/mcp` is unreachable (confirms the opt-in gate actually gates, not just documents intent).
- Same, with `FORGE_MCP_ENABLED=true` and a bootstrap token set: `/mcp` responds to an authenticated tool call through the nginx proxy exactly as it does hitting the backend container directly — proves the nginx location block (`03_BACKEND.md` §5) is wired correctly, not just theoretically documented.
- Health check: confirm `/health` (already used by the existing `frontend: depends_on: backend: condition: service_healthy` wiring) is unaffected by MCP being enabled or disabled.

## 7. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md)
