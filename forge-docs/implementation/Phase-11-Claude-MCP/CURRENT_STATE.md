# Phase 11 — Current State

> **Purpose:** Living snapshot of where this phase actually is.
> **Last Updated:** 2026-08-18

---

## 1. Lifecycle stage

**Implementation — Milestone 1 complete, committed (`6854971`); Milestone 2 complete, gate PASS, checkpointed and committed; Milestone 3 not authorized.** Per `../../13_PHASE_LIFECYCLE.md`, the phase moved Specification → Authorized → Implementation on 2026-08-18. Milestone 1's gate reached PASS the same day, checkpointed and committed. The owner then authorized Milestone 2 (Knowledge CRUD) as a separate, explicit act; Milestone 2's mechanical verification contract and independent Agentic Review (one repair cycle — see §5) both reached PASS, and the owner then separately instructed the checkpoint and commit (*"checkpoint and commit M2, then stop"*). **Milestone 3 is not authorized** — the instruction was to stop, and nothing here should be read as implying otherwise.

## 2. What exists right now

**Planning package** (unchanged since Specification): `README.md`, `01_SPEC.md`, `03_BACKEND.md`, `04_DATABASE.md`, `06_API.md`, `07_TESTING.md`, `08_ACCEPTANCE.md`, `09_IMPLEMENTATION_TASKS.md` — `01_SPEC.md`/`06_API.md`/`08_ACCEPTANCE.md` corrected during Milestone 2 implementation where real code diverged from planning assumptions (see §5).

**Milestone 1 implementation** (committed at `6854971`): MCP transport/auth foundation — `backend/app/mcp/` (`auth.py`, `server.py`), `services/mcp/tokens.py`, `POST/GET/DELETE /api/mcp/tokens`, `mcp_tokens` table + `activity_log.source` column, nginx/Docker wiring, the new Agentic Review FDK verifier. Full detail in `forge-docs/history/2026-08-18-phase-11-milestone-1-checkpoint.md`.

**Milestone 2 implementation** (new, 2026-08-18, checkpointed and committed):
- `backend/app/mcp/tools/` — `notes.py`, `documents.py`, `projects.py` (12 tools total), `_common.py` (shared `tool_session`/`current_scope`/`filtered_update_kwargs`/`validate_project_id` helpers).
- `backend/app/mcp/server.py` — all 12 tools registered via each module's `register(server)`.
- `backend/app/services/activity.py`, `notes/service.py`, `documents/service.py`, `projects/service.py` — `source: str = "ui"` threaded into every *existing* `activity.record(...)` call site (create/delete for Notes/Documents, create/update/delete for Projects); **deliberately not added** to `update_note`/`update_document`, which never logged for any caller — see §5.
- `backend/tests/test_mcp_tools_crud.py` (31 tests), `test_mcp_tools_static_checks.py` (4 tests, recursive `app/mcp/**` scan) — all green, alongside the full pre-existing backend suite (unchanged, zero regressions) and FDK suite (113/113).
- `VERIFICATION_CONTRACT.md` updated in place for the Milestone 2 gate; independent review recorded at [`reviews/AGENTIC_REVIEW_M2.md`](reviews/AGENTIC_REVIEW_M2.md).

**Committed to git** (checkpoint + commit, per explicit owner instruction) — no tag, merge to a release branch, or push has occurred; this is an ordinary commit on the working branch, not a release act.

## 3. What does NOT exist yet (correctly, per Milestone 2's scope boundary)

- `forge_search`, `forge_context`, `forge_link_items`, `forge_unlink_items` — Milestone 3 scope.
- `forge_capture_session`/`forge_capture_decision`, resource exposure (`forge://projects`) — Milestone 4 scope.
- `knowledge_service.list_links_for_items` (batch link retrieval) — Milestone 3 scope, correctly untouched this milestone (Milestone 2's tools only call `purge_links_for`/existing single-item `get_note`/`get_document`, no batch operation needed yet).
- `02_UI.md`, `05_COMPONENTS.md` — still deliberately omitted.
- A token-management UI — still an open question for Milestone 5.
- `forge-docs/02_ROADMAP.md` update — still deliberately deferred to the Released/Frozen stage.

## 4. Immediate next step

**Milestone 2 checkpointed and committed, per explicit owner instruction (*"checkpoint and commit M2, then stop"*). Stopped here — Milestone 3 is not authorized** and this session takes no further action on this phase without a new, explicit instruction.

Summary of the Milestone 2 gate:
1. All 7 tasks (M2-T0 through M2-T6) complete.
2. Mechanical verification: all 7 applicable FDK verifiers PASS against the real repository.
3. Independent Agentic Review: **PASS WITH REQUIRED FIXES** on first pass — found one BLOCKER (a boolean-coercion bypass in the `confirm: true` delete-safety check, see §5) and two MAJOR findings (a raw DB exception leak on a bad `project_id`; an output-shape documentation ambiguity), plus several MINOR test-coverage/robustness gaps. All fixed; the same reviewer independently re-verified every fix (fresh empirical probes, not the fix description) before updating its verdict to PASS. Full detail in `reviews/AGENTIC_REVIEW_M2.md`.
4. Checkpointed at `forge-docs/history/2026-08-18-phase-11-milestone-2-checkpoint.md` and committed.

**Next:** owner authorizes Milestone 3 (Search, Context & Knowledge Graph) as a separate, explicit act whenever ready — not before.

## 5. Known findings from Milestone 2 (kept here as institutional memory, not just in the review artifact)

1. **The plan's own assumption about audit logging was wrong, caught by re-reading the actual baseline code, not by trusting prior research.** `01_SPEC.md` §4.5 (written during planning) assumed every create/update/delete service function already called `activity.record(...)`. Verified false for `notes_service.update_note`/`documents_service.update_document` specifically (only create/delete log, for any caller, today). Corrected in the spec; `forge_update_note`/`forge_update_document` correctly produce zero `ActivityLog` rows, matching existing REST behavior rather than introducing new logging as an unplanned side effect.
2. **Security BLOCKER, caught by the independent Agentic Review**: `confirm: bool` on `forge_delete_note`/`forge_delete_document` let Pydantic's lax validation coerce `"true"`, `"1"`, `1`, etc. into Python `True`, silently defeating the "confirm is structural, never inferred" guarantee `01_SPEC.md` §6 requires. Fixed with `pydantic.StrictBool`; regression tests added covering every previously-exploitable coerced value, each also confirming the target record still exists afterward.
3. **MAJOR, caught by the same review**: an unvalidated `project_id` on note/document create/update reached the database unchecked and surfaced as a raw `sqlite3.IntegrityError` — leaking the SQL statement and submitted content to the tool caller instead of the documented clean not-found error. Fixed with `_common.py::validate_project_id`, called before every create/update service call that accepts a `project_id`.
4. **MAJOR, caught by the same review**: `06_API.md`'s original wording ("`default_provider`/`default_model` excluded from the tool surface") was ambiguous and, read literally, contradicted the actual (correct) behavior of still returning those fields on reads. Resolved by clarifying the docs — the exclusion is write-input-only; these are non-sensitive fields already exposed via the existing REST `ProjectOut`, unlike `secret_count`, which has a real confidentiality reason for exclusion.
5. **Two documented tool-surface narrowings versus the original `06_API.md` draft, found during implementation, not the plan**: `z_index` dropped from `forge_update_note` (same UI-placement-concern category as `pos_x`/`pos_y`/`width`/`height`, already excluded from create); `default_provider`/`default_model` dropped from project *write* input (avoids pulling Model Playground's provider/model registry validation into a knowledge-substrate tool).
6. **An MCP SDK serialization quirk, not a bug in this codebase**: a tool returning a `list[...]` wraps it as `{"result": [...]}` in `structuredContent` while `content[0].text` only previews the first item; a bare `dict` return sometimes populates `structuredContent` directly and sometimes doesn't. Test helpers were written to handle both cases robustly — flagged here so Milestone 3's `forge_search`/`forge_context` (which return lists/aggregates) don't rediscover this from scratch.

## 6. Recommended next prompt (for whoever picks this up)

"Milestone 2 is checkpointed and committed; Milestone 3 is not authorized. Review `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md` and `reviews/AGENTIC_REVIEW_M2.md`, then authorize Milestone 3 (Search, Context & Knowledge Graph) explicitly when ready — not implied by anything above."

## 7. Cross-references

- [README.md](README.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md)
- [reviews/AGENTIC_REVIEW_M1.md](reviews/AGENTIC_REVIEW_M1.md)
- [reviews/AGENTIC_REVIEW_M2.md](reviews/AGENTIC_REVIEW_M2.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../history/2026-08-18-phase-11-milestone-1-checkpoint.md](../../history/2026-08-18-phase-11-milestone-1-checkpoint.md)
