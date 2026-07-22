# Project Initialization Engine — Testing

> **Purpose:** Test plan for this phase — what must be covered before it can be marked done.
> **Scope:** Test strategy and enumeration. Pass/fail criteria live in 08_ACCEPTANCE.md.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Accepted.
> **Last Updated:** 2026-07-22

---

## 1. Backend tests

- **Unit** (`backend/tests/test_project_init_renderer.py`):
  - Rendering `fdk_phase` with a valid config produces exactly the 13 expected filenames, each containing the supplied `phase_number`/`phase_name`/`objective` substituted into the expected locations.
  - Rendering `ai_instructions` with a subset of `output_files` produces only those files.
  - Placeholder substitution never leaves a raw `$placeholder` token in output for any required field.
- **Unit** (`backend/tests/test_project_init_zipper.py`): `{filename: content}` round-trips through `to_zip` → a real `zipfile.ZipFile` reader recovers the same filenames and content.
- **Unit** (`backend/tests/test_project_init_service.py`):
  - `generate()` persists a `ProjectInitGeneration` row with the right `kind`/`name`/`config`.
  - `generate()` writes exactly one `ActivityLog` row.
  - `delete()` on a nonexistent id raises `NotFoundError`.
  - `list_history()` returns rows newest-first and respects `limit`.
- **Integration** (`backend/tests/test_project_init_api.py`), exercising the real router → service → test-database path (per [`../../07_CODING_STANDARDS.md §4`](../../07_CODING_STANDARDS.md)):
  - `GET /api/project-init/catalog` → 200, both kinds present with expected field lists.
  - `POST /api/project-init/generate` (fdk_phase, valid) → 201, `file_count == 13`.
  - `POST /api/project-init/generate` (ai_instructions, valid, 2 of 3 files) → 201, `file_count == 2`.
  - `POST /api/project-init/generate` (missing required field) → 422.
  - `POST /api/project-init/generate` (ai_instructions, empty `output_files`) → 422.
  - `GET /api/project-init/{id}/download` → 200, `Content-Type: application/zip`, body is a valid zip containing the expected filenames.
  - `GET /api/project-init/{bad-id}/download` → 404.
  - `GET /api/project-init/history` → 200, includes the generation created above.
  - `DELETE /api/project-init/{id}` → 204, subsequent `GET /download` → 404.
  - Unauthenticated request to any route → 401, matching every other `/api/*` route.

## 2. Frontend tests

No frontend test framework exists yet in this repo ([`../../06_TECH_STACK.md §5`](../../06_TECH_STACK.md) — not yet chosen). Per [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md), this phase substitutes thorough manual browser verification (§3) rather than shipping a shallow/no-op automated frontend suite.

## 3. Manual verification

- Kind picker: both kinds selectable via mouse and keyboard.
- Both forms: validation errors appear inline; "Generate & Download" stays disabled until valid.
- Successful generation triggers an actual browser download for both kinds; downloaded zip opens and contains the expected files.
- History list populates after generation, supports re-download and delete (with confirmation).
- Empty/loading/error states for both the form area and history list, per [02_UI.md §3](02_UI.md).
- Light and dark mode.
- Sidebar and command-palette (`⌘K`) both reach `/project-init`.
- Mobile viewport (375px) layout per [02_UI.md §4](02_UI.md).
- Recent Activity (Workbench panel or equivalent) shows the new generation with no code changes to that panel.

## 4. Regression risk

None expected — this phase adds only new, isolated files (`services/project_init/`, `api/routes/project_init.py`, `schemas/project_init.py`, `models/project_init.py`, `features/project-init/`, one new migration, one `nav-registry.ts` entry). No existing route, service, model, or component is modified. Verify specifically:

- `frontend/lib/nav-registry.ts` diff is additive only (one new array entry).
- `backend/app/api/router.py` diff is additive only (one new `include_router` call).
- Existing test suite (all other `backend/tests/*`) still passes unchanged after the new migration is added.

## 5. TODO

None.

## 6. Cross-references

- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
