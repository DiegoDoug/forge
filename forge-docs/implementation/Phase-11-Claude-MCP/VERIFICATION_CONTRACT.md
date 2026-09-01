# Phase 11 — Verification Contract

> **Status:** Milestone 5 (and the whole phase's cumulative) gate has reached **PASS** — Agentic RC Review, second/final pass, after a narrow repair cycle addressing the first pass's 1 MAJOR + 3 MINOR findings (1 MAJOR + 1 MINOR fixed and independently re-verified; 2 MINOR correctly left as backlog) — see `reviews/AGENTIC_REVIEW_M5.md`. **Not yet checkpointed or committed. This PASS does NOT authorize release, merge, tag, or freeze** — per `IMPLEMENT.md`'s own rule, the mandatory human review gate (not yet requested of the owner) must be explicitly completed first; no automated process in this repository may perform that step regardless of how many Agentic Review gates passed. Milestones 1–4's gate content is preserved in `../../history/2026-08-18-phase-11-milestone-1-checkpoint.md`, `../../history/2026-08-18-phase-11-milestone-2-checkpoint.md`, `../../history/2026-08-19-phase-11-milestone-3-checkpoint.md`, `../../history/2026-08-19-phase-11-milestone-4-checkpoint.md`, `reviews/AGENTIC_REVIEW_M1.md` through `AGENTIC_REVIEW_M4.md` — this file always reflects the *current* milestone's gate, not phase history.
> **Last Updated:** 2026-08-20

## 1. Phase Metadata

- **Phase name:** Phase 11 — Claude MCP / Second Brain
- **Phase objective:** Expose a scoped, semantic MCP interface over Forge's Notes/Documents/Projects/Knowledge Hub so Claude can use Forge as persistent knowledge substrate, without duplicating Forge's service layer or exposing Secrets/Settings/Crypto.
- **Dependencies:** Phase 06 (Projects), Phase 07 (Knowledge Hub) — both released & frozen, satisfied as-is. Milestones 1–4 — all complete, checkpointed and committed.
- **Completion definition (this milestone):** Token-management UI (owner-resolved), full authorization matrix, audit-logging completeness, Docker production verification, full regression + security suite, release artifacts per `09_IMPLEMENTATION_TASKS.md`'s Milestone 5 table; every mechanical verifier passes; an independent Agentic RC Review records a release recommendation.
- **Milestone:** Milestone 5 — Production Hardening & Release (final milestone of this phase)

## 2. Required Tasks

- [x] M5-T1 — Token-management-UI open question resolved by the owner (Settings-page UI, not a CLI script) and implemented — `frontend/features/mcp-tokens/` (API client + `McpTokensCard`), wired into the existing Settings page. No backend extension needed (`POST/GET/DELETE /api/mcp/tokens` already accepted `AuthDep`). `docs/Security.md` updated.
- [x] M5-T2 — Full authorization matrix test — `backend/tests/test_mcp_authz_matrix.py`: every one of the 18 tools × correctly-scoped / wrongly-scoped / zero-scope token, plus a mutation-safety check (wrongly-scoped write/delete tools stage zero DB changes) and an invalid/revoked-token cross-reference.
- [x] M5-T3 — Audit completeness pass — `backend/tests/test_mcp_audit_completeness.py`: every one of the 12 mutating tools produces exactly the `06_API.md`-documented `ActivityLog` behavior (create/delete tools log once with `source="mcp"`; the three documented exceptions — `forge_update_note`/`forge_update_document`/`forge_link_items`/`forge_unlink_items` — log nothing, matching pre-existing REST behavior); every one of the 6 read tools confirmed to write nothing (verifying, not deciding, `08_ACCEPTANCE.md` §6's still-open "should reads log?" question holds consistently as "no" today).
- [x] M5-T4 — Full regression + security suite run — `cd backend && .venv/Scripts/python.exe -m pytest -q` (469 passed), frontend `tsc --noEmit` + `eslint .` (both clean).
- [x] M5-T5 — Docker/nginx production-path verification — a full, isolated `docker compose -p forge-m5-verify up --build` run (separate project name/volume from any pre-existing local `forge` deployment on this machine, torn down after verification): health check, first-run setup, MCP token provisioning, full `initialize` → `tools/list` (18/18) → `resources/list` (`forge://projects` present) handshake through nginx, frontend served, bare `/mcp` path handled without a redirect trap.
- [x] M5-T6 — Release artifacts — `10_RELEASE_NOTES.md` (drafted, not yet published — publication is part of the release/freeze step this phase cannot self-authorize), `README.md`/`CURRENT_STATE.md` closed out, this document.

## 3. Acceptance Criteria

Full `08_ACCEPTANCE.md` sweep — AC1 through AC20, all previously satisfied by Milestones 1–4, re-verified where this milestone's own work touches them:

- [x] AC1–AC5, AC19 — Authorization matrix (M5-T2) exhaustively re-confirms every tool's scope enforcement, plus invalid/revoked-token rejection, in one place rather than by inference across five files.
- [x] AC16 — Existing Forge REST APIs behave unchanged — full backend suite green (469/469), zero files under `app/api/`, `app/services/notes/`, `documents/`, `projects/`, `knowledge/`, `app/models/` touched this milestone (`git diff --stat`).
- [x] AC17 — Existing tests remain green after all of this phase's migrations (up/down/up already verified in Milestone 1; no new migration this milestone).
- [x] AC18 — Every MCP-originated create/delete mutation logs exactly once with `source="mcp"`; the three documented no-log exceptions hold. `M5-T5`'s Docker verification additionally confirms `/mcp` is correctly reachable through nginx in a production-shaped deployment.
- [x] AC20 — No MCP tool/resource handler contains a raw ORM call — unchanged static check, confirmed still passing for all files across all five milestones.
- [x] AC10 — No MCP tool/resource in any milestone reaches Secrets/Crypto/Settings — re-confirmed by the same recursive static check, unmodified.

AC6–AC15 (CRUD, search/context, memory workflows) are unchanged from Milestones 2–4's own verification; this milestone did not modify any tool handler, so they are not re-verified from scratch here (see the cited milestones' own `VERIFICATION_CONTRACT.md`/checkpoint history for their original proof).

## 4. Expected File Scope

- **Expected new/modified files or directories:** `frontend/features/mcp-tokens/` (new: `api.ts`, `mcp-tokens-card.tsx`), `frontend/app/(app)/settings/page.tsx` (wired in), `backend/tests/test_mcp_authz_matrix.py` (new), `backend/tests/test_mcp_audit_completeness.py` (new), `docs/Security.md`, `docs/API.md`, `.env.example`, `forge-docs/implementation/Phase-11-Claude-MCP/01_SPEC.md` (§4.6 resolved), `08_ACCEPTANCE.md` (§6 token-UI question resolved), `README.md`, `CURRENT_STATE.md`, `IMPLEMENT.md`, `VERIFICATION_CONTRACT.md`, `10_RELEASE_NOTES.md` (new).
- **Explicitly out of scope, confirmed untouched:** every backend `app/mcp/tools/*.py`, `app/mcp/resources.py`, `app/mcp/auth.py`, `app/mcp/server.py`, `app/services/notes/`, `documents/`, `projects/`, `knowledge/`, `app/models/`, `backend/alembic/` (no new migration — no schema change this milestone). `POST/GET/DELETE /api/mcp/tokens` (`app/api/routes/mcp_tokens.py`) also untouched — the token-management UI needed zero backend changes.

## 5. Required Validation Commands

- [x] Test: `cd backend && .venv/Scripts/python.exe -m pytest -q` — 469 passed (up from 395 after Milestone 4; +74 new tests across the two new M5 test files, 0 regressions).
- [x] Test fdk suite: `backend/.venv/Scripts/python.exe -m pytest tools/tests -q` — the Milestone 5 Agentic RC Review independently re-ran this twice and got **113 passed, 0 failed** both times, not the 103/10-failed figure this document previously carried forward from Milestone 4 — the Windows/Git-Bash subprocess-quoting condition that caused those 10 failures is apparently no longer present in this environment (not root-caused further; zero files under `tools/` were touched by Phase 11 in either direction, so this is an environment-state change between sessions, not a Phase-11 fix or regression).
- [x] Frontend: `npx tsc --noEmit` — clean. `npx eslint .` — clean, full repo.
- [x] Build/deploy: isolated `docker compose -p forge-m5-verify --env-file <disposable> up --build` — succeeded; full MCP handshake (18 tools, `forge://projects` resource) verified through nginx; torn down cleanly (`down -v`) afterward, leaving the pre-existing local `forge` project/volume on this machine untouched.

## 6. Architecture Constraints

- [x] The token-management UI required zero backend changes — `POST/GET/DELETE /api/mcp/tokens` already accepted `AuthDep` (browser session cookie) per `01_SPEC.md` §4.3.1, decided and built in Milestone 1. Confirmed by reading the route file before writing any frontend code, not assumed.
- [x] `backend/tests/test_mcp_authz_matrix.py`/`test_mcp_audit_completeness.py` are test-only additions — no `app/mcp/**` file was modified to make them pass; both were designed to prove existing, already-shipped behavior, and both passed on the first run against the unmodified Milestone 1–4 codebase.
- [x] No MCP tool/resource handler was touched this milestone — `git diff --stat` confirms `app/mcp/tools/*.py`, `app/mcp/resources.py`, `app/mcp/auth.py`, `app/mcp/server.py` all empty.
- [x] **Documented, deliberate scope note**: `08_ACCEPTANCE.md` §6 lists several open product questions beyond the token-UI one (should Note/Document updates log; should knowledge-link mutations log; should reads log; is OAuth worth building; should `forge_delete_project` exist). None of these were resolved by this milestone — M5-T3's audit-completeness pass *verifies the current, consistent behavior holds*, it does not *decide* whether that behavior should change. Silently resolving a still-open product question while "just writing a completeness test" would have been exactly the kind of unplanned scope expansion this phase's own execution rules forbid at every prior milestone.

## 7. Documentation Requirements

- [x] `01_SPEC.md` §4.6 — token-UI open question marked resolved, with the owner's actual decision and what was built.
- [x] `08_ACCEPTANCE.md` §6 — same resolution recorded against its own open-questions list; the remaining open questions (audit-logging asymmetries, OAuth, `forge_delete_project`) left explicitly open, not silently closed.
- [x] `docs/Security.md` — MCP section corrected (was stale since Milestone 1, still describing "zero MCP tools" and referencing a Milestone-1-only scope note) and extended to mention token management from the UI and the `forge://projects` scope-enforcement limitation.
- [x] `docs/API.md` — `/api/mcp/tokens` row corrected (same "zero MCP tools" staleness).
- [x] `.env.example` — MCP section comment corrected (same staleness class, third occurrence found this milestone).
- [x] `README.md` — full pass: status line, all Scope/Deliverables/Milestones/Definition-of-Complete checkboxes brought current (this file had never been updated since Specification, unlike `CURRENT_STATE.md`/`IMPLEMENT.md` which were kept current every milestone).
- [x] `CURRENT_STATE.md` — updated to reflect Milestone 5.
- [x] `IMPLEMENT.md` — Milestone 5 section to be added (mission, read order, execution rules, quality gates), following Milestones 1–4's exact structure (this same session, after the RC Review).
- [x] `10_RELEASE_NOTES.md` — drafted.

## 8. Regression Targets

- [x] Full existing backend test suite green — 469/469, including all of Milestones 1–4's own test files, unmodified and still passing.
- [x] Existing REST API behavior provably unchanged — `git diff --stat` shows zero changes under `app/api/`, `app/services/{notes,documents,projects,knowledge}/`, `app/models/`.
- [x] FDK verification framework tests: 113/113 clean per the Agentic RC Review's independent re-run (twice) — see §5's correction; not a Phase-11-caused change either way.
- [x] Frontend regression: full-repo `eslint`/`tsc` clean; the new Settings-page card was manually verified end-to-end (list → create → show-once dialog → copy → revoke) against a live dev instance; no existing Settings-page behavior (theme, master password, backup/import/export) was touched or regressed.

## 9. Required Verification Agents

- [x] Specification
- [x] Architecture
- [x] Build
- [x] Test
- [x] Regression
- [x] Code Quality
- [x] Documentation
- [ ] UX — not formally re-run this milestone; the new Settings-page UI was manually verified live (see §8) rather than through a dedicated UX verifier, consistent with this phase's backend-only verifier posture in Milestones 1–4 (this milestone's one frontend addition is small and reuses 100% pre-existing components/patterns).
- [x] Agentic RC Review — required. **Final verdict: PASS** (first pass: PASS WITH REQUIRED FIXES, 0 BLOCKER/1 MAJOR/3 MINOR; the MAJOR — `test_forge_search_never_returns_secret_data` never actually created a Secret, an unsubstantiated-but-not-live-broken AC10/AC12 claim across five documents — fixed by inserting a real `Secret` row directly via the DB session and asserting it never appears in output; MINOR m1 — a stale FDK test-count claim this document itself carried — corrected; MINORs m2/m3 correctly left as backlog per the reviewer's own explicit non-blocking classification: no MCP-specific structured logging/observability path, and an orphaned pre-existing `handout.md` at repo root unrelated to this phase. Second pass independently re-verified both fixes by re-reading the actual current code, re-deriving *why* the fix closes the specific regression class it targets — not by trusting the fix description — and re-running the full backend suite (469/469) and FDK suite (113/113) fresh). Full record at `reviews/AGENTIC_REVIEW_M5.md`. **This PASS is a code/test-quality gate only — it does not authorize release; the mandatory human review gate below is separate and still required.**

## 10. Known findings from this milestone (for institutional memory — see `reviews/AGENTIC_REVIEW_M5.md` for the full independent whole-phase record)

1. **The regression test for AC10/AC12 (`forge_search` never leaks Secret data) never actually created a `Secret` — found by the whole-phase Agentic RC Review, not any of the four prior milestone reviews or the implementing sessions.** The live property was always correct (`forge_search` never imports `services.secrets`, structurally) — the reviewer independently proved this with a real Secret before flagging the test itself as a false-assurance gap. Fixed by adding a real `Secret` row (inserted directly via the DB session, bypassing the vault-crypto/setup flow entirely — the same pattern `test_knowledge_service.py` already used for a Secret fixture) and asserting it never appears in `forge_search`'s output by content, not just by shape.
2. **`README.md` had never been updated since Specification** (all checkboxes unchecked, status "NOT yet Authorized, NOT started") despite four complete, gated, committed milestones — found and fixed this milestone. This is the third distinct staleness class this phase's later milestones have had to catch and fix (Milestone 4 found `docs/Deployment.md`; this milestone found `docs/Security.md`/`docs/API.md`/`.env.example`/`README.md`) — a process observation worth carrying into future phases: docs describing "current state" drift unless a milestone's own execution rules explicitly name them, not just the files the current milestone's own diff touches.
3. **The frontend token-management UI was manually verified live, not covered by an automated test** — this phase has no frontend test suite (a pre-existing, repo-wide characteristic, not something Phase 11 introduced or is expected to fix).
4. **Two documented, judgment-call security postures carried forward from Milestone 4, independently re-confirmed neither more broken nor silently fixed by the RC Review**: the `forge://projects` static-resource scope-enforcement SDK limitation, and the still-open `08_ACCEPTANCE.md` §6 audit-logging asymmetries (Note/Document updates, knowledge-link mutations, reads).
5. **Docker verification used an isolated project name/volume (`forge-m5-verify`), not the default `forge` project** — this machine already had a `forge_forge-data` volume and stopped containers from what appears to be the operator's own prior deployment testing, discovered during this milestone's work. Nothing under that project/volume was read, modified, or removed.
6. **A second, independent instance of the "docs claim more adversarial testing than the code does" failure class**, this time surfaced by the RC Review itself in real time: after being told the FDK-suite failure count didn't reproduce (m1 in the review), this document was corrected rather than left stating a now-inaccurate number — the same discipline the review's own MAJOR finding required of the shipped test.
7. **No MCP-specific structured logging/observability path** — unhandled exceptions inside `/mcp` tool handlers are caught by the MCP SDK's own generic exception wrapping (a separately-mounted sub-app), not Forge's `register_exception_handlers`/`logger.exception(...)` path every REST-API error goes through. Not exploitable, not a data-integrity issue — an operational-visibility gap only, left as backlog per the reviewer's own classification; would need independent investigation (does the `mcp` package's internal logger propagate to root and get formatted correctly?) before deciding whether it needs code.
8. **An orphaned, pre-existing `handout.md` at repo root** contains stale phase-progress claims now five milestones out of date — predates this session, not a Phase 11 deliverable, not part of any milestone's declared file scope. Left for the owner to delete/update/gitignore at their convenience.

## 11. Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [10_RELEASE_NOTES.md](10_RELEASE_NOTES.md)
- [reviews/AGENTIC_REVIEW_M5.md](reviews/AGENTIC_REVIEW_M5.md)
- [reviews/AGENTIC_REVIEW_M4.md](reviews/AGENTIC_REVIEW_M4.md)
- [reviews/AGENTIC_REVIEW_M3.md](reviews/AGENTIC_REVIEW_M3.md)
- [../../history/2026-08-18-phase-11-milestone-1-checkpoint.md](../../history/2026-08-18-phase-11-milestone-1-checkpoint.md)
- [../../history/2026-08-18-phase-11-milestone-2-checkpoint.md](../../history/2026-08-18-phase-11-milestone-2-checkpoint.md)
- [../../history/2026-08-19-phase-11-milestone-3-checkpoint.md](../../history/2026-08-19-phase-11-milestone-3-checkpoint.md)
- [../../history/2026-08-19-phase-11-milestone-4-checkpoint.md](../../history/2026-08-19-phase-11-milestone-4-checkpoint.md)
