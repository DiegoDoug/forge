# Phase 11 — Verification Contract

> **Status:** Milestone 3 implementation complete, gate **PASS** (Agentic Review, second/final pass, after a repair cycle addressing the first pass's 3 MAJOR + 3 MINOR findings — see `reviews/AGENTIC_REVIEW_M3.md`), **checkpointed and committed** per explicit owner instruction. Milestone 1/2/3's gate content is preserved in `../../history/2026-08-18-phase-11-milestone-1-checkpoint.md`, `../../history/2026-08-18-phase-11-milestone-2-checkpoint.md`, `../../history/2026-08-19-phase-11-milestone-3-checkpoint.md`, `reviews/AGENTIC_REVIEW_M1.md`, `reviews/AGENTIC_REVIEW_M2.md` — this file always reflects the *current* milestone's gate, not phase history. **Milestone 4 is explicitly not authorized and stays closed until the owner opens it.**
> **Last Updated:** 2026-08-19

## 1. Phase Metadata

- **Phase name:** Phase 11 — Claude MCP / Second Brain
- **Phase objective:** Expose a scoped, semantic MCP interface over Forge's Notes/Documents/Projects/Knowledge Hub so Claude can use Forge as persistent knowledge substrate, without duplicating Forge's service layer or exposing Secrets/Settings/Crypto.
- **Dependencies:** Phase 06 (Projects), Phase 07 (Knowledge Hub) — both released & frozen, satisfied as-is. Milestone 1 (MCP Foundation) — complete, committed at `6854971`. Milestone 2 (Knowledge CRUD) — complete, checkpointed and committed.
- **Completion definition (this milestone):** `forge_search`, `forge_context`, `forge_link_items`, `forge_unlink_items` implemented per `06_API.md` §1, §3; every mechanical verifier passes; an independent Agentic Review records a PASS verdict.
- **Milestone:** Milestone 3 — Search, Context & Knowledge Graph

## 2. Required Tasks

- [x] M3-T0a — `project_id: str | None = None` param added to `notes_service.search_notes`/`documents_service.search_documents`, applied inside the FTS query before `LIMIT 50`
- [x] M3-T0b — `knowledge_service.list_links_for_items(session, items)` — batch link retrieval, one query for a whole result set (plus at most one query per referenced item type for titles)
- [x] M3-T1 — `app/mcp/tools/search.py` — `forge_search` (calls `notes_service.search_notes`/`documents_service.search_documents` directly, never `search_service.global_search`; `project_id` threaded through per M3-T0a)
- [x] M3-T2 — `forge_context` composition — uses `list_links_for_items` (M3-T0b), not one `list_links` call per matched item
- [x] M3-T3 — `app/mcp/tools/knowledge.py` — `forge_link_items`, `forge_unlink_items`
- [x] M3-T4 — Tool registry wiring for the 4 new tools — all 16 tools now registered in `app/mcp/server.py::build_mcp_server`
- [x] M3-T5 — This document, updated

## 3. Acceptance Criteria

From `08_ACCEPTANCE.md` §3 (Search & context), plus the AC10/AC20 carry-forward checks re-verified against the new tools:

- [x] AC10 — No MCP tool exposes `Secret` data, `secret_count`, or any crypto primitive — re-verified for the two new tools (`test_mcp_tools_search_context.py::test_forge_search_never_returns_secret_data`; `test_mcp_tools_static_checks.py`'s import-boundary check, which recursively scans all of `app/mcp/**` and therefore already covered `search.py`/`knowledge.py` the moment they were added)
- [x] AC11 — `forge_context` returns the project record, matching Notes/Documents, their tags, and their existing links, for a project — every field backed by an existing Forge query (`test_forge_context_aggregates_project_notes_documents_tags_links`)
- [x] AC12 — `forge_search` never returns Secret names/metadata, unlike `search_service.global_search` (`test_forge_search_never_returns_secret_data`)
- [x] AC13 — An invalid `project_id` passed to `forge_context` produces an explicit not-found error, not silently-unfiltered results (`test_forge_context_invalid_project_id_errors_not_silently_unfiltered`)
- [x] AC13a — A project-scoped `forge_search`/`forge_context` call is constrained at the query itself, not post-filtered after the 50-per-type cap — proven with an adversarial fixture where an unscoped-then-filtered implementation would provably return 0 of the target project's 30 matches (`test_forge_search_project_scoping_is_query_level_not_post_filtered`)
- [x] AC13b — `forge_context`'s link lookup issues a bounded, small number of queries (<=3) regardless of result-set size, verified by query-count assertion at 50+50 matched items (`test_knowledge_service.py::test_list_links_for_items_issues_a_bounded_query_count_regardless_of_item_count`)
- [x] AC20 — No MCP tool handler contains a raw ORM call — static check across `app/mcp/**`, re-run against the two new modules (`test_mcp_tools_static_checks.py::test_no_mcp_module_calls_the_orm_directly`)

AC1–AC10, AC16–AC17, AC19 (Milestone 1/2 connectivity, auth, CRUD, regression) remain satisfied, unchanged. **AC18 gained a new, documented exception this milestone** (corrected from an earlier draft of this section that inaccurately claimed AC18 was untouched — flagged by the Agentic Review's fix-verification pass): `app/mcp/tools/knowledge.py` is a new file introducing `forge_link_items`/`forge_unlink_items`, and `knowledge_service.create_link`/`delete_link` (which they call) have never logged to `ActivityLog` for any caller, REST or MCP — the same class of exception `01_SPEC.md` §4.5 already documents for `update_note`/`update_document`, now also documented there, in `06_API.md`'s Audit rows for both tools, and in `08_ACCEPTANCE.md` AC18/§6. Verified by `test_forge_link_and_unlink_items_produce_no_activity_row_matching_existing_rest_behavior`. AC14/AC15 (memory workflows) are Milestone 4 scope, intentionally not listed here.

## 4. Expected File Scope

- **Expected new/modified files or directories:** `backend/app/mcp/tools/search.py` (new), `backend/app/mcp/tools/knowledge.py` (new), `backend/app/mcp/tools/projects.py` (`_to_mcp_out` → `project_to_mcp_out`, made public for reuse by `search.py`; tool descriptions added in the repair cycle), `backend/app/mcp/tools/notes.py`, `backend/app/mcp/tools/documents.py` (**repair-cycle addition, not original scope**: tool descriptions added — see §10 finding M2 — no other change), `backend/app/mcp/server.py` (registration), `backend/app/services/notes/service.py`, `backend/app/services/documents/service.py` (`project_id` param), `backend/app/services/knowledge/service.py` (`list_links_for_items` added; `_tags_for` → `tags_for_items`, made public for reuse by `search.py`), `backend/tests/test_mcp_tools_search_context.py` (new), `backend/tests/test_mcp_tools_knowledge.py` (new), `backend/tests/test_knowledge_service.py` (batch-link tests added), `backend/tests/test_mcp_server.py` (tool-list assertion updated), `forge-docs/`
- **Explicitly out of scope:** `backend/app/services/secrets/`, `backend/app/services/crypto/`, `backend/app/services/settings/`, `backend/app/api/deps.py`, `backend/app/mcp/auth.py` (unmodified — `git diff --stat` confirms empty), `backend/alembic/` (no new migration — no new table/column this milestone), `frontend/`

## 5. Required Validation Commands

- [x] Test: cd backend && .venv/Scripts/python.exe -m pytest -q — 377 passed (independently re-run and re-confirmed by the Agentic Review's fix-verification pass, including a `--collect-only` count check)
- [x] Test fdk suite: backend/.venv/Scripts/python.exe -m pytest tools/tests -q — 113 passed
- [x] Build: docker build -t forge-mcp-m3-buildcheck ./backend — succeeded

## 6. Architecture Constraints

- [x] `backend/app/mcp/tools/**` imports only `services/notes`, `services/documents`, `services/projects`, `services/knowledge` — no import of `services/secrets`, `services/crypto`, `services/settings` anywhere (`test_mcp_tools_static_checks.py`, unchanged check, now also scanning `search.py`/`knowledge.py`).
- [x] `AuthDep`/`require_auth`/`api/deps.py`, `app/mcp/auth.py` unmodified this milestone (`git diff --stat` confirms empty). `app/mcp/tools/notes.py`/`documents.py` gained tool-description additions only during the repair cycle (§10 finding M2) — no logic change; `git diff` for those two files is description-string-only.
- [x] Every tool handler reaches data exclusively through a `services/*` function — zero raw `session.get`/`session.execute` calls in `app/mcp/tools/**` (AC20, statically checked). `forge_link_items`/`forge_unlink_items` calling `knowledge_service` directly (rather than a domain-specific service) is the documented, pre-anticipated exception `test_mcp_tools_static_checks.py`'s own comment already called out during Milestone 2 — linking is inherently cross-item, and `knowledge_service` already owns that logic for the REST API too.
- [x] **Documented deviation, found during implementation**: `06_API.md`'s original `forge_link_items` draft ("re-linking returns the existing link, per the service's normalization") turns out to describe the *tool's* required behavior, not `knowledge_service.create_link`'s actual behavior — the service itself raises `AppError(code="knowledge_link_duplicate", status_code=409)` on an exact re-link, to protect the REST API's own duplicate-prevention UX. `app/mcp/tools/knowledge.py::forge_link_items` catches exactly that error code and re-fetches the existing link via `list_links` instead of propagating it. Verified in both directions (`test_forge_link_items_relink_either_direction_returns_existing_link_not_an_error`) — this is the same class of "spec describes desired behavior; a thin translation layer is what actually produces it" gap Milestone 2 found for `update_note`'s audit logging (see `06_API.md`'s updated `forge_link_items` row for the full note).
- [x] **Documented deviation, found during implementation**: `forge_search` validates `project_id` via the existing `validate_project_id` helper even though `06_API.md`'s original per-tool row only stated this requirement for `forge_context` — applied for consistency with every other `project_id`-accepting tool (a bad ID should error, not silently produce empty-looking-but-actually-just-unfiltered results). A narrowing of behavior toward stricter validation, not a scope expansion of what the tool does.
- [x] **Service-layer reuse, not duplicated logic**: `knowledge_service._tags_for` (private, list_knowledge-only) was promoted to `tags_for_items` (public) rather than reimplementing the same batched-tag-lookup query inside `search.py`; `app/mcp/tools/projects.py::_to_mcp_out` was promoted to `project_to_mcp_out` (public) rather than reimplementing project-output-shaping (including the `secret_count` exclusion) inside `search.py`. Both are the same kind of internal-helper-becomes-shared-function refactor `03_BACKEND.md` §2.1 anticipated for `list_links_for_items`, applied to two more cases discovered during implementation.

## 7. Documentation Requirements

- [x] `06_API.md` — `forge_search`'s Validation row updated to note the `project_id` validation deviation; `forge_link_items`'s Underlying-service row updated to document the duplicate-link translation
- [x] `CURRENT_STATE.md` — updated to reflect Milestone 3 completion
- [x] `IMPLEMENT.md` — Milestone 3 section added (mission, read order, execution rules, quality gates), following the exact structure Milestones 1 and 2 established

## 8. Regression Targets

- [x] Full existing backend test suite green (one expected, intentional update: `test_mcp_server.py`'s Milestone-2-era 12-tool assertion updated to assert the real, current 16-tool set — not a regression, a correct update to a fact that changed on purpose)
- [x] Existing REST API behavior provably unchanged — `notes_service.search_notes`/`documents_service.search_documents`'s three existing call sites (`api/routes/notes.py`, `api/routes/documents.py`, `services/search/service.py`, `services/knowledge/service.py`'s `_candidate_notes`/`_candidate_documents`) all call with exactly two positional args, unaffected by the additive keyword-only `project_id` default
- [x] FDK verification framework tests remain green (113/113, unchanged by this milestone)

## 9. Required Verification Agents

- [x] Specification
- [x] Architecture
- [x] Build
- [x] Test
- [x] Regression
- [x] Code Quality
- [x] Documentation
- [ ] UX — not required (backend-only milestone)
- [x] Agentic Review — required. **Final verdict: PASS** (first pass: PASS WITH REQUIRED FIXES, 0 BLOCKER/3 MAJOR/3 MINOR; repair cycle applied; second pass independently re-verified all 6 fixes with fresh empirical probes, not the fix descriptions). Full record at `reviews/AGENTIC_REVIEW_M3.md`.

## 10. Known findings from this milestone (for the Agentic Review's attention)

**Findings 6–11 below were raised by the Agentic Review's first pass and addressed in a repair cycle, independently re-verified in its second pass (see `reviews/AGENTIC_REVIEW_M3.md` §5 for the full re-verification detail) — kept here per this section's own convention of recording findings as institutional memory, not just in the review artifact:**

6. **MAJOR — `forge_link_items`/`forge_unlink_items` produced zero `ActivityLog` rows, undocumented.** Resolved by documenting it as a deliberate REST-parity exception (matching the `update_note`/`update_document` precedent), not by silently adding new logging behavior that would change existing REST callers' behavior too — `01_SPEC.md` §4.5, `06_API.md`'s Audit rows, `08_ACCEPTANCE.md` AC18/§6 all updated; regression test added. Independently re-verified: the exception is real, pre-existing REST behavior (not new), and is now honestly documented rather than silently reintroduced.
7. **MAJOR — all 16 MCP tools returned an empty `tools/list` description, including `forge_create_document`'s already-required-but-missing HTML-not-Markdown warning.** Fixed by adding explicit `description=` to every `@server.tool(...)` call across all five tool modules. Independently re-verified via a fresh live `tools/list` probe: zero empty descriptions remain, HTML warning confirmed present verbatim.
8. **MAJOR — `forge_context`'s `links` output could reference items outside its own `notes`/`documents` set** (a dangling ID with no accompanying title anywhere in the response), diverging from `01_SPEC.md` §5.2's "links between the matched items" wording. Fixed by filtering to intra-matched-set edges only. Independently re-verified by reproducing the exact original failing scenario and confirming the dangling edge no longer appears.
9. **MINOR — `forge_context`'s `topic` had no length cap, unlike `forge_search`'s `query`**, despite both feeding the identical FTS phrase-prefix construction the cap exists to guard against. Fixed — `topic` now validated identically to `query`.
10. **MINOR — the `forge_context` aggregate test never exercised tags**, a coverage gap (the underlying wiring was already correct, confirmed live). Fixed — test now tags a note and asserts on it, plus asserts an untagged document's tags stay empty (guards against a `note_tags`/`document_tags` dict swap). Independently re-verified this specific mutation would in fact be caught.
11. **MINOR — `CURRENT_STATE.md`'s self-reported test counts were inaccurate.** Corrected to the actual counts (independently re-confirmed by grep: 13 and 7).

**Original findings from this milestone's first implementation pass (kept for institutional memory):**

1. **`06_API.md`'s `forge_link_items` idempotency claim didn't match `create_link`'s actual behavior**, found by re-reading the real service code rather than assuming the plan's prose was already accurate — the service raises a 409 on an exact re-link rather than returning the existing row. Translated at the MCP tool layer; worth independently re-confirming the translation is correct in both link directions, not just one.
2. **Two private service helpers were promoted to public** (`knowledge_service._tags_for` → `tags_for_items`, `projects_tools._to_mcp_out` → `project_to_mcp_out`) so `forge_context`/`forge_search` could reuse existing query/shaping logic instead of duplicating it. Worth confirming this reads as a legitimate reuse-driven promotion (both functions now have two real call sites) rather than an unjustified public-surface expansion.
3. **`forge_search` validates `project_id` even though `06_API.md`'s original draft didn't explicitly require it there** (only for `forge_context`) — a deliberate consistency choice, not a spec requirement. Worth an independent judgment on whether this narrowing (stricter failure mode) is sound or should have been left exactly as specified.
4. **AC13a's adversarial test** deliberately engineers relevance-score skew (one project's notes repeat the search term 5x, the other's once) to make the project-scoping bug deterministically reproducible rather than order-dependent/flaky. Worth checking the test actually would fail against a naive post-filter implementation (i.e., isn't accidentally passing for an unrelated reason) — the historical Milestone 2 review found real bugs the plan's own prose didn't anticipate, so the same adversarial-verification standard should apply to this milestone's own new test, not just its new code.
5. **`links` output field in `forge_context`** is deduplicated by `link_id` across the batch result (a link between two matched items is returned once, not twice — once from each item's oriented view) — the orientation of the emitted `{source_type, source_id, ...}` edge is arbitrary (whichever item's iteration order reached it first), not necessarily matching `knowledge_links`' own normalized DB column order. This is a display-shape choice, not a data-correctness issue (06_API.md's documented shape doesn't require DB-column orientation), but worth confirming no caller could reasonably infer directionality from it.

## 11. Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [reviews/AGENTIC_REVIEW_M3.md](reviews/AGENTIC_REVIEW_M3.md)
- [reviews/AGENTIC_REVIEW_M2.md](reviews/AGENTIC_REVIEW_M2.md)
- [../../history/2026-08-18-phase-11-milestone-1-checkpoint.md](../../history/2026-08-18-phase-11-milestone-1-checkpoint.md)
- [../../history/2026-08-18-phase-11-milestone-2-checkpoint.md](../../history/2026-08-18-phase-11-milestone-2-checkpoint.md)
