# Projects — Testing

> **Purpose:** Test plan for this phase — what must be covered before it can be marked done.
> **Scope:** Test strategy and enumeration. Pass/fail criteria live in 08_ACCEPTANCE.md.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** Confirmed
> **Last Updated:** 2026-08-02

---

## 1. Backend tests

- `test_projects_service.py` — unit tests for `services/projects/service.py`: CRUD, archived filter, count accuracy, delete-unscopes-not-deletes, AI-run delegation (success, unconfigured-default, missing-credential), project-scoped run listing.
- `test_projects_api.py` — integration tests for `api/routes/projects.py`: auth-required on every route, full CRUD over HTTP, 404s, 422 validation of `default_provider`/`default_model`, 400 `project_ai_not_configured`, delete-then-verify-unscoped-via-GET.
- Extend (not replace) the existing Secrets/Notes/Documents test files with `project_id` round-trip + filter coverage.
- Migration test exercising `upgrade → downgrade → upgrade` on `0008_projects.py` against a throwaway SQLite file, asserting pre-existing seeded rows in `secrets`/`notes` survive untouched.

## 2. Frontend tests

No frontend test tooling exists in this repo yet (confirmed against `06_TECH_STACK.md` — none chosen as of this scaffold, and `07_CODING_STANDARDS.md` §4 leaves it TODO). Introducing one is out of scope for Phase 06 (would be unrelated infrastructure work, not a Projects requirement). Frontend correctness is instead verified via: TypeScript strict-mode typecheck, ESLint, a successful production build, and the manual QA pass in §3.

## 3. Manual verification

Per the mission's §13 workflow, executed against a real browser preview with throwaway data:

- Create a project, verify it appears in the list with correct counts.
- Assign a secret, a note, and a document to it (at creation and via edit); verify each shows up in the project's scoped lists and the counts update.
- Configure a default AI provider/model; verify the picker reflects `configured` status accurately.
- Run a quick prompt with a mocked/real provider; verify the result renders and appears in both the project's AI activity and Model Playground's own history.
- Edit the project's name/description/color; verify persistence.
- Delete the project with confirmation; verify the secret/note/document survive with `project_id` cleared, and the project itself is gone from the list.
- Exercise error states: unknown provider/model combination, running AI with no default set, running AI with a default set but no credential configured, navigating to a deleted project's URL directly.
- Verify the Workbench "Recent Projects" panel in both its empty and populated states.
- Verify keyboard-only operation of the delete confirmation dialog and the AI config form.
- Verify light/dark theme and a mobile viewport width on both the list and detail screens.

## 4. Regression risk

- Secrets, Notes, Documents list/detail pages and their existing filters (folder/tag/archived/search) — must continue to behave identically when no project filter is applied. Verified by re-running each feature's existing test suite unmodified (must still pass) plus the new `project_id`-specific additions.
- Model Playground's own run history and credential flows — must be completely unaffected by the new nullable `project_id` column and by project-initiated runs going through the same `create_run` path. Verified by re-running `test_model_playground_service.py`/`test_model_playground_api.py` unmodified.
- Workbench panel catalog and layout persistence — adding a new panel type must not disturb existing panel registration/order/visibility. Verified by re-running `test_workbench.py` unmodified.
- Migration chain integrity — `0008` must apply cleanly after `0007` on both a fresh install (`create_all` path) and an existing populated database (explicit `op.create_table`/`op.add_column` path), per the guarded-check pattern every migration since `0006` already uses.

## 5. TODO

None — this document is confirmed, not a template placeholder.

## 6. Cross-references

- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
