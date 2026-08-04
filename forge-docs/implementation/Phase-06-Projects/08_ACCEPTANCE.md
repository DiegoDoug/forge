# Projects — Acceptance Criteria

> **Purpose:** The pass/fail checklist that decides whether this phase is complete — the authoritative list referenced by 08_DEFINITION_OF_DONE.md.
> **Scope:** This phase only. Each criterion must be independently verifiable.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** Complete — all criteria verified
> **Last Updated:** 2026-08-03

---

## 1. Functional acceptance criteria

Traces to `01_SPEC.md` §3.

- [x] AC1 (FR1–FR2). Creating a Project with a name persists it; it appears in the project list with correct name/color/archived state and accurate secret/note/document counts.
- [x] AC2 (FR1). Creating a Project without a name is rejected with a validation error (name is required, 1–200 chars).
- [x] AC3 (FR3). Opening a Project's detail page shows its metadata, AI configuration, and the live lists of secrets/notes/documents scoped to it.
- [x] AC4 (FR4). Editing a Project's name/description/color persists and is reflected immediately in the list and detail views.
- [x] AC5 (FR5). Archiving a Project removes it from the default (non-archived) list view without deleting it or unscoping its children; unarchiving reverses this.
- [x] AC6 (FR6). Deleting a Project requires an explicit confirmation step. After deletion: the project is gone from the list; every secret/note/document that referenced it now has `project_id = null` and is otherwise unchanged (name, content, value all intact); no 404s or orphaned references remain in the UI.
- [x] AC7 (FR7–FR9). A Secret/Note/Document can be assigned to a project at creation and reassigned later; items with no project continue to behave identically to pre-Phase-06 behavior (verified via existing Secrets/Notes/Documents test suites still passing unmodified).
- [x] AC8 (FR8). The Secrets, Notes, and Documents list views can filter to a single project and show only that project's items; clearing the filter restores the full list.
- [x] AC9 (FR10). The Project AI configuration UI lists the same providers/models Model Playground exposes (`GET /api/model-playground/providers`), correctly reflecting which are configured.
- [x] AC10 (FR11). Setting a default provider/model that has no credential configured is allowed and persists; attempting to run a prompt against it returns a clear `provider_not_configured` error, not a crash or an opaque 500.
- [x] AC11 (FR12–FR13). With a configured default provider/model, running a prompt from the Project page returns a result (mocked adapter in tests / real provider in manual QA) and the run appears both in the Project's recent-AI-activity list and in Model Playground's own run history.
- [x] AC12 (FR14). No API key or credential value ever appears in any Project API response, and no new credential table/column is introduced (verified by code review of `models/project.py` and a grep for `encrypted_` / `api_key` in the Projects module returning nothing).
- [x] AC13 (FR15). The Workbench shows a "Recent Projects" panel; with zero projects it shows an empty state with a create action; with projects it lists the most recently updated ones and links into them.
- [x] AC14 (FR16). Projects is reachable from the sidebar nav and from the command palette (⌘K).

## 2. UX acceptance criteria

Derived from `02_UI.md` — every screen has empty/loading/error states, keyboard access confirmed.

- [x] AC15. Project list: empty state (no projects yet, with a "New Project" call to action), loading skeleton, error state with retry, populated state — all present.
- [x] AC16. Project detail: loading skeleton, error/not-found state (deleted or bad ID), populated state — all present.
- [x] AC17. Project delete confirmation dialog clearly states that secrets/notes/documents are kept and only unassigned, not deleted (avoids the exact ambiguity ADR-0014 called out).
- [x] AC18. All new interactive elements (project picker, AI config form, quick-run prompt box, delete confirmation) are reachable and operable via keyboard alone.
- [x] AC19. All new surfaces render correctly in both light and dark theme, and remain usable at mobile viewport widths.

## 3. Quality acceptance criteria

- [x] AC20. All tests in `07_TESTING.md` pass.
- [x] AC21. No architectural invariant violated (per `../../03_ARCHITECTURE.md` §2) — routers stay thin, no cross-feature frontend imports, models are the schema source of truth, migrations are explicit, ORM objects are never exposed directly.
- [x] AC22. `../../08_DEFINITION_OF_DONE.md` feature-level checklist satisfied.
- [x] AC23. Backend test suite, frontend build, lint, and typecheck all pass with zero regressions in pre-existing (non-Projects) tests.
- [x] AC24. Migration `0008_projects.py` applies cleanly to an existing populated database (upgrade), and its `downgrade()` cleanly reverses it without data loss to pre-existing tables, verified by an explicit upgrade → downgrade → upgrade test cycle.

## 4. Sign-off

Go/no-go checkpoint completed before implementation began. Final verification completed 2026-08-03: all 24 acceptance criteria verified directly (backend unit/integration tests, live migration upgrade/downgrade/upgrade cycles against both fresh-install and pre-existing-database scenarios, and a full manual browser QA pass covering CRUD, scoping, AI configuration, a real end-to-end AI run, deletion/unscoping, the Workbench panel, navigation, empty/not-found states, and dark mode/mobile rendering).

## 5. TODO

None — this document is confirmed, not a template placeholder.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [07_TESTING.md](07_TESTING.md)
- [README.md](README.md) — Definition of Complete
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
- [../../decisions/0014-project-data-model-shape.md](../../decisions/0014-project-data-model-shape.md)
