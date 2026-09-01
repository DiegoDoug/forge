# Checkpoint — Claude MCP / Second Brain (Phase 11) — 2026-08-20 (Milestone 5, Final)

> **Trigger:** Milestone completion — the final milestone of the phase, plus the mandatory human review gate. Per [`../10_CHECKPOINT_PROTOCOL.md`](../10_CHECKPOINT_PROTOCOL.md) §1.
> **Phase:** [Phase-11-Claude-MCP](../implementation/Phase-11-Claude-MCP/README.md)
> **Last Updated:** 2026-08-20

---

```
Phase 11
Milestone 5 — PASS (whole-phase Agentic RC Review)
Mechanical verification: backend 469/469, frontend tsc/eslint clean, Docker production path verified live
Agentic RC Review: PASS (after one repair cycle)
Findings: 0 BLOCKER, 1 MAJOR, 3 MINOR — MAJOR + 1 MINOR fixed and independently re-verified; 2 MINOR left as backlog
Mandatory human review gate: COMPLETE — owner approved 2026-08-20, item by item
Phase 11: RELEASE AUTHORIZED
```

This checkpoint covers Milestone 5's work and the phase's closing gate. Milestones 1–4 are already committed (`6854971`, `4cf1bd2`, the Milestone 3 commit, `936c13c`); this is the fifth and final milestone. All five milestones are now complete, each independently gated PASS, and the owner has completed the mandatory human review gate — see `../implementation/Phase-11-Claude-MCP/IMPLEMENT.md`'s "mandatory human review gate" section for the full record. Per `../13_PHASE_LIFECYCLE.md`, this checkpoint records **Milestone 5 complete and the phase release-authorized**; the actual release commit, tag, and freeze are separate acts recorded in git history and `10_RELEASE_NOTES.md`, not in this file.

## Completed Tasks

All six Milestone 5 tasks from [`09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-11-Claude-MCP/09_IMPLEMENTATION_TASKS.md):

- **M5-T1** — Token-management-UI open question resolved by the owner (Settings-page UI, not a CLI script) and implemented: `frontend/features/mcp-tokens/` (API client + `McpTokensCard`), wired into the existing Settings page. No backend change needed.
- **M5-T2** — Full authorization matrix — `backend/tests/test_mcp_authz_matrix.py`: all 18 tools × correctly-scoped/wrongly-scoped/zero-scope token, plus a DB-level mutation-safety check and an invalid/revoked-token cross-reference.
- **M5-T3** — Audit completeness pass — `backend/tests/test_mcp_audit_completeness.py`: every one of the 12 mutating tools produces exactly its documented `ActivityLog` behavior; all 6 read tools confirmed to write nothing.
- **M5-T4** — Full regression + security suite — backend 469/469, frontend `tsc`/`eslint` clean.
- **M5-T5** — Docker/nginx production-path verification — a full, isolated `docker compose -p forge-m5-verify up --build` run (health, setup, token provisioning, full MCP handshake through nginx — 18/18 tools, `forge://projects` resource — torn down cleanly, never touching the pre-existing local `forge` project/volume on this machine).
- **M5-T6** — Release artifacts — `10_RELEASE_NOTES.md` drafted, `README.md`/`CURRENT_STATE.md`/`08_ACCEPTANCE.md` closed out, `VERIFICATION_CONTRACT.md` updated.

Plus the gate itself: the whole-phase Agentic RC Review (not just Milestone 5's diff — all five milestones' cumulative work), including **one narrow repair cycle addressing 1 MAJOR + 1 MINOR finding, independently re-verified by the same reviewer** — see Known Risks. And the mandatory human review gate, completed by the owner in chat.

## Modified Files

**Created**
- `frontend/features/mcp-tokens/api.ts`, `mcp-tokens-card.tsx`
- `backend/tests/test_mcp_authz_matrix.py`, `test_mcp_audit_completeness.py`
- `forge-docs/implementation/Phase-11-Claude-MCP/10_RELEASE_NOTES.md`
- `forge-docs/implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M5.md`
- `forge-docs/09_CLAUDE_CODE_RULES.md` §3.1 (new repo-wide safeguard — see Known Risks item 4)
- `forge-docs/history/2026-08-20-phase-11-milestone-5-checkpoint.md` (this file)

**Modified**
- `frontend/app/(app)/settings/page.tsx` (token UI wired in)
- `backend/tests/test_mcp_tools_search_context.py` (`test_forge_search_never_returns_secret_data` repair-cycle fix — see Known Risks item 1)
- `docs/Security.md`, `docs/API.md`, `.env.example` (staleness corrections — "as of Milestone 1, zero MCP tools" class, found and fixed)
- `forge-docs/implementation/Phase-11-Claude-MCP/01_SPEC.md` (§4.6 token-UI question resolved), `08_ACCEPTANCE.md` (§6 resolution recorded; all 20 ACs individually checked with citations at the human review gate's request), `README.md` (full pass — had never been updated since Specification), `CURRENT_STATE.md`, `IMPLEMENT.md` (Milestone 5 section + human review gate record), `VERIFICATION_CONTRACT.md`

**Untouched, confirmed by `git diff --stat` and the Agentic RC Review independently**: every `app/mcp/tools/*.py`, `app/mcp/resources.py`, `app/mcp/auth.py`, `app/mcp/server.py`; `app/services/{notes,documents,projects,knowledge}/`; `app/models/`; `backend/alembic/` (no new migration); `docker/nginx.conf`, `docker-compose.yml`, `backend/Dockerfile`.

## Current State

All five Phase 11 milestones are complete, independently gated PASS, and the mandatory human review gate is complete — the owner approved the phase in full, in chat, 2026-08-20:

- Architecture, authentication model, scopes, tool surface, data exposure, destructive-operation policy (`confirm: true` for v1), Claude workflow, and deployment model all approved.
- `forge:secrets` stays explicitly unimplemented (owner decision, not a gap).
- The static `forge://projects` resource's scope-enforcement limitation was reviewed verbatim (quoted in `IMPLEMENT.md`) and accepted as an intentional, documented narrow exception — recorded as technical debt, not silently absorbed into release history.
- AC14 (cross-session memory continuity) confirmed genuinely live-verified at three independently-increasing levels of rigor.
- A procedural safeguard (`09_CLAUDE_CODE_RULES.md` §3.1) was added against this session's own near-miss deletion of local dev state during Docker verification prep — promoted to a permanent, repo-wide rule per the owner's explicit requirement, not scoped to Phase 11.

**Gate result:** Milestone 5's own mechanical verification and Agentic RC Review both PASS; the whole-phase human review gate is complete. **Release authorized by the owner.**

## Remaining Work

None for this phase's implementation. Post-checkpoint: the release commit, annotated tag, push, and post-release freeze commit — all separate, explicit acts per the owner's own release-closure instruction, not part of this checkpoint.

## Recommended Next Prompt

> Phase 11 is complete, gated, and release-authorized. Proceed with the release closure sequence the owner specified: release commit → integrity check → annotated tag on the release commit → push/PR as appropriate → separate freeze commit → roadmap/CURRENT_STATE reconciliation → verify the tag still resolves to the release commit → push the freeze commit.

## Known Risks

1. **The whole-phase Agentic RC Review's first pass was not a clean PASS, and the finding was real.** One MAJOR: `test_forge_search_never_returns_secret_data` (a Milestone-3-era test) had never actually created a `Secret`, despite its own docstring and four other documents describing it as adversarial — a gap that survived Milestone 3's own Agentic Review and Milestone 5's own "full regression + security suite" pass, caught only by the final whole-phase audit reading the test body itself. The live product was never actually vulnerable — the reviewer independently proved this with a real Secret before flagging the test — but the regression test's own safety net was weaker than five documents claimed. Fixed by inserting a real `Secret` row directly via the DB session and asserting it never appears in `forge_search`'s output by content; the same reviewer independently re-verified the fix by re-deriving *why* it closes the specific regression class, not by trusting the fix description.
2. **One MINOR finding, fixed**: the FDK tools/tests suite's documented "103 passed, 10 failed" figure (carried since Milestone 4) no longer reproduced — the reviewer got 113/113 clean across three separate runs. Corrected in `VERIFICATION_CONTRACT.md`/`CURRENT_STATE.md`; the underlying environment-state change was not further root-caused (FDK tooling, not Forge product code).
3. **Two MINOR findings, deliberately left as backlog**, per the reviewer's own explicit non-blocking classification: no MCP-specific structured logging/observability path (unhandled tool-handler exceptions bypass Forge's own `register_exception_handlers` path since `/mcp` is a separately-mounted sub-app); an orphaned, pre-existing `handout.md` at repo root, unrelated to Phase 11, now five milestones out of date.
4. **This session nearly deleted a local dev database (`backend/.dev-data/`) while preparing Milestone 5's Docker verification** — caught before real damage (the file was locked by a still-running process; contents turned out to be a single empty note from Phase 01), but the reasoning that led to attempting the deletion was unsound: inferring a directory was disposable from its gitignored status and naming convention, rather than confirming it. **The owner required this be converted into a permanent process safeguard, not just a one-time close call** — added `forge-docs/09_CLAUDE_CODE_RULES.md` §3/§3.1, a new repo-wide rule (not scoped to Phase 11): never delete/reset local DB state or a Docker volume not created by the same session/task; inspect before touching anything ambiguous; default to an isolated new volume/project instead of clearing an existing one. This same default was, in fact, what correctly protected a separate pre-existing `forge`-named Docker Compose project/volume later in this same session's Docker verification work.
5. **The `forge://projects` static-resource scope-enforcement limitation is intentional, documented technical debt, not a defect** — a genuine MCP SDK constraint (no per-request auth context for a static resource in this SDK version), independently confirmed at Milestones 4 and 5 by reading the installed SDK's source directly. The owner reviewed the verbatim limitation text and explicitly accepted it as a narrow exception; it remains visible in `06_API.md` §5's footnote, `docs/Security.md`, `app/mcp/resources.py`'s docstring, and this phase's release notes — not something release closure should let disappear into history.
6. **Three of `08_ACCEPTANCE.md` §6's original open questions remain genuinely open**, not resolved by this phase: whether Note/Document updates and knowledge-graph link mutations should gain `ActivityLog` logging, whether reads should log at all, and whether OAuth 2.0 is worth building for a future hardening phase. None were silently closed while pursuing release — they are explicitly carried forward as deferred work in `10_RELEASE_NOTES.md`.

## Blocking decisions requiring approval

**None currently.** The owner has completed the mandatory human review gate and authorized release. The remaining steps (commit, tag, push, freeze) are the owner's own directed release-closure sequence, being executed as specified.

## Cross-references

- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md](../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md)
- [../implementation/Phase-11-Claude-MCP/IMPLEMENT.md](../implementation/Phase-11-Claude-MCP/IMPLEMENT.md)
- [../implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md](../implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md)
- [../implementation/Phase-11-Claude-MCP/08_ACCEPTANCE.md](../implementation/Phase-11-Claude-MCP/08_ACCEPTANCE.md)
- [../implementation/Phase-11-Claude-MCP/10_RELEASE_NOTES.md](../implementation/Phase-11-Claude-MCP/10_RELEASE_NOTES.md)
- [../implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M5.md](../implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M5.md)
- [2026-08-19-phase-11-milestone-4-checkpoint.md](2026-08-19-phase-11-milestone-4-checkpoint.md)
- [2026-08-19-phase-11-milestone-3-checkpoint.md](2026-08-19-phase-11-milestone-3-checkpoint.md)
- [2026-08-18-phase-11-milestone-2-checkpoint.md](2026-08-18-phase-11-milestone-2-checkpoint.md)
- [2026-08-18-phase-11-milestone-1-checkpoint.md](2026-08-18-phase-11-milestone-1-checkpoint.md)
