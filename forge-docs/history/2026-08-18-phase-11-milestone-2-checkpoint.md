# Checkpoint — Claude MCP / Second Brain (Phase 11) — 2026-08-18 (Milestone 2)

> **Trigger:** Milestone completion. Milestone 2 (Knowledge CRUD) of [Phase-11-Claude-MCP](../implementation/Phase-11-Claude-MCP/README.md) reached a passing Agentic Review gate. Per [`../10_CHECKPOINT_PROTOCOL.md`](../10_CHECKPOINT_PROTOCOL.md) §1.
> **Phase:** [Phase-11-Claude-MCP](../implementation/Phase-11-Claude-MCP/README.md)
> **Last Updated:** 2026-08-18

---

```
Phase 11
Milestone 2 — PASS
Mechanical verification: 8/8
Agentic Review: PASS (after one repair cycle)
Security findings: resolved (1 BLOCKER, 2 MAJOR, several MINOR)
Regression tests added: yes
M3: NOT AUTHORIZED
Phase 11: NOT RELEASED
Phase 11: NOT FROZEN
```

This is a **milestone checkpoint, not a release and not a freeze.** Milestone 1 is already committed at `6854971`; this checkpoint covers Milestone 2's work only. Phase 11 remains in **Implementation**, two of five milestones complete, per [`../13_PHASE_LIFECYCLE.md`](../13_PHASE_LIFECYCLE.md).

## Completed Tasks

All seven Milestone 2 tasks from [`09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-11-Claude-MCP/09_IMPLEMENTATION_TASKS.md):

- **M2-T0** — `source: str = "ui"` threaded into every service function that already called `activity.record(...)` (Notes/Documents create+delete, Projects create+update+delete) — **not** added to `update_note`/`update_document`, which the plan incorrectly assumed already logged (verified false against the actual baseline; corrected in `01_SPEC.md` §4.5)
- **M2-T1** — `notes_service.get_note` added, matching `documents_service.get_document`'s shape
- **M2-T2** — `app/mcp/tools/notes.py` — 4 tools, corrected 3-step delete sequence
- **M2-T3** — `app/mcp/tools/documents.py` — 4 tools, identical sequence
- **M2-T4** — `app/mcp/tools/projects.py` — 4 tools (list/get/create/update, no delete), `secret_count` excluded from output
- **M2-T5** — All 12 tools registered in `app/mcp/server.py::build_mcp_server`, scope-gated per `01_SPEC.md` §4.4
- **M2-T6** — `VERIFICATION_CONTRACT.md` updated in place for the Milestone 2 gate

Plus the gate itself: full mechanical verification (7/7 applicable verifiers) and an independent Agentic Review, including **one substantive repair cycle** — see Known Risks.

## Modified Files

**Created**
- `backend/app/mcp/tools/__init__.py`, `_common.py`, `notes.py`, `documents.py`, `projects.py`
- `backend/tests/test_mcp_tools_crud.py` (31 tests), `test_mcp_tools_static_checks.py` (4 tests)
- `forge-docs/implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M2.md`
- `forge-docs/history/2026-08-18-phase-11-milestone-2-checkpoint.md` (this file)

**Modified**
- `backend/app/mcp/server.py` (tool registration — all 12 tools wired in)
- `backend/app/services/activity.py`, `notes/service.py`, `documents/service.py`, `projects/service.py` (`source` threading; `get_note` added)
- `backend/tests/test_mcp_server.py` (Milestone-1-era "zero tools" assertion updated to the real, current 12-tool set — a correct update to a fact that changed on purpose, not a regression)
- `forge-docs/implementation/Phase-11-Claude-MCP/01_SPEC.md`, `06_API.md`, `08_ACCEPTANCE.md` (corrected against verified implementation findings — see Known Risks)
- `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md`, `IMPLEMENT.md`, `VERIFICATION_CONTRACT.md`

**Untouched, confirmed by the Architecture Verifier and the Agentic Review independently**: `backend/app/services/secrets/`, `crypto/`, `settings/`; `backend/app/api/deps.py` (`AuthDep`/`require_auth`); `backend/app/mcp/auth.py` (`McpBearerAuthMiddleware`, the token/scope model); `backend/alembic/`; `frontend/`.

## Current State

Claude can now create, read, update, and delete Notes and Documents, and create/read/update Projects, through the MCP surface built in Milestone 1 — the first milestone where the system holds real write/delete authority over persistent user data:

```
Claude
  ↓
forge_create_note / forge_update_note / forge_delete_note   (+ same for documents)
  ↓                                                           forge_list/get/create/update_project
require_scope (forge:read / forge:write / forge:delete)
  ↓
services/notes, services/documents, services/projects   (same functions the REST routes call)
  ↓
SQLite
```

Deletes require a literal, non-coercible `confirm: true` and follow an existence-check-first sequence before any `knowledge_links` mutation is staged. Every create/delete produces exactly one `ActivityLog` row with `source="mcp"`; update logging follows the pre-existing REST asymmetry (Notes/Documents updates unlogged, Project updates logged) rather than introducing new behavior. Zero MCP code path reaches Secrets, Crypto, or Settings — confirmed by a static check that now recursively scans all of `app/mcp/`, not just the tool files.

**Gate result:** mechanical verification 8/8. Agentic Review: PASS, after one repair cycle — see Known Risks.

## Remaining Work

Milestones 3–5 of [`09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-11-Claude-MCP/09_IMPLEMENTATION_TASKS.md), **none authorized**:

- **Milestone 3 — Search, Context & Knowledge Graph.** `forge_search`, `forge_context`, `forge_link_items`, `forge_unlink_items`. Needs its own scoping/review discipline, same as Milestone 2 — not implied by this checkpoint.
- Milestones 4–5 (Memory Workflows, Production Hardening) unchanged, downstream of Milestone 3.

## Recommended Next Prompt

> Milestone 2 is checkpointed and committed; Milestone 3 is not authorized. When ready, review `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md` and `reviews/AGENTIC_REVIEW_M2.md`, then authorize Milestone 3 explicitly as its own act — not implied by this checkpoint. On authorization, update `IMPLEMENT.md`'s Status line to record it as a separate, dated gate (matching how Milestones 1 and 2's authorizations are recorded there), then begin `09_IMPLEMENTATION_TASKS.md`'s Milestone 3 task table.

## Known Risks

1. **The Agentic Review's first pass was not a clean PASS, and the finding was real.** `forge_delete_note`/`forge_delete_document`'s `confirm: bool` parameter let Pydantic's default lax boolean coercion accept `"true"`, `"True"`, `"1"`, `"yes"`, and `1` as authorization to permanently delete — exactly the "soft signal substituting for the literal field" failure mode `01_SPEC.md` §6 says must be structurally impossible. Fixed with `pydantic.StrictBool`; the same reviewer independently re-verified the fix with a fresh exploit attempt (not a re-run of the implementer's own test) before updating its verdict. Worth remembering going into Milestone 3/4: a spec stating an intended guarantee is not the same as an enforced one, and the gap here was in code that read as correct on casual inspection.
2. **Two MAJOR findings, both fixed**: an unvalidated `project_id` on note/document create/update reached the database unchecked and surfaced a raw `sqlite3.IntegrityError` (SQL and submitted content leaked to the caller) instead of the documented clean not-found error — fixed with a `validate_project_id` check added ahead of the service call; and an ambiguous doc claim about `default_provider`/`default_model` being "excluded from the tool surface," which read output-shape docs as stricter than the (correct) actual behavior — resolved by clarifying the exclusion is write-input-only, since these are non-sensitive fields already exposed via the existing REST `ProjectOut`.
3. **The plan's own assumption about audit logging was wrong**, caught by re-reading the actual baseline code rather than trusting prior research: `update_note`/`update_document` never logged to `ActivityLog` for any caller, contradicting `01_SPEC.md`'s original draft. Corrected in the spec and preserved (not "fixed") in the implementation, since adding new logging there would itself be an unplanned behavior change to existing REST routes.
4. **An MCP SDK serialization quirk, not a bug in this codebase**: a tool returning a list wraps it as `{"result": [...]}` in `structuredContent` while `content[0].text` only previews the first item; a bare `dict` return sometimes populates `structuredContent` and sometimes doesn't. Test helpers handle both cases; flagged for Milestone 3, whose `forge_search`/`forge_context` will return lists/aggregates and would otherwise rediscover this from scratch.
5. **No frontend surface for MCP token management** — unchanged from Milestone 1, still an open question for Milestone 5.

## Blocking decisions requiring approval

**None currently.** As with Milestone 1, the standing request from the owner is procedural, not a specific blocker: Milestone 3 gets its own explicit authorization, its own scoping discussion, and the same unhurried review discipline Milestone 2 got — not inferred from this checkpoint or rushed on the strength of two consecutive PASS gates.

## Cross-references

- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md](../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md)
- [../implementation/Phase-11-Claude-MCP/IMPLEMENT.md](../implementation/Phase-11-Claude-MCP/IMPLEMENT.md)
- [../implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md](../implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md)
- [../implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M2.md](../implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M2.md)
- [2026-08-18-phase-11-milestone-1-checkpoint.md](2026-08-18-phase-11-milestone-1-checkpoint.md)
