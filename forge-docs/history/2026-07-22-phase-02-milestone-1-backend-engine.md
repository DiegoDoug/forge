# Checkpoint — Project Initialization Engine — 2026-07-22

> **Trigger:** Milestone completion
> **Phase:** [Phase-02-Project-Initialization-Engine](../implementation/Phase-02-Project-Initialization-Engine/README.md)
> **Last Updated:** 2026-07-22

---

## Completed Tasks

Spec authorization (prerequisite to T1, not itself a numbered task): the phase was found entirely unauthorized (every `Phase-02-Project-Initialization-Engine/*.md` was a template placeholder, `IMPLEMENT.md` stated "Not authorized"), flagged to the user instead of guessing, scope was resolved (unified: FDK phase scaffolds + AI instruction files), and the full spec package (`README.md` through `10_RELEASE_NOTES.md`, `IMPLEMENT.md`) was drafted and self-authorized per the project owner's explicit instruction to treat spec-drafting and implementation as one continuous session.

Milestone 1 — Backend engine, per [`09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-02-Project-Initialization-Engine/09_IMPLEMENTATION_TASKS.md):

- [x] T1 — Branch `Phase02/Project-Initialization-Engine` created off `master`.
- [x] T2 — `ProjectInitGeneration` model, registered in `app/models/__init__.py`.
- [x] T3 — Additive Alembic migration `0004_project_init.py`.
- [x] T4 — Pydantic schemas (`app/schemas/project_init.py`).
- [x] T5 — Template catalog + 13 FDK-phase templates + 3 AI-instructions templates.
- [x] T6 — `string.Template`-based renderer + stdlib-`zipfile`-based zipper.
- [x] T7 — Service layer (generate / render_zip_for / list_history / delete), with `ActivityLog` integration.
- [x] T8 — Thin API router (`catalog`, `generate`, `history`, `{id}/download`, `delete`), registered in `api/router.py`.
- [x] T9 — Backend tests: 3 new test modules (renderer/zipper unit, service unit, API integration), 26 new tests, all passing; full suite (73 tests) green with zero regressions to Notes/Vault/Documents/Workbench/etc.

## Modified Files

**Spec (forge-docs):**
- `forge-docs/02_ROADMAP.md` (Phase 02 status line)
- `forge-docs/templates/project-initialization/README.md` (points at real content location)
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/README.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/01_SPEC.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/02_UI.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/03_BACKEND.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/04_DATABASE.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/05_COMPONENTS.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/06_API.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/07_TESTING.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/08_ACCEPTANCE.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/09_IMPLEMENTATION_TASKS.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/10_RELEASE_NOTES.md` (new)
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/IMPLEMENT.md`
- `forge-docs/implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md`

**Backend:**
- `backend/app/models/project_init.py` (new)
- `backend/app/models/__init__.py`
- `backend/alembic/versions/0004_project_init.py` (new)
- `backend/app/schemas/project_init.py` (new)
- `backend/app/services/project_init/__init__.py`, `catalog.py`, `renderer.py`, `zipper.py`, `service.py` (new)
- `backend/app/services/project_init/templates/fdk_phase/*.tmpl` (13 files, new)
- `backend/app/services/project_init/templates/ai_instructions/*.tmpl` (3 files, new)
- `backend/app/api/routes/project_init.py` (new)
- `backend/app/api/router.py`
- `backend/tests/test_project_init_renderer.py`, `test_project_init_service.py`, `test_project_init_api.py` (new)

## Current State

The backend half of Project Init is fully functional and tested: `POST /api/project-init/generate` validates a `fdk_phase` or `ai_instructions` request, renders the matching template set via stdlib `string.Template`, persists a history row (input config only, not the rendered output — deterministic re-render on demand, same pattern as Documents' export-on-demand), and logs one `ActivityLog` entry. `GET /api/project-init/{id}/download` re-renders and streams a zip. `GET /api/project-init/history` lists recent generations; `DELETE /api/project-init/{id}` removes a record. No frontend exists yet — the feature is not reachable from the UI. No Docker build has been run yet this session (only a local venv).

A real bug was caught and fixed during T9: the FDK phase scaffold produces **13** files, not the "12" the spec docs originally (incorrectly) stated everywhere — `10_RELEASE_NOTES.md` is part of this phase's own (and the generated) structure, one more than the count in `11_PROJECT_STRUCTURE.md §5`, which predates that file existing as a standard (Phase 01 shipped without one). Fixed consistently across all spec docs, code, and tests; flagged as a Known Issue (doc/reality drift in a root doc, intentionally not silently rewritten) rather than hidden.

A second, subtler bug was caught and fixed in the test suite itself: `test_project_init_api.py` and the pre-existing `test_workbench.py` both boot the real FastAPI app end-to-end and call `/api/setup`; `get_settings`/`get_engine`/`get_sessionmaker` are process-wide `lru_cache` singletons, so running both in one pytest process leaked state (a completed setup, a stale data-dir) across module boundaries regardless of each module's own throwaway `FORGE_DATA_DIR`. Fixed by having the new test module save/restore the env var and clear the relevant caches around its own fixture, isolating it without touching `test_workbench.py`. Full suite (73 tests) is green with this fix.

## Remaining Work

Milestone 2 — Frontend UI (T10–T12): `features/project-init/api.ts`, kind picker, both forms, file preview, generation history, `/project-init` page, `nav-registry.ts` entry.

Milestone 3 — Integration & release (T13–T14): frontend build/lint/typecheck, Docker Compose build + boot verification, manual browser verification of the golden path (per `07_TESTING.md` §3), final `CURRENT_STATE.md`/acceptance sign-off, closing checkpoint.

## Recommended Next Prompt

```
Resume Phase 02 (Project Initialization Engine) implementation. Milestone 1
(Backend engine) is complete and checkpointed — see
forge-docs/history/2026-07-22-phase-02-milestone-1-backend-engine.md and
forge-docs/implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md.
Continue with Milestone 2 (Frontend UI, T10-T12) per
09_IMPLEMENTATION_TASKS.md, then Milestone 3 (T13-T14: validation, Docker,
final checkpoint). Follow the checkpoint protocol throughout.
```

## Known Risks

- No frontend test framework exists in this repo yet — frontend verification for this phase relies on manual browser testing (per `07_TESTING.md` §2), not an automated suite. This is a pre-existing repo-wide gap, not new to this phase.
- Docker build/boot has not yet been verified this session — deferred to Milestone 3 (T13).
- The "12-file" vs. "13-file" doc/reality drift in `11_PROJECT_STRUCTURE.md §5` remains unfixed at the root-doc level (intentionally, out of this phase's ownership) — see `CURRENT_STATE.md` Known Issues.
- Retroactive project-owner sign-off on the self-authorized spec (§4 of `08_ACCEPTANCE.md`) is still an open TODO — there was no synchronous project-owner available this session, per the project owner's own explicit instruction to self-authorize and proceed.

## Cross-references

- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md](../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md)
