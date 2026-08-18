# Phase 11 — Current State

> **Purpose:** Living snapshot of where this phase actually is.
> **Last Updated:** 2026-08-18

---

## 1. Lifecycle stage

**Implementation — Milestone 1 complete, Milestone 2 not authorized.** Per `../../13_PHASE_LIFECYCLE.md`, the phase moved Specification → Authorized → Implementation on 2026-08-18 (see `IMPLEMENT.md`). Milestone 1's mechanical verification contract and independent Agentic Review both reached PASS the same day. Milestone 2 has not been authorized and must not be started — see §4.

## 2. What exists right now

**Planning package** (unchanged since Specification): `README.md`, `01_SPEC.md`, `03_BACKEND.md`, `04_DATABASE.md`, `06_API.md`, `07_TESTING.md`, `08_ACCEPTANCE.md`, `09_IMPLEMENTATION_TASKS.md`.

**Milestone 1 implementation** (new, 2026-08-18):
- Two ADRs, Accepted: [`decisions/0018-mcp-server-integrated-not-separate-process.md`](../../decisions/0018-mcp-server-integrated-not-separate-process.md), [`decisions/0019-mcp-bearer-token-authentication.md`](../../decisions/0019-mcp-bearer-token-authentication.md).
- `backend/app/mcp/` (`auth.py`, `server.py`) — mounts a Streamable HTTP MCP app at `/mcp`, gated by `FORGE_MCP_ENABLED`, zero tools registered.
- `backend/app/services/mcp/tokens.py` — persistent MCP token issue/verify/revoke/list, write-throttled `last_used_at`.
- `backend/app/api/routes/mcp_tokens.py` — `POST/GET/DELETE /api/mcp/tokens`, dual auth (browser session OR bootstrap token).
- `backend/app/models/mcp_token.py`, migration `0010_mcp_tokens.py` — `mcp_tokens` table, `activity_log.source` column.
- `docker/nginx.conf`, `docker-compose.yml`, `.env.example` — `/mcp` proxying (exact + prefix, avoiding a 307-redirect trap found during Docker verification), MCP env vars.
- New FDK verifier: `tools/fdk_verification/verifiers/agentic_review.py`, registered in `CANONICAL_VERIFIERS`, with a `milestone` metadata field added to `VerificationContract`.
- 5 new backend test modules (`test_mcp_tokens_service.py`, `test_mcp_tokens_migration.py`, `test_mcp_tokens_api.py`, `test_mcp_server.py`) plus `tools/tests/verifiers/test_agentic_review.py` — all green, alongside the full pre-existing backend suite and FDK suite.
- `docs/API.md`, `Architecture.md`, `Database.md`, `Deployment.md`, `Security.md` updated with the real, shipped MCP surface (not speculative).
- `VERIFICATION_CONTRACT.md` filled in for the Milestone 1 gate; independent review recorded at [`reviews/AGENTIC_REVIEW_M1.md`](reviews/AGENTIC_REVIEW_M1.md).

**Not committed to git** — everything above is working-tree state; no commit, tag, merge, or push has occurred (per the owner's explicit instruction to stop at the Milestone 1 checkpoint).

## 3. What does NOT exist yet (correctly, per Milestone 1's scope boundary)

- Any MCP tool (`forge_get_note`, `forge_search`, etc.) — zero registered, by design; Milestone 2 scope.
- `source`/`project_id` parameters on `notes_service`/`documents_service`/`projects_service`, or `knowledge_service.list_links_for_items` — Milestone 2/3 scope, correctly untouched.
- `02_UI.md`, `05_COMPONENTS.md` — still deliberately omitted (no frontend surface committed through Milestone 4; see `08_ACCEPTANCE.md` §6).
- A token-management UI — still an open question for Milestone 5.
- `forge-docs/02_ROADMAP.md` update — deliberately deferred to the Released/Frozen stage per `15_VERIFICATION_FRAMEWORK.md` §4.7's own convention, not an oversight.

## 4. Immediate next step

**Milestone 1 checkpoint reached, per the owner's explicit instruction: stop here.** Do not release, merge, tag, freeze, or begin Milestone 2 without a separate, explicit owner authorization act.

Summary of the Milestone 1 gate:
1. All 9 tasks (M1-T1 through M1-T9) complete.
2. Mechanical verification: all 7 applicable FDK verifiers (Specification, Architecture, Build, Test, Regression, Code Quality, Documentation) PASS against the real repository — not asserted, actually executed via `Orchestrator.run()`. Two real bugs were caught and fixed in the process of getting the contract's own commands/scope declarations to parse and run correctly (see §5).
3. Independent Agentic Review: **PASS WITH REQUIRED FIXES** on first pass — found one BLOCKER (the browser-session half of `POST /api/mcp/tokens`'s dual-auth was dead code, see §5) and one MAJOR (this file being stale) that a self-report would not have caught. Both fixed; the review's findings, not a re-run of the review itself, were verified resolved (full detail in `reviews/AGENTIC_REVIEW_M1.md`).

**Next:** owner reviews this state and either requests changes, or explicitly authorizes Milestone 2 (Knowledge CRUD) as a separate act.

## 5. Known findings from Milestone 1 (kept here as institutional memory, not just in the review artifact)

1. **Real regression, caught by mechanical verification, not manual review**: migration `0010`'s original `upgrade()`/`downgrade()` unconditionally inspected `activity_log`, breaking two pre-existing migration tests that use synthetic partial-schema fixtures without that table. Fixed with a table-existence guard — full suite green after.
2. **Security BLOCKER, caught by the independent Agentic Review, not the implementing session**: `_require_session_or_bootstrap` called `require_auth(session)` as a plain coroutine instead of through FastAPI's dependency injection, so `require_auth`'s `Cookie()`-marked parameter was never resolved from the actual request — a valid `forge_session` cookie could never satisfy the check, silently forcing every `/api/mcp/tokens` call through the bootstrap-token path. Practical consequence: an operator who followed `docs/Deployment.md`'s own hardening advice (disable the bootstrap token after first provisioning) would have lost all ability to manage MCP tokens via the browser. Fixed by declaring the cookie parameter on the dependency itself and passing it through explicitly; regression test added (`test_browser_session_alone_can_provision_a_token_with_no_bootstrap_header`).
3. **MINOR, caught by the same review**: bootstrap token comparison used `!=` instead of `hmac.compare_digest`. Fixed for consistency with `verify_session_token`'s existing pattern.
4. **Documented, deliberate deviations, reviewed and accepted**: `require_mcp_auth` implemented as ASGI middleware (not FastAPI `Depends`) because the MCP SDK's app has no FastAPI DI surface; DNS-rebinding protection disabled for `/mcp` since `McpBearerAuthMiddleware` is the real auth boundary and Forge's deployment model doesn't fit a Host-header allowlist. Both independently scrutinized and accepted by the Agentic Review, not merely self-certified.

## 6. Recommended next prompt (for whoever picks this up)

"Review `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md` and `reviews/AGENTIC_REVIEW_M1.md`. If you're satisfied with Milestone 1, authorize Milestone 2 (Knowledge CRUD) explicitly and I'll update `IMPLEMENT.md` and begin `09_IMPLEMENTATION_TASKS.md`'s Milestone 2 task table."

## 7. Cross-references

- [README.md](README.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md)
- [reviews/AGENTIC_REVIEW_M1.md](reviews/AGENTIC_REVIEW_M1.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
