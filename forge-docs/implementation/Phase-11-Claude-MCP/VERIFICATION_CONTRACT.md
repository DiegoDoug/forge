# Phase 11 — Verification Contract

> **Status:** Active — Milestone 2 implementation complete, contract updated in place for the Milestone 2 gate per `09_IMPLEMENTATION_TASKS.md` M2-T6. Milestone 1's gate content is preserved in `../../history/2026-08-18-phase-11-milestone-1-checkpoint.md` and `reviews/AGENTIC_REVIEW_M1.md` — this file always reflects the *current* milestone's gate, not phase history.
> **Last Updated:** 2026-08-18

## 1. Phase Metadata

- **Phase name:** Phase 11 — Claude MCP / Second Brain
- **Phase objective:** Expose a scoped, semantic MCP interface over Forge's Notes/Documents/Projects/Knowledge Hub so Claude can use Forge as persistent knowledge substrate, without duplicating Forge's service layer or exposing Secrets/Settings/Crypto.
- **Dependencies:** Phase 06 (Projects), Phase 07 (Knowledge Hub) — both released & frozen, satisfied as-is. Milestone 1 (MCP Foundation) — complete, committed at `6854971`.
- **Completion definition (this milestone):** All 12 Knowledge CRUD tools (Notes/Documents/Projects) implemented per `06_API.md` §1–§2; every mechanical verifier passes; an independent Agentic Review records a PASS verdict.
- **Milestone:** Milestone 2 — Knowledge CRUD

## 2. Required Tasks

- [x] M2-T0 — `source: str = "ui"` threaded into every service function that already calls `activity.record(...)` (notes/documents create+delete, projects create+update+delete) — **not** added to `update_note`/`update_document`, which never called it (real, verified finding, not the plan's original assumption — see `01_SPEC.md` §4.5)
- [x] M2-T1 — `notes_service.get_note` added, matching `documents_service.get_document`'s shape
- [x] M2-T2 — `app/mcp/tools/notes.py` — 4 tools, corrected 3-step delete sequence
- [x] M2-T3 — `app/mcp/tools/documents.py` — 4 tools, identical delete sequence
- [x] M2-T4 — `app/mcp/tools/projects.py` — 4 tools (list/get/create/update, no delete), `secret_count` excluded from output
- [x] M2-T5 — Tool registry wiring — all 12 tools registered in `app/mcp/server.py::build_mcp_server`, scope-gated per `01_SPEC.md` §4.4
- [x] M2-T6 — This document, updated

## 3. Acceptance Criteria

From `08_ACCEPTANCE.md` §2 (Knowledge CRUD) plus the relevant carry-forward items from §5:

- [x] AC6 — `forge:write` creates/reads/updates Notes and Documents through MCP tools; resulting rows indistinguishable from REST-created ones (`test_mcp_tools_crud.py::test_note_create_get_update_delete_lifecycle`, `test_document_create_get_update_delete_lifecycle`)
- [x] AC7 — `forge:delete` + `confirm: true` deletes a Note/Document and purges its `knowledge_links` rows (`test_delete_purges_knowledge_links_no_orphans`)
- [x] AC7a — Existence check runs before any mutation is staged — a delete against a bad ID stages zero DB changes (`test_delete_nonexistent_note_stages_zero_changes`)
- [x] AC8 — `confirm` omitted or `false` fails validation, nothing deleted, and no natural-language phrasing can substitute (`test_note_create_get_update_delete_lifecycle`'s no-confirm assertion; enforced structurally — the handler only ever sees the parsed argument, never conversation text)
- [x] AC9 — `forge:write` creates/updates Projects; Notes/Documents can be project-scoped via the `project_id` field on create/update
- [x] AC10 — No MCP tool exposes `Secret` data, `secret_count`, or any crypto primitive (`test_project_create_get_update_list_no_delete_tool`'s `secret_count` assertion; `test_mcp_tools_static_checks.py`'s import-boundary check)
- [x] AC16 — Existing REST APIs unchanged — full backend regression suite green
- [x] AC17 — Existing tests remain green (no new migration this milestone; `0010` unchanged)
- [x] AC18 — Every MCP-originated **create/delete** mutation logs to `ActivityLog` with `source="mcp"`, exactly once (`test_create_note_produces_exactly_one_activity_row_with_mcp_source`). **Update is a documented, verified exception** — `notes_service.update_note`/`documents_service.update_document` have never logged for any caller; `forge_update_note`/`forge_update_document` correctly produce zero rows, matching existing behavior (`test_update_note_produces_no_activity_row_matching_existing_rest_behavior`), not a Phase 11 gap
- [x] AC19 — Browser session and MCP token remain provably independent (unchanged from Milestone 1, re-confirmed — no change to `AuthDep`/`McpBearerAuthMiddleware` this milestone)
- [x] AC20 — No MCP tool handler contains a raw ORM call — static check across `app/mcp/**` (`test_mcp_tools_static_checks.py::test_no_tool_module_calls_the_orm_directly`)

AC1–AC5, AC1a–AC4a (Milestone 1 connectivity/auth) remain satisfied, unchanged. AC11–AC15 (search/context/memory) are Milestone 3–4 scope, intentionally not listed here.

## 4. Expected File Scope

- **Expected new/modified files or directories:** `backend/app/mcp/tools/`, `backend/app/mcp/server.py`, `backend/app/services/activity.py`, `backend/app/services/notes/service.py`, `backend/app/services/documents/service.py`, `backend/app/services/projects/service.py`, `backend/tests/test_mcp_tools_crud.py`, `backend/tests/test_mcp_tools_static_checks.py`, `backend/tests/test_mcp_server.py`, `forge-docs/`
- **Explicitly out of scope:** `backend/app/services/secrets/`, `backend/app/services/crypto/`, `backend/app/services/settings/`, `backend/app/api/deps.py`, `backend/app/services/knowledge/service.py` (read-only use of `purge_links_for`/`create_link`, no modification), `backend/alembic/`, `frontend/`

## 5. Required Validation Commands

- [x] Test: cd backend && .venv/Scripts/python.exe -m pytest -q
- [x] Test fdk suite: backend/.venv/Scripts/python.exe -m pytest tools/tests -q
- [x] Build: docker build -t forge-mcp-m2-buildcheck ./backend

## 6. Architecture Constraints

- [x] `backend/app/mcp/tools/**` imports only `services/notes`, `services/documents`, `services/projects`, `services/knowledge` (link operations only), `app/mcp/auth` (`require_scope`), `app/mcp/tools/_common` — no import of `services/secrets`, `services/crypto`, `services/settings` anywhere (`test_mcp_tools_static_checks.py`).
- [x] `AuthDep`/`require_auth`/`api/deps.py` unmodified this milestone (`git diff` confirms empty).
- [x] Every tool handler reaches data exclusively through a `services/*` function — zero raw `session.get`/`session.execute` calls in `app/mcp/tools/**` (AC20, statically checked, not just spot-checked).
- [x] **Documented deviation, found during implementation**: `Context.headers` (the MCP SDK's own documented mechanism) is used to re-derive the calling token's scope inside each tool handler, rather than propagating `McpBearerAuthMiddleware`'s already-computed `McpTokenContext` through ASGI scope state. This causes one extra indexed DB lookup per tool call (cheap) in exchange for not depending on undocumented cross-layer state propagation through the MCP SDK's internal session/dispatch machinery. See `app/mcp/tools/_common.py::current_scope`'s docstring.
- [x] **Documented deviation, found during implementation**: `default_provider`/`default_model` excluded from `forge_create_project`/`forge_update_project`'s tool surface (originally specified in `06_API.md`) — see `06_API.md`'s updated per-tool rows for the reasoning (avoids pulling Model Playground's provider/model registry validation into a knowledge-substrate tool).
- [x] **Documented exception, found during implementation**: `notes_service.update_note`/`documents_service.update_document` deliberately did **not** gain `activity.record`/`source` — see §3 AC18 above. This is the correct application of "reuse the existing service layer, don't introduce new behavior," not an oversight.

## 7. Documentation Requirements

- [x] `01_SPEC.md` §4.5 corrected with the verified update-logging finding (not the plan's original, incorrect assumption)
- [x] `06_API.md` §1–§2 corrected to match the actual shipped tool input shapes (`z_index` excluded from `forge_update_note`; `default_provider`/`default_model` excluded from the two project tools; audit rows corrected for update tools)
- [x] `08_ACCEPTANCE.md` AC18 narrowed to create/delete, with the update exception stated explicitly; new open question added to §6
- [x] `CURRENT_STATE.md` — to be updated to reflect Milestone 2 completion once this gate reaches PASS
- [x] `IMPLEMENT.md` — Milestone 2's Quality Gates section to be marked satisfied once this gate reaches PASS

## 8. Regression Targets

- [x] Full existing backend test suite green (one expected, intentional update: `test_mcp_server.py`'s Milestone-1-era "zero tools" assertion updated to assert the real, current 12-tool set — not a regression, a correct update to a fact that changed on purpose)
- [x] Existing REST API behavior provably unchanged — `notes_service`/`documents_service`/`projects_service`'s existing call sites (routes, other tests) unaffected by the additive `source` parameter's default
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
- [x] Agentic Review — required. Verdict recorded at `reviews/AGENTIC_REVIEW_M2.md`.

## 10. Known findings from this milestone (for the Agentic Review's attention)

1. **The plan's own assumption about audit logging was wrong, caught by re-reading the actual baseline code.** `01_SPEC.md` §4.5 (written during planning) assumed every create/update/delete service function already called `activity.record(...)`. Verified false for `update_note`/`update_document` specifically. Corrected in the spec and reflected in the implementation (no new logging added to those two functions) and in a dedicated regression test. This is exactly the class of "verify claims against actual code, don't trust prior research" discipline the Milestone 1 Agentic Review demanded — worth independently re-confirming here, not just taking this section's word for it.
2. **Two documented tool-surface narrowings versus the original `06_API.md` draft**: `z_index` dropped from `forge_update_note`, `default_provider`/`default_model` dropped from both project tools. Both are scope reductions (less surface, not more), reasoned and documented, not silent — worth confirming the reasoning holds up, not just that it's written down.
3. **`Context.headers` re-derivation, not middleware-state propagation**: every tool handler independently re-verifies the bearer token via `tokens_service.verify()` rather than trusting a value the ASGI middleware already computed. Costs one extra DB lookup per tool call; buys not depending on undocumented SDK internals. Worth an independent judgment on whether this tradeoff is sound.
4. **`structuredContent` serialization inconsistency observed in the MCP SDK itself** (not this codebase's bug): a tool returning a `list[...]` wraps it as `{"result": [...]}` in `structuredContent`, while `content[0].text` only previews the first item; a tool returning a bare `dict` sometimes has `structuredContent` populated directly and sometimes doesn't (observed for `forge_delete_note`'s `-> dict` return specifically). Tests were written to handle both cases robustly (`test_mcp_tools_crud.py::_tool_result`). Flagged here so a future milestone building `forge_search`/`forge_context` (which return lists/aggregates) doesn't rediscover this from scratch.

## 11. Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [06_API.md](06_API.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [reviews/AGENTIC_REVIEW_M2.md](reviews/AGENTIC_REVIEW_M2.md)
- [../../history/2026-08-18-phase-11-milestone-1-checkpoint.md](../../history/2026-08-18-phase-11-milestone-1-checkpoint.md)
