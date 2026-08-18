# Checkpoint — Claude MCP / Second Brain (Phase 11) — 2026-08-18 (Milestone 1)

> **Trigger:** Milestone completion. Milestone 1 (MCP Foundation) of [Phase-11-Claude-MCP](../implementation/Phase-11-Claude-MCP/README.md) reached a passing Agentic Review gate. Per [`../10_CHECKPOINT_PROTOCOL.md`](../10_CHECKPOINT_PROTOCOL.md) §1.
> **Phase:** [Phase-11-Claude-MCP](../implementation/Phase-11-Claude-MCP/README.md)
> **Last Updated:** 2026-08-18

---

```
Phase 11
Milestone 1 — PASS
Mechanical verification: 8/8
Agentic Review: PASS
Security findings: resolved
Documentation findings: resolved
Regression test added: yes
M2: NOT AUTHORIZED
Phase 11: NOT RELEASED
Phase 11: NOT FROZEN
```

This is a **milestone checkpoint, not a release and not a freeze.** No git commit, tag, merge, or push has occurred — everything below is working-tree state. Phase 11 remains in **Implementation**, one milestone of five complete, per [`../13_PHASE_LIFECYCLE.md`](../13_PHASE_LIFECYCLE.md).

## Completed Tasks

All nine Milestone 1 tasks from [`09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-11-Claude-MCP/09_IMPLEMENTATION_TASKS.md):

- **M1-T1** — ADR-0018 (MCP-in-process) and ADR-0019 (bearer-token auth), both Accepted
- **M1-T2** — `McpToken` model, migration `0010_mcp_tokens.py`, `activity_log.source` column
- **M1-T3** — Config additions (`mcp_enabled`, `mcp_bootstrap_enabled`, `mcp_bootstrap_token[_file]`)
- **M1-T4** — `services/mcp/tokens.py` (issue/verify/revoke/list/touch_last_used, write-throttled)
- **M1-T4a** — `POST/GET/DELETE /api/mcp/tokens` provisioning route, `require_bootstrap_auth`
- **M1-T5** — `app/mcp/auth.py` (`require_bootstrap_auth`, `require_scope`, `McpBearerAuthMiddleware`)
- **M1-T6** — MCP server mounted at `/mcp`, gated by `mcp_enabled`, zero tools registered
- **M1-T7** — New "Agentic Review" FDK verifier + contract-format update (`milestone` field, `CANONICAL_VERIFIERS`)
- **M1-T8** — `docker/nginx.conf` `/mcp` routing, `docker-compose.yml`/`.env.example` env additions
- **M1-T9** — `VERIFICATION_CONTRACT.md` filled in for the Milestone 1 gate

Plus the gate itself: the full mechanical verification contract (all 7 applicable verifiers) and the independent Agentic Review, including one repair cycle (see Known Risks).

## Modified Files

**Created**
- `backend/app/mcp/__init__.py`, `auth.py`, `server.py`
- `backend/app/services/mcp/__init__.py`, `tokens.py`
- `backend/app/models/mcp_token.py`
- `backend/app/api/routes/mcp_tokens.py`
- `backend/app/schemas/mcp_tokens.py`
- `backend/alembic/versions/0010_mcp_tokens.py`
- `backend/tests/test_mcp_tokens_service.py`, `test_mcp_tokens_migration.py`, `test_mcp_tokens_api.py`, `test_mcp_server.py`
- `tools/fdk_verification/verifiers/agentic_review.py`
- `tools/tests/verifiers/test_agentic_review.py`
- `forge-docs/decisions/0018-mcp-server-integrated-not-separate-process.md`, `0019-mcp-bearer-token-authentication.md`
- `forge-docs/implementation/Phase-11-Claude-MCP/` (full planning package plus `IMPLEMENT.md`, `reviews/AGENTIC_REVIEW_M1.md`, updated `CURRENT_STATE.md`/`VERIFICATION_CONTRACT.md`)
- `forge-docs/history/2026-08-18-phase-11-milestone-1-checkpoint.md` (this file)

**Modified**
- `backend/app/models/__init__.py`, `activity.py` (registration, `source` column)
- `backend/app/core/config.py`, `errors.py`, `security.py` (MCP settings, `ForbiddenError`, token hashing)
- `backend/app/api/router.py`, `main.py` (route registration, `/mcp` mount + lifespan chaining)
- `backend/requirements.txt` (`mcp` SDK dependency)
- `docker/nginx.conf`, `docker-compose.yml`, `.env.example`
- `tools/fdk_verification/contract.py`, `verifiers/__init__.py`
- `docs/API.md`, `Architecture.md`, `Database.md`, `Deployment.md`, `Security.md`
- `forge-docs/06_TECH_STACK.md`, `15_VERIFICATION_FRAMEWORK.md`, `decisions/README.md`, `implementation/VERIFICATION_CONTRACT_TEMPLATE.md`

**Untouched, confirmed by the Architecture Verifier and the Agentic Review independently**: `backend/app/services/secrets/`, `crypto/`, `settings/`; `backend/app/api/deps.py` (`AuthDep`/`require_auth`); `backend/app/services/notes/`, `documents/`, `projects/`, `knowledge/`; `frontend/`.

## Current State

The narrow vertical slice this milestone exists to prove now works end-to-end, verified against the real repository (not asserted) and against a real `docker compose up --build` stack:

```
Claude
  ↓
Streamable HTTP
  ↓
nginx
  ↓
FastAPI /mcp
  ↓
MCP authentication
  ↓
scope enforcement
  ↓
MCP server
```

A persistent, individually-revocable bearer token — provisioned via a one-time bootstrap credential that can never itself authenticate to `/mcp` — connects, completes the MCP handshake, and lists zero tools. Missing/malformed/bootstrap/revoked credentials are all rejected before any protocol processing. The browser session and the MCP token are provably independent in both directions. Zero MCP tools exist; zero Notes/Documents/Projects/Knowledge service code was touched.

**Gate result:** mechanical verification 8/8 (Specification, Architecture, Build, Test, Regression, Code Quality, Documentation, Agentic Review — UX correctly declared not-required). Agentic Review: PASS, after one repair cycle — see Known Risks.

## Remaining Work

Milestones 2–5 of [`09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-11-Claude-MCP/09_IMPLEMENTATION_TASKS.md), **none authorized**:

- **Milestone 2 — Knowledge CRUD.** Notes/Documents/Projects tools. This is where the system begins touching actual persistent knowledge and introducing write/delete authority — a materially different risk profile from Milestone 1's transport/auth foundation, and should be scoped and reviewed with that in mind rather than rushed on the strength of Milestone 1's pass.
- Milestones 3–5 (Search/Context, Memory Workflows, Production Hardening) unchanged, all downstream of Milestone 2.

## Recommended Next Prompt

> Milestone 1 is checkpointed and not yet followed by a Milestone 2 authorization. When ready, review `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md` and `reviews/AGENTIC_REVIEW_M1.md`, then authorize Milestone 2 explicitly as its own act — not implied by this checkpoint. On authorization, update `IMPLEMENT.md`'s Status line to record it as a separate, dated gate (matching how Milestone 1's authorization is recorded there), then begin `09_IMPLEMENTATION_TASKS.md`'s Milestone 2 task table (M2-T0 through M2-T6).

## Known Risks

1. **The Agentic Review's first pass was not a clean PASS** — it found a genuine BLOCKER (the browser-session half of `POST /api/mcp/tokens`'s dual-auth was silently dead code, because `require_auth` was called as a plain coroutine instead of through FastAPI's dependency injection, so its `Cookie()`-marked parameter never resolved from the actual request) and a MAJOR (`CURRENT_STATE.md` staleness). Both are fixed, a regression test was added for the security bug, and the same reviewer independently re-verified both fixes before updating its verdict to PASS. Recorded in full in `reviews/AGENTIC_REVIEW_M1.md` — carried forward here rather than treated as resolved-and-forgotten, since it's the kind of bug class (auth logic that looks correct but silently no-ops) worth remembering when Milestone 2 adds real write authority on top of this foundation.
2. **Two deliberate, documented deviations from the original spec sketch**, both reviewed and accepted rather than merely self-certified: `require_mcp_auth` is ASGI middleware, not a FastAPI `Depends` (the MCP SDK's app has no FastAPI DI surface); DNS-rebinding protection is disabled for `/mcp` (Forge's deployment model doesn't fit a Host-header allowlist, and the bearer-token middleware is the real auth boundary). Both should be re-examined if Forge's deployment model or the MCP SDK's auth primitives change.
3. **Docker/deployment verification was manual, not mechanically re-run by the contract** — a full `docker compose up --build` cycle with real port binding isn't practical to auto-run on every verification pass. It was genuinely exercised (not just reasoned about) during this milestone, including catching and fixing a 307-redirect trap in the original nginx config, but a future milestone's contract should decide whether to invest in making this mechanically re-runnable.
4. **No frontend surface exists for MCP token management** — `POST/GET/DELETE /api/mcp/tokens` is REST-only, no UI. Still an open question for Milestone 5, unchanged from the planning package.

## Blocking decisions requiring approval

**None currently.** The one decision this checkpoint surfaces for the owner is not a blocker but a request already honored: **do not rush Milestone 2.** Milestone 2 introduces write/delete authority over real persistent knowledge for the first time — a different risk class from Milestone 1's connect-and-authenticate slice — and should get its own deliberate authorization, scoping discussion, and (per the owner's stated intent) unhurried review, not a reflexive "M1 passed, proceed."

## Cross-references

- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md](../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md)
- [../implementation/Phase-11-Claude-MCP/IMPLEMENT.md](../implementation/Phase-11-Claude-MCP/IMPLEMENT.md)
- [../implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md](../implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md)
- [../implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M1.md](../implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M1.md)
- [../decisions/0018-mcp-server-integrated-not-separate-process.md](../decisions/0018-mcp-server-integrated-not-separate-process.md)
- [../decisions/0019-mcp-bearer-token-authentication.md](../decisions/0019-mcp-bearer-token-authentication.md)
