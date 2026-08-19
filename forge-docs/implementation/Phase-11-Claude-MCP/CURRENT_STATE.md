# Phase 11 — Current State

> **Purpose:** Living snapshot of where this phase actually is.
> **Last Updated:** 2026-08-19

---

## 1. Lifecycle stage

**Implementation — Milestone 1 complete, committed (`6854971`); Milestone 2 complete, checkpointed and committed (`4cf1bd2`); Milestone 3 complete, checkpointed and committed. Milestone 4 explicitly NOT authorized — stays closed until the owner opens it.** Per `../../13_PHASE_LIFECYCLE.md`, the phase moved Specification → Authorized → Implementation on 2026-08-18. Milestone 1's gate reached PASS the same day, checkpointed and committed. Milestone 2's gate also reached PASS (one repair cycle), checkpointed and committed per the owner's explicit instruction (*"checkpoint and commit M2, then stop"*). The owner then instructed, in chat, on 2026-08-19: *"Start Milestone 3 implementation"* — read as the separate, explicit authorization `IMPLEMENT.md`'s gate structure requires before any Milestone 3 task begins, matching the precedent Milestones 1 and 2 both required.

The independent Agentic Review (a genuinely separate, no-memory-of-implementation agent, per `09_IMPLEMENTATION_TASKS.md` §0) reached **PASS WITH REQUIRED FIXES** on its first pass (zero BLOCKER, three MAJOR, three MINOR). All six findings were addressed in a repair cycle; the same reviewer independently re-verified every fix — fresh empirical probes reproducing the original failing scenarios, not the fix descriptions — before returning a final verdict of **PASS**. One trivial documentation-staleness item the reviewer caught mid-re-verification (this file and `VERIFICATION_CONTRACT.md` still describing AC18 as "unchanged" after the fix) was corrected immediately afterward. Full record: `reviews/AGENTIC_REVIEW_M3.md`.

The owner then instructed, in chat, on 2026-08-19: *"checkpoint and commit M3, then stop. M4 remains explicitly unauthorized until I open it."* Checkpointed at `forge-docs/history/2026-08-19-phase-11-milestone-3-checkpoint.md` and committed. **This session takes no further action on this phase without a new, explicit instruction** — in particular, no Milestone 4 task, however small, until the owner separately opens it.

## 2. What exists right now

**Planning package** (unchanged in structure since Specification; `01_SPEC.md`/`06_API.md`/`08_ACCEPTANCE.md` gained Milestone-3 corrections, in the same style as Milestone 2's corrections): `README.md`, `01_SPEC.md`, `03_BACKEND.md`, `04_DATABASE.md`, `06_API.md`, `07_TESTING.md`, `08_ACCEPTANCE.md`, `09_IMPLEMENTATION_TASKS.md`.

**Milestone 1 implementation** (committed at `6854971`): MCP transport/auth foundation. Full detail in `forge-docs/history/2026-08-18-phase-11-milestone-1-checkpoint.md`.

**Milestone 2 implementation** (checkpointed and committed): the 12 Knowledge CRUD tools (Notes/Documents/Projects). Full detail in `forge-docs/history/2026-08-18-phase-11-milestone-2-checkpoint.md`.

**Milestone 3 implementation** (new, 2026-08-19, Agentic Review PASS, checkpointed and committed):
- `backend/app/services/notes/service.py::search_notes`, `backend/app/services/documents/service.py::search_documents` — additive `project_id: str | None = None` keyword-only param, applied inside the FTS5 query before `LIMIT 50` (M3-T0a).
- `backend/app/services/knowledge/service.py::list_links_for_items` — new batch link-retrieval method, one query for the links themselves plus at most one query per referenced item type (note/document) for titles, regardless of item count (M3-T0b). `_tags_for` promoted to public `tags_for_items` (now has two real call sites: `list_knowledge` and the new `forge_context`).
- `backend/app/mcp/tools/search.py` (new) — `forge_search`, `forge_context`. Both call `notes_service.search_notes`/`documents_service.search_documents` directly (never `search_service.global_search`, which also returns Secrets). `forge_context`'s `links` output is filtered to edges between two matched items only (repair-cycle fix — see below).
- `backend/app/mcp/tools/knowledge.py` (new) — `forge_link_items`, `forge_unlink_items`, calling `knowledge_service` directly (the pre-anticipated, documented exception to "each tool calls its own domain's service" — linking is inherently cross-item). Both produce zero `ActivityLog` rows, a documented exception matching `update_note`/`update_document`'s existing precedent (repair-cycle finding — see below).
- `backend/app/mcp/tools/projects.py::_to_mcp_out` promoted to public `project_to_mcp_out` (reused by `search.py` for `forge_context`'s project field).
- `backend/app/mcp/server.py` — all 16 tools now registered (12 from Milestone 2 + 4 new). Every tool across all five modules now carries an explicit `description=` visible via `tools/list` (repair-cycle fix, verified live).
- `backend/tests/test_mcp_tools_search_context.py` (new, 13 tests), `backend/tests/test_mcp_tools_knowledge.py` (new, 7 tests), `backend/tests/test_knowledge_service.py` (+3 tests for `list_links_for_items`, including the AC13b query-count assertion), `backend/tests/test_mcp_server.py` (tool-list assertion updated to the real 16-tool set) — all green, alongside the full pre-existing backend suite (**377/377**, zero regressions) and FDK suite (**113/113**).
- `VERIFICATION_CONTRACT.md` updated in place for the Milestone 3 gate, including the repair-cycle findings and corrected AC18 status.
- Docker build check (`docker build ./backend`) succeeded.

**Milestone 3 repair cycle** (2026-08-19, in response to the Agentic Review's first-pass findings, all independently re-verified fixed in its second pass): three MAJOR findings — knowledge-graph link create/delete's undocumented lack of `ActivityLog` rows (resolved by documenting it as a deliberate exception, not by silently adding new logging behavior that would affect every REST caller too), all 16 MCP tools' empty `tools/list` descriptions (fixed by adding explicit `description=` to every tool, including restoring `06_API.md`'s already-required HTML-not-Markdown warning for `forge_create_document`/`forge_update_document`), `forge_context` emitting links to items outside its own matched set (fixed by filtering to intra-matched-set edges only) — and three MINOR findings: `forge_context`'s `topic` gained `forge_search`'s existing 200-char cap; the aggregate test now actually exercises tags; test counts corrected. Full detail in `reviews/AGENTIC_REVIEW_M3.md` §5.

## 3. What does NOT exist yet (correctly, per Milestone 3's scope boundary)

- `forge_capture_session`/`forge_capture_decision`, resource exposure (`forge://projects`) — Milestone 4 scope.
- `02_UI.md`, `05_COMPONENTS.md` — still deliberately omitted.
- A token-management UI — still an open question for Milestone 5.
- `forge-docs/02_ROADMAP.md` update — still deliberately deferred to the Released/Frozen stage.
- No new Alembic migration this milestone — no new table/column was needed (`list_links_for_items` and the `project_id` search params are pure query-shape additions over existing tables).

## 4. Immediate next step

**Milestone 3 is checkpointed and committed, per explicit owner instruction (*"checkpoint and commit M3, then stop. M4 remains explicitly unauthorized until I open it."*). Stopped here — Milestone 4 is not authorized** and this session takes no further action on this phase without a new, explicit instruction.

**Next:** owner authorizes Milestone 4 (Claude Memory Workflows) as a separate, explicit act whenever ready — not before.

## 5. Known findings from Milestone 3 (kept here as institutional memory, not just in the review artifact)

1. **`06_API.md`'s `forge_link_items` idempotency claim ("re-linking returns the existing link") described the *tool's* required behavior, not what `knowledge_service.create_link` actually does.** The real service raises `AppError(code="knowledge_link_duplicate", status_code=409)` on an exact re-link (protecting the REST API's own duplicate-prevention UX). The MCP tool handler catches exactly that error code and re-fetches the existing link instead of propagating it — verified in both link directions. Same class of gap as Milestone 2's `update_note` audit-logging finding: a planning document describing desired behavior is not the same as the underlying function already producing it.
2. **Two private service helpers promoted to public, not duplicated**: `knowledge_service._tags_for` → `tags_for_items`, `app/mcp/tools/projects.py::_to_mcp_out` → `project_to_mcp_out`. Both are the same "internal helper gains a second legitimate caller, so it gets promoted rather than copy-pasted" pattern `03_BACKEND.md` §2.1 anticipated for `list_links_for_items` specifically.
3. **`forge_search` validates `project_id` for consistency, beyond what `06_API.md`'s original draft strictly required** (only `forge_context`'s row stated this). A deliberate, documented narrowing toward a stricter failure mode.
4. **Knowledge-graph link create/delete produce no `ActivityLog` row — found by the Agentic Review, not the implementing session.** `knowledge_service.create_link`/`delete_link` have never logged for any caller, REST or MCP. Documented as a deliberate exception (same shape as `update_note`/`update_document`'s existing one) rather than silently fixed by adding new logging behavior that would change existing REST callers' behavior too — that would have been exactly the kind of unplanned audit-design change Milestone 2's own execution rules require asking about first. Tracked as a new open question in `08_ACCEPTANCE.md` §6.
5. **All 16 MCP tools had empty `tools/list` descriptions until the repair cycle — including a violation of an already-written `06_API.md` requirement** (`forge_create_document`'s HTML-not-Markdown warning was documented as required but never actually surfaced to a caller). Fixed across all five tool modules, verified via a live `tools/list` probe showing zero empty descriptions.
6. **`forge_context`'s original `links` output could reference items outside its own matched `notes`/`documents` set** — a dangling ID with no accompanying title anywhere in the same response, diverging from `01_SPEC.md` §5.2's "links between the matched items" wording. Fixed by filtering to intra-matched-set edges only; verified by reproducing the exact original failing scenario.

## 6. Recommended next prompt (for whoever picks this up)

"Milestone 3 is checkpointed and committed; Milestone 4 is explicitly not authorized and stays closed until the owner opens it. Review `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md` and `reviews/AGENTIC_REVIEW_M3.md`, then authorize Milestone 4 (Claude Memory Workflows) explicitly when ready — not implied by anything above."

## 7. Cross-references

- [README.md](README.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md)
- [reviews/AGENTIC_REVIEW_M1.md](reviews/AGENTIC_REVIEW_M1.md)
- [reviews/AGENTIC_REVIEW_M2.md](reviews/AGENTIC_REVIEW_M2.md)
- [reviews/AGENTIC_REVIEW_M3.md](reviews/AGENTIC_REVIEW_M3.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../history/2026-08-18-phase-11-milestone-1-checkpoint.md](../../history/2026-08-18-phase-11-milestone-1-checkpoint.md)
- [../../history/2026-08-18-phase-11-milestone-2-checkpoint.md](../../history/2026-08-18-phase-11-milestone-2-checkpoint.md)
- [../../history/2026-08-19-phase-11-milestone-3-checkpoint.md](../../history/2026-08-19-phase-11-milestone-3-checkpoint.md)
