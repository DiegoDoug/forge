# Phase 11 — Verification Contract

> **Status:** Active — Milestone 1 implementation complete, contract filled in for the Milestone 1 gate per `09_IMPLEMENTATION_TASKS.md` M1-T9. This single contract file is updated in place for each milestone (M2-T6, M3-T5, M4-T5, M5 gate) rather than one file per milestone — see §1's **Milestone** key and `tools/fdk_verification/verifiers/agentic_review.py`'s milestone-numbered artifact resolution.
> **Last Updated:** 2026-08-18

## 1. Phase Metadata

- **Phase name:** Phase 11 — Claude MCP / Second Brain
- **Phase objective:** Expose a scoped, semantic MCP interface over Forge's Notes/Documents/Projects/Knowledge Hub so Claude can use Forge as persistent knowledge substrate, without duplicating Forge's service layer or exposing Secrets/Settings/Crypto.
- **Dependencies:** Phase 06 (Projects), Phase 07 (Knowledge Hub) — both released & frozen, satisfied as-is.
- **Completion definition (this milestone):** Milestone 1's narrow vertical slice (transport, auth, scope enforcement, handshake, zero tools) proven end-to-end; every mechanical verifier below passes; an independent Agentic Review records a PASS verdict.
- **Milestone:** Milestone 1 — MCP Foundation

## 2. Required Tasks

- [x] M1-T1 — ADR-0018 (MCP-in-process), ADR-0019 (bearer-token auth) — `forge-docs/decisions/0018-*.md`, `0019-*.md`
- [x] M1-T2 — `McpToken` model, migration `0010_mcp_tokens.py`, `activity_log.source` column
- [x] M1-T3 — Config additions (`mcp_enabled`, `mcp_bootstrap_enabled`, `mcp_bootstrap_token[_file]`)
- [x] M1-T4 — `services/mcp/tokens.py` (issue/verify/revoke/list/touch_last_used, throttled)
- [x] M1-T4a — `POST/GET/DELETE /api/mcp/tokens` provisioning route, `require_bootstrap_auth`
- [x] M1-T5 — `app/mcp/auth.py` (`require_bootstrap_auth`, `require_scope`, `McpBearerAuthMiddleware`)
- [x] M1-T6 — MCP server bootstrap, mounted at `/mcp` gated by `mcp_enabled`, zero tools registered
- [x] M1-T7 — New `Agentic Review` FDK verifier + contract-format update (`milestone` field, `CANONICAL_VERIFIERS`)
- [x] M1-T8 — `docker/nginx.conf` `/mcp` location blocks, `docker-compose.yml`/`.env.example` env additions
- [x] M1-T9 — This document, filled in

## 3. Acceptance Criteria

From `08_ACCEPTANCE.md` §1 (Connectivity & auth) — the only section in scope for this milestone (§2–§5 require CRUD tools that don't exist until Milestone 2+):

- [x] AC1 — Persistent MCP token connects via Streamable HTTP (`test_mcp_server.py::test_valid_persistent_token_completes_the_handshake_with_zero_tools`; also verified against a real `docker compose up --build` stack, see §5)
- [x] AC1a — Bootstrap token rejected by `/mcp` (`test_mcp_server.py::test_bootstrap_token_is_never_accepted_by_mcp_itself`, plus a live Docker verification)
- [x] AC1b — Raw token returned exactly once, never again on list (`test_mcp_tokens_api.py::test_created_token_is_never_returned_again_on_list`)
- [x] AC1c — `mcp_bootstrap_enabled=false` is a true kill switch (`test_mcp_tokens_api.py::test_disabling_bootstrap_closes_provisioning_even_with_a_correct_token`)
- [x] AC2 — `/mcp` unreachable when `FORGE_MCP_ENABLED=false` (`test_mcp_server.py::test_mcp_disabled_by_default_leaves_mcp_unmounted`; live Docker verification: 404 through nginx)
- [x] AC3 — Missing/malformed `Authorization` rejected before any protocol processing (`test_mcp_server.py::test_missing_authorization_header_is_rejected_before_any_protocol_processing`, `test_malformed_authorization_header_is_rejected`)
- [x] AC4 — Revoked token loses access immediately (`test_mcp_server.py::test_revoked_token_is_rejected_immediately`)
- [x] AC4a — `last_used_at` write-throttled to a 5-minute window (`test_mcp_tokens_service.py::test_touch_last_used_is_throttled_within_the_five_minute_window`, `test_touch_last_used_updates_again_once_the_throttle_window_has_passed`)

**AC5 (scope enforcement on write/delete tools) is deliberately not listed above** — it is not yet checkable, not merely deferred: zero MCP tools are registered in Milestone 1, so there is no tool call site to exercise it against. `require_scope` exists and is unit-testable in isolation, but AC5 itself names a behavior only observable once Milestone 2 registers tools. It is listed and verified at the Milestone 2 gate instead of being included here unchecked, per the Specification Verifier's all-checked-or-absent convention (an unchecked §3 item is a FAIL, not an N/A — the item does not belong in this milestone's checklist at all).

From §5 (Regression, audit, deployment):
- [x] AC16 — Existing REST APIs unchanged — full backend regression suite green (see §5)
- [x] AC17 — Existing tests remain green after the migration is applied — `test_mcp_tokens_migration.py`, plus the two pre-existing migration tests (`test_projects_migration.py`, `test_knowledge_migration.py`) that migration `0010` initially broke and was corrected to handle (see Known Findings below)
- [x] AC18 (partial) — Docker deployment exposes `/mcp` correctly through nginx when enabled (live-verified); the `source="mcp"` audit-logging half is not yet exercisable (no write tools until Milestone 2)
- [x] AC19 — The two auth schemes are provably independent in both directions (`test_mcp_server.py::test_mcp_token_cannot_authenticate_against_the_rest_api`, `test_browser_session_cookie_cannot_authenticate_against_mcp`)

AC6–AC15 (Knowledge CRUD, search/context, memory workflows) are Milestone 2–4 scope and intentionally unchecked here.

## 4. Expected File Scope

- **Expected new/modified files or directories:** `backend/app/mcp/`, `backend/app/services/mcp/`, `backend/app/models/mcp_token.py`, `backend/app/api/routes/mcp_tokens.py`, `backend/app/schemas/mcp_tokens.py`, `backend/alembic/versions/0010_mcp_tokens.py`, `backend/tests/test_mcp_`, `docker/nginx.conf`, `docker-compose.yml`, `.env.example`, `tools/fdk_verification/verifiers/agentic_review.py`, `tools/tests/verifiers/test_agentic_review.py`, `docs/`, `forge-docs/`
- **Explicitly out of scope:** `backend/app/services/secrets/`, `backend/app/services/crypto/`, `backend/app/services/settings/`, `backend/app/api/deps.py`, `backend/app/services/notes/`, `backend/app/services/documents/`, `backend/app/services/projects/`, `backend/app/services/knowledge/`, `frontend/`

Detail (the two lines above are the machine-checked prefixes the Architecture Verifier compares every changed file against — `_commands.py`/`_paths.py` extract backticked, comma-separated tokens from a single line, so the summary above must stay on one line each; this breakdown is the human-readable version of the same scope):

**New/modified files this milestone (verified against actual `git status`):**
- `backend/app/mcp/__init__.py`, `auth.py`, `server.py` (new package)
- `backend/app/services/mcp/__init__.py`, `tokens.py` (new package)
- `backend/app/models/mcp_token.py` (new)
- `backend/app/models/__init__.py`, `activity.py` (modified — registration, `source` column)
- `backend/app/core/config.py` (modified — MCP settings)
- `backend/app/core/errors.py` (modified — `ForbiddenError` added)
- `backend/app/core/security.py` (modified — `generate_mcp_token`/`hash_mcp_token`)
- `backend/app/api/routes/mcp_tokens.py` (new)
- `backend/app/api/router.py` (modified — route registration)
- `backend/app/main.py` (modified — mount `/mcp`, lifespan chaining)
- `backend/app/schemas/mcp_tokens.py` (new)
- `backend/alembic/versions/0010_mcp_tokens.py` (new)
- `backend/requirements.txt` (modified — `mcp` dependency added)
- `backend/tests/test_mcp_tokens_service.py`, `test_mcp_tokens_migration.py`, `test_mcp_tokens_api.py`, `test_mcp_server.py` (new)
- `docker/nginx.conf`, `docker-compose.yml`, `.env.example` (modified)
- `tools/fdk_verification/verifiers/agentic_review.py` (new), `verifiers/__init__.py`, `contract.py` (modified)
- `tools/tests/verifiers/test_agentic_review.py` (new)
- `docs/API.md`, `docs/Architecture.md`, `docs/Database.md`, `docs/Deployment.md`, `docs/Security.md` (modified)
- `forge-docs/06_TECH_STACK.md`, `15_VERIFICATION_FRAMEWORK.md`, `decisions/README.md`, `implementation/VERIFICATION_CONTRACT_TEMPLATE.md` (modified)
- `forge-docs/decisions/0018-*.md`, `0019-*.md` (new)
- `forge-docs/implementation/Phase-11-Claude-MCP/**` (this folder, including `IMPLEMENT.md`, `CURRENT_STATE.md` updates and `reviews/AGENTIC_REVIEW_M1.md`)

**Out-of-scope detail (must NOT be touched) — confirmed clean via `git status`:**
- `backend/app/services/secrets/`, `backend/app/services/crypto/`, `backend/app/services/settings/` — untouched
- `backend/app/api/routes/` other than the new `mcp_tokens.py` — untouched (not machine-checkable as a clean prefix, since `mcp_tokens.py` legitimately lives in that same directory — verified by inspection instead)
- `backend/app/api/deps.py` (`AuthDep`/`require_auth`) — untouched
- `frontend/` — untouched
- Any other phase's folder under `forge-docs/implementation/` — untouched
- `backend/app/services/notes/`, `documents/`, `projects/`, `knowledge/` service logic — untouched (Milestone 2+ scope; `source`/`project_id`/batch-link params are not yet added, correctly, since Milestone 2 hasn't started)

## 5. Required Validation Commands

Machine-executed by the Build/Test verifiers (contract-driven — see `tools/fdk_verification/verifiers/_commands.py`), all commands relative to the repo root. Exactly one colon per item (label, then command) and no markdown backticks around the command — `_commands.py`'s parser takes the item text verbatim as the shell command, so backticks would be passed to the shell literally (command substitution), not treated as Markdown formatting:

- [x] Test: cd backend && .venv/Scripts/python.exe -m pytest -q
- [x] Test fdk suite: backend/.venv/Scripts/python.exe -m pytest tools/tests -q
- [x] Build: docker build -t forge-mcp-m1-buildcheck ./backend

**Manually performed, not mechanically re-run by this contract** (require a live Docker daemon + port binding, exceed what's practical to auto-run on every verification pass, and were already exercised directly during implementation — see `09_IMPLEMENTATION_TASKS.md`'s M1 gate and §10 below for what was actually observed):
- Full stack up via `docker compose up --build -d` with `FORGE_MCP_ENABLED=true`: bootstrap-at-`/mcp` rejected (401), no-auth rejected (401), provisioning via nginx succeeds (201), bare `/mcp` (no trailing slash) handshake succeeds through nginx (200, no client-visible redirect) — this is what caught and fixed the 307-redirect trap in the original nginx config.
- Same, `FORGE_MCP_ENABLED=false`: `/mcp` returns 404 through nginx, `/health` unaffected (200).

## 6. Architecture Constraints

- [x] `backend/app/mcp/` and `backend/app/services/mcp/` import only `services/activity` indirectly (via `app/mcp/auth.py` → `services/mcp/tokens.py`, which imports only `app/core/security` and `app/models/mcp_token`) — no import of `services/secrets`, `services/crypto`, or `services/settings` anywhere in the new code (confirmed by direct inspection; Milestone 2's AC20 adds an automated static check once tool handlers exist to check).
- [x] No new database beyond the existing SQLite file; no new inter-process boundary — confirmed by ADR-0018 and the actual code (`app.mount()` inside the existing FastAPI app, same `AsyncSession` factory).
- [x] `AuthDep`/`require_auth`/`api/deps.py` unmodified — confirmed via `git diff backend/app/api/deps.py` (empty).
- [x] Routers stay thin; MCP tool handlers stay thin — logic lives in `services/` — trivially satisfied this milestone (zero tool handlers exist yet); `api/routes/mcp_tokens.py` delegates entirely to `services/mcp/tokens.py`.
- [x] **Deviation from `03_BACKEND.md`'s original sketch, documented not silent**: `require_mcp_auth` was specified as a FastAPI `Depends`-shaped function; the actual MCP SDK app has no FastAPI DI surface, so it is implemented as `McpBearerAuthMiddleware` (ASGI middleware) instead. Enforcement guarantee preserved; see ADR-0019 §4 and `app/mcp/auth.py`'s module docstring. Pre-approved in `IMPLEMENT.md`'s Autonomy Rules.
- [x] **New, documented deviation found during implementation**: the MCP SDK's DNS-rebinding protection (`TransportSecuritySettings`) is disabled for `/mcp`, since Forge's deployment model (arbitrary LAN IP/Tailscale hostname/reverse-proxied domain) doesn't fit a Host-header allowlist, and `McpBearerAuthMiddleware` — not the SDK's Host-header heuristic — is the real authorization boundary here. Documented in `app/mcp/server.py`'s inline comment and flagged explicitly for Agentic Review scrutiny (see `reviews/AGENTIC_REVIEW_M1.md`).

## 7. Documentation Requirements

- [x] `docs/API.md` — `/api/mcp/tokens` row added, pointer to `06_API.md` for the MCP tool contract
- [x] `docs/Architecture.md` — request-flow diagram + Auth model section updated per ADR-0018/0019
- [x] `docs/Database.md` — `mcp_tokens` table entry, `activity_log.source` column noted
- [x] `docs/Deployment.md` — "MCP server for Claude / Claude Code" section, matching the Vision-Ingest section's style
- [x] `docs/Security.md` — "MCP access" section
- [x] `forge-docs/06_TECH_STACK.md` — `mcp` dependency recorded
- [x] `forge-docs/15_VERIFICATION_FRAMEWORK.md` — §4.9 Agentic Review Verifier documented
- [x] `forge-docs/decisions/README.md` — ADR-0018/0019 indexed
- [x] `forge-docs/implementation/VERIFICATION_CONTRACT_TEMPLATE.md` — Milestone metadata key, Agentic Review line added
- [x] `CURRENT_STATE.md` — updated to reflect Milestone 1 completion
- [ ] `forge-docs/02_ROADMAP.md` — **not required at this milestone** (Release-stage obligation per `15_VERIFICATION_FRAMEWORK.md` §4.7, not RC/milestone-stage — left unchecked deliberately, matching the framework's own documented convention).

## 8. Regression Targets

- [x] Full existing backend test suite green, unchanged in behavior (two pre-existing migration tests initially broke due to migration `0010`'s unconditional `activity_log` inspection — fixed with an existence guard; both green now, see Known Findings)
- [x] Existing REST API behavior provably unchanged — no route file outside the new `mcp_tokens.py` touched; `AuthDep`/`api/deps.py` untouched
- [x] Existing FDK verification framework tests (`tools/tests/`) remain green after the new verifier is added — 113/113

## 9. Required Verification Agents

- [x] Specification
- [x] Architecture
- [x] Build
- [x] Test
- [x] Regression
- [x] Code Quality
- [x] Documentation
- [ ] UX — not required (backend-only milestone; `verifiers/ux.py` always returns N/A regardless)
- [x] Agentic Review — required. Verdict recorded at `reviews/AGENTIC_REVIEW_M1.md`.

## 10. Known findings from this milestone (for the Agentic Review's attention)

1. **Real regression caught and fixed**: migration `0010`'s original `upgrade()`/`downgrade()` unconditionally inspected `activity_log`, breaking two pre-existing migration tests (`test_projects_migration.py`, `test_knowledge_migration.py`) that use synthetic partial-schema fixtures without that table. Fixed with a table-existence guard. Full suite is green now, but this is exactly the class of thing an independent reviewer should double-check wasn't papered over incorrectly.
2. **Documented, deliberate deviation**: DNS-rebinding protection disabled for `/mcp` (§6 above) — a security-relevant choice that deserves independent scrutiny, not just self-certification.
3. **Documented, deliberate deviation**: `require_mcp_auth` implemented as ASGI middleware rather than a FastAPI `Depends`, because the MCP SDK's app has no FastAPI DI surface (§6 above, ADR-0019 §4).
4. **nginx trailing-slash fix**: the backend's `Mount("/mcp", ...)` 307-redirects a bare `/mcp` to `/mcp/`; an MCP HTTP client is not guaranteed to follow a 307 on POST, so `docker/nginx.conf` normalizes this with an exact + prefix location pair rather than relying on redirect-following. Verified against a real `docker compose up --build` stack, not just reasoned about.

## 11. Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [reviews/AGENTIC_REVIEW_M1.md](reviews/AGENTIC_REVIEW_M1.md)
- [../VERIFICATION_CONTRACT_TEMPLATE.md](../VERIFICATION_CONTRACT_TEMPLATE.md)
- [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md)
