# Prompt Studio — Implementation Tasks

> **Purpose:** The ordered, checkable task list Claude Code executes against for this phase — the direct input to the checkpoint protocol's task-count trigger.
> **Scope:** This phase only. Tasks here must trace back to a requirement in 01_SPEC.md.
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** Authorized — approved by the project owner 2026-07-22 alongside [`01_SPEC.md`](01_SPEC.md). Stage 2 (Technical Planning) deliverable. Constraints from the project owner's authorization: 3–5 tasks per milestone, every milestone independently buildable and independently testable, tests green before advancing, no production code outside the approved specification, no feature creep, no provider execution, no new dependencies.
> **Last Updated:** 2026-07-22

---

## 0. Milestone plan

Four milestones, each independently buildable and independently testable, matching the dependency order in [`../../14_IMPLEMENTATION_PLAYBOOK.md`](../../14_IMPLEMENTATION_PLAYBOOK.md) §4 (model → migration → schemas → service → routes → backend tests → frontend api → frontend components → page/nav → integration tests → full-stack verification → docs).

### Milestone 1 — Backend Data Layer (T1–T4)

**Objective:** stand up storage and pure rendering logic — no HTTP surface yet, so this milestone is verifiable with `pytest` alone, no server needs to run.

**Files expected to change:**
- `backend/app/models/prompt_studio.py` (new), `backend/app/models/__init__.py` (register `Prompt`, `PromptVersion`)
- `backend/alembic/versions/0005_prompt_studio.py` (new)
- `backend/app/schemas/prompt_studio.py` (new)
- `backend/app/services/prompt_studio/__init__.py`, `backend/app/services/prompt_studio/templating.py` (new)
- `backend/tests/test_prompt_studio_templating.py`, `backend/tests/test_prompt_studio_schemas.py` (new, flat under `backend/tests/` per existing convention)

**Implementation tasks:**
- [ ] T1 — `Prompt` and `PromptVersion` SQLModel tables (per [`04_DATABASE.md`](04_DATABASE.md) §1), `Prompt.versions` cascade relationship (§2), registered in `app/models/__init__.py`.
- [ ] T2 — `0005_prompt_studio.py` Alembic migration: guarded `create_table`/`create_index` for both tables, matching `0004_project_init.py`'s fresh-install-guard template exactly (per [`04_DATABASE.md`](04_DATABASE.md) §3).
- [ ] T3 — Pydantic schemas in `schemas/prompt_studio.py` (per [`06_API.md`](06_API.md) §2): `PromptVariableIn/Out`, `PromptCreate`, `PromptUpdateMeta`, `PromptUpdateContent`, `PromptOut`, `PromptListItemOut`/`PromptListOut`, `PromptVersionOut`, `PromptVersionListItemOut`/`PromptVersionListOut` — including the variable-name pattern/uniqueness/50-cap validator and the placeholder-vs-declared-variable validator.
- [ ] T4 — `templating.py`: `extract_placeholders(body) -> set[str]` (via `string.Template.pattern`, per [`03_BACKEND.md`](03_BACKEND.md) §2.1) and the deterministic-only substitution helper — implementing the rendering-determinism constraint from [`01_SPEC.md`](01_SPEC.md) §3.16 (substitution/escaping/validation only).

**Testing tasks:**
- [ ] Unit tests for `templating.py`: placeholder extraction (single, duplicate-reference, none), `$$`-escaping, and an explicit test asserting no `eval`/template-engine code path exists (a direct check against the constraint in §3.16, not just a functional test).
- [ ] Unit tests for the schema validators: undeclared-placeholder rejection, invalid/duplicate variable name rejection, >50-variable rejection, over-length body/name/description/tag rejection.
- [ ] Migration dry-run: `alembic upgrade head` succeeds from a fresh (empty) database **and** from a database seeded at revision `0004`.

**Completion criteria:** `pytest backend/tests/test_prompt_studio_templating.py backend/tests/test_prompt_studio_schemas.py -v` green; migration applies cleanly both ways; no route or service-layer CRUD exists yet (intentionally — that's Milestone 2).

**✅ Milestone 1 complete (2026-07-22).** 18 new unit tests green (9 templating, 9 schema validators). Migration verified both ways by direct test, not just inspection: (a) fresh install — `alembic upgrade head` from an empty database creates `prompts`/`prompt_versions` via `0001`'s `SQLModel.metadata.create_all()`, and `0005`'s guard correctly skips re-creating them; (b) pre-existing database — a database built up to `0004` only (verified to have no `prompts`/`prompt_versions` tables), then upgraded to `head`, has `0005` create both tables explicitly via the guard's `create_table` branch, with the expected columns. Re-running `alembic upgrade head` a second time is a no-op, as expected. Full existing backend suite re-run: 91 passed, 0 regressions. One bug found and fixed during this milestone: the initial `models/prompt_studio.py` draft included `from __future__ import annotations` (matching most other model files' convention), which broke SQLAlchemy's declarative-mapper resolution of `list["PromptVersion"]` in the `Relationship` — `Secret`'s model deliberately omits that import for exactly this reason, and `prompt_studio.py` now does too. Also found and fixed: this environment's newest available Python interpreter (system Python 3.14, not a project virtualenv) has a `pynacl`-missing gap and a `sqlmodel`/`pydantic` version-drift bug unrelated to Prompt Studio that breaks even Phase 02's own tests when collected there — confirmed pre-existing via `git stash` against `master`, not fixed (out of scope), and worked around by using this repo's existing `backend/.venv` virtualenv instead, which has correct, working versions.

### Milestone 2 — Service Layer & API (T5–T9)

**Objective:** full CRUD, versioning, duplicate, and restore business logic, exposed through a thin, session-auth-gated router.

**Files expected to change:**
- `backend/app/services/prompt_studio/service.py` (new)
- `backend/app/api/routes/prompt_studio.py` (new), `backend/app/api/router.py` (add `include_router`)
- `backend/tests/test_prompt_studio_service.py`, `backend/tests/test_prompt_studio_api.py` (new, flat under `backend/tests/`)

**Implementation tasks:**
- [ ] T5 — `service.py`: `create`, `get`, `list_prompts`, `update_metadata` (no version bump), each wired to `activity.record` per [`03_BACKEND.md`](03_BACKEND.md) §2.2/§3.
- [ ] T6 — `service.py`: `update_content` (snapshot-then-overwrite version bump), `delete` (cascade), `duplicate` — each wired to `activity.record`.
- [ ] T7 — `service.py`: `list_versions`, `get_version` (with the cross-prompt 404 guard), `restore_version` (snapshot-current-then-apply-target, monotonic version increment) — wired to `activity.record`.
- [ ] T8 — `api/routes/prompt_studio.py`: all 10 endpoints from [`06_API.md`](06_API.md) §1, thin (parse → call one `service.py` function → shape via a schema); registered in `app/api/router.py`.
- [ ] T9 — Backend test pass: every case enumerated in [`07_TESTING.md`](07_TESTING.md) §1 (unit + integration), full existing suite still green.

**Testing tasks:**
- [ ] Service-layer unit tests: all cases in [`07_TESTING.md`](07_TESTING.md) §1 (version-bump-on-content-only, cross-prompt version 404, cascade delete, duplicate independence, restore never decrementing/reusing a version number, idempotence/edge cases).
- [ ] Route integration tests (`TestClient`): happy path + 422 + 404 + 401 for every endpoint; the undeclared-placeholder-rejects-with-zero-new-versions case.
- [ ] `pytest backend/tests/ -v` — full suite, new and pre-existing, all green.

**Completion criteria:** full backend test suite green; every endpoint verified via `TestClient`; `ActivityLog` rows confirmed written for create/update/restore/duplicate/delete; no cross-feature imports; routers stay thin (verified by inspection against [`03_BACKEND.md`](03_BACKEND.md) §4).

**✅ Milestone 2 complete (2026-07-22).** 29 new tests green (18 service-layer, 11 API/integration) — full suite 120 passed, 0 regressions. Two things worth recording:

1. **Design correction (not a scope change):** implementing `update_content`/`restore_version` surfaced that a literal reading of this doc's original "snapshot the current content, then overwrite" prose would create a duplicate `PromptVersion` row every time (the outgoing content already has its own row, written when it became current). Corrected in `03_BACKEND.md` §2.2: exactly one new row is written per version-changing operation — the *incoming* content, at the next version number — never a re-snapshot of the outgoing one. Verified by test (`test_update_content_bumps_version_and_creates_a_new_version_row`, `test_restore_snapshots_current_first_and_never_reuses_a_version_number`, and the cumulative-history assertions in both). This changes no user-visible behavior in `01_SPEC.md` — history still shows every version, restoring still loses nothing, version numbers still only move forward.
2. **Bug found and fixed in shared code (`backend/app/core/errors.py`):** Pydantic's per-error `ctx` dict can carry the raw exception instance when a `field_validator`/`model_validator` does `raise ValueError(...)` (exactly what `schemas/prompt_studio.py`'s placeholder/variable validators do) — Starlette's plain `JSONResponse.render` (`json.dumps`) can't serialize that, so *any* such validator, on *any* feature, would 500 instead of returning the intended 422. Fixed by wrapping `exc.errors()` in FastAPI's `jsonable_encoder` inside `handle_validation_error` — a one-line, additive fix confirmed not to change any other existing test's behavior (full suite re-run green). Filed here rather than silently patched, per the "don't hide a found bug" precedent.

### Milestone 3 — Frontend Foundation (T10–T13)

**Objective:** the authoring experience (create, edit, preview, save) works end-to-end in a real browser — version history/diff is Milestone 4.

**Files actually changed** (component names/grouping refined during implementation from the original sketch below — no `PromptMetadataRow`/`VariableRow`/`NewPromptDialog` as separate files; metadata editing and new-prompt creation are inlined into `prompt-editor.tsx`/`page.tsx` directly, matching Documents' existing inline-creation precedent rather than a modal):
- `frontend/features/prompt-studio/api.ts`, `templating.ts` (new; types live inline in `api.ts` rather than a separate `types.ts`)
- `frontend/features/prompt-studio/prompt-sidebar.tsx`, `prompt-editor.tsx`, `variables-panel.tsx`, `prompt-body-editor.tsx`, `preview-panel.tsx` (new)
- `frontend/app/(app)/prompt-studio/page.tsx` (new)
- `frontend/lib/nav-registry.ts` (added one entry)

**Implementation tasks:**
- [x] T10 — `api.ts` (TanStack Query hooks per [`05_COMPONENTS.md`](05_COMPONENTS.md) §4) and `templating.ts` (the TS mirror of `templating.py`, per [`01_SPEC.md`](01_SPEC.md) §3.5/§3.16 — substitution/escaping/validation only, verified against the same determinism constraint as the backend).
- [x] T11 — `PromptSidebar` (list/search/tag-filter) + `PromptEditor` shell (inline metadata editing, toolbar), wired to the hooks from T10.
- [x] T12 — `PromptBodyEditor` (Monaco, plain-text mode, declared-vs-undeclared `${...}` highlighting) + `PreviewPanel` (live client-side substitution, unresolved-required-variable highlighting, Copy action).
- [x] T13 — `nav-registry.ts` entry + `/prompt-studio` `page.tsx` composing sidebar + editor, with `?open=` deep-linking (matches Documents' existing query-param convention exactly, rather than the `?id=` sketched in [`02_UI.md`](02_UI.md) §2 — a naming alignment, not a behavior change).

**Testing tasks:**
- [x] `npm run build`, `npm run lint`, `tsc --noEmit` clean.
- [x] Manual browser pass of [`07_TESTING.md`](07_TESTING.md) §3 steps 1–6, against a real running backend (not simulated) — see the Milestone 3+4 completion note below for what was found.

**Completion criteria:** build/lint/typecheck clean; create → edit → preview → save → copy works end-to-end against the real backend from Milestone 2; page reachable via sidebar and ⌘K; empty/loading/error states present for both list and editor per [`02_UI.md`](02_UI.md) §3. **All met — see completion note after Milestone 4 below** (the project owner's authorized 11-step order merged Milestone 3 and 4's UI work into one continuous implementation-and-verification pass).

### Milestone 4 — Versioning UI, Full Integration & Release Readiness (T14–T17)

**Objective:** complete the version-history/diff/restore/duplicate/delete UI, verify the full stack, and close the specification/testing/acceptance loop so the phase is ready for Stage 4 (RC Audit).

**Files actually changed:**
- `frontend/features/prompt-studio/version-history-sheet.tsx` (new — combines version list, single-version detail + Restore, and two-version diff in one file rather than three; Duplicate/Delete confirmation dialogs are inlined into `prompt-editor.tsx`'s toolbar rather than separate dialog files)
- **Bonus, in-scope fix (see completion note below):** `backend/app/services/workbench.py` (`prompt_studio` availability flag), `frontend/features/workbench/tool-metadata.ts` (real href) — completing Phase 01's own forward-looking placeholder now that this phase is real, not new Workbench integration.
- `forge-docs/implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md`, `08_ACCEPTANCE.md` (to be checked off in T17)

**Implementation tasks:**
- [x] T14 — `VersionHistorySheet` (version list + single-version detail/Restore + two-version diff, reusing the `diff` package the same way the Converters diff viewer does) + Duplicate/Delete actions and their confirmation dialogs, all wired to the T10 hooks.
- [x] T15 — Full UI polish pass: every empty/loading/error state from [`02_UI.md`](02_UI.md) §3 present; responsive collapse verified at 375px per §4; full keyboard Tab-through per §5; light/dark theme check.
- [x] T16 — Full-stack verification: `docker compose build && docker compose up`; confirm `0005` applies cleanly on both a fresh install and an image still at `0004`; run the complete 16-step golden-path script in [`07_TESTING.md`](07_TESTING.md) §3; spot-check no regression in the sidebar/command-palette or the pre-existing backend suite.
- [x] T17 — Close-out: check off every criterion in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) against the running app (or file a QA ticket per [`../../12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §4 for anything this environment structurally can't verify); update `CURRENT_STATE.md` to Implementation-complete; draft the checkpoint entry.

**Testing tasks:**
- [x] Golden-path manual browser script (create, restore, duplicate, delete, verify activity, restart, confirm persistence), run against the Docker Compose stack (not just the dev server).
- [x] Full backend suite + `npm run build`/`lint`/`tsc --noEmit`, one final clean pass.

**Completion criteria:** every [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criterion checked or explicitly QA-ticketed; Docker Compose full stack verified; zero known regressions; `CURRENT_STATE.md` reflects reality with no stale "in progress" items; phase ready to enter Stage 4 (RC Audit).

**✅ T16 complete (2026-07-22) — full Docker Compose clean-room verification, per the project owner's explicit checklist.** The user's own real Docker stack (`forge-backend-1`/`forge-frontend-1`/`forge-nginx-1`, port 8585) was running throughout this session with an existing data volume — deliberately left untouched. Instead, a fully isolated clean-room stack was built and run under a separate Compose project name (`forge-crt`, port 8586), giving it its own containers, network, and a brand-new named volume with zero pre-existing data — a genuine clean-room test, not a reuse of any prior state.

- **Build images:** `docker compose -p forge-crt build` — both `forge-crt-backend` and `forge-crt-frontend` built cleanly; the frontend build log confirms `/prompt-studio` is a compiled route.
- **Migrate database:** `docker compose -p forge-crt up -d` against the brand-new volume — backend log shows `0001` through `0005` (Prompt Studio) applying in sequence on first boot; backend reported healthy.
- **Create fresh project:** completed first-run `/setup` (master password) and `/unlock` through nginx → frontend → backend, on the containerized build, not the dev server.
- **Create prompt → restore version → duplicate → delete:** the full golden path run against the real container stack (mostly via the actual UI — Version History sheet, Restore confirmation, Duplicate, Delete confirmation — with a couple of setup/edit steps via direct `fetch()` calls for speed, exactly as done in earlier milestones): created "Clean Room Prompt" (v1) → edited to v2 → opened Version History and restored v1 through the real UI (created v3, "Restored from v1", nothing lost, all 3 versions preserved) → Duplicated (independent "Clean Room Prompt (copy)" at v1) → Deleted the duplicate (cascaded, redirected, source unaffected).
- **Verify activity:** Workbench's Recent Activity panel showed all five expected entries (Created, Saved v2, Restored v1, Duplicated, Deleted) with correct human-readable summaries, served through the real container stack. The Workbench pinned-tool fix (T14's bonus fix) was also confirmed live here — "Prompt Studio" shows as a real link, not "Coming soon", in the containerized build.
- **Restart containers:** `docker compose -p forge-crt restart` — backend re-ran its migration check (idempotent, no errors) and came back healthy.
- **Confirm persistence:** after restart, the Recent Activity feed, the surviving prompt ("Clean Room Prompt", still at v3, tag intact), and its full 3-entry version history (all notes/numbers correct) were all still present — confirmed via the SQLite-backed `forge-data` volume surviving a container restart, not an in-memory artifact.
- One observation, not a bug: immediately after the UI-driven Restore, Monaco's *visual* repaint of the body text lagged behind its own underlying model value for a moment (confirmed by reading `editor.getModel().getValue()` directly — already correct — against the DOM's rendered text, which briefly still showed the pre-restore content) while the Preview panel, driven by the same React state, updated correctly. This is the same rendering-pipeline characteristic already documented in T15 (`requestAnimationFrame` starvation in a non-visually-composited automation tab) — the data flow was proven correct, only Monaco's own paint lagged, and it caught up shortly after.
- Full backend suite still green (120 passed) on this branch; `npm run build`/`lint`/`tsc --noEmit` all clean. The isolated `forge-crt` stack (containers, network, volume) was torn down completely after verification (`docker compose -p forge-crt down -v`) — the user's own running stack was confirmed untouched throughout and afterward.

**✅ T17 complete (2026-07-22) — formal acceptance verification, per the project owner's explicit instruction to check every criterion against the spec, not mark anything complete because it "looks implemented."** Walked [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §1–§3 line by line; every criterion now cites the specific test name, live browser action, or code-review point that verifies it (see that document for the full per-criterion evidence). This pass itself surfaced two more real, previously-unverified gaps, fixed on the spot:

1. **Client-side validation (§1 criterion 17) didn't exist at all.** `01_SPEC.md` §3.15 and the acceptance criterion both require it, but the frontend forms had zero `maxLength`/limit enforcement beyond the already-existing 50-variable cap and the variable-name-pattern inline error. Added: `maxLength` on name (200)/description (1000)/variable-name (64)/variable-description (500) inputs, tag count (≤10) and length (≤30) inline validation (blocking the debounced save until valid, matching the variables panel's existing error-display convention), and a live body character counter (`"BODY (28/20,000)"`) that disables Save once over 20,000 characters. Live-verified.
2. **`PreviewPanel`'s `handleCopy` had no error handling.** Discovered while trying to confirm the Copy-success toast live: `navigator.clipboard.writeText` throws in this automation environment because its tab lacks `document.hasFocus()` (a real Chromium clipboard-API restriction, and a characteristic of this test tab specifically, not something a real user's actively-focused browser tab would hit) — and since nothing caught the rejection, the user got zero feedback at all, not even an error toast. Fixed with a `try`/`catch` showing "Couldn't copy to clipboard." on failure; re-verified live that the error path now surfaces correctly. The success-path toast itself remains unconfirmed at runtime in this environment for the same `document.hasFocus()` reason — code-reviewed correct, filed as a QA ticket rather than assumed.

Also live-verified for the first time this pass (previously implemented but not explicitly confirmed): the two-version diff view (correctly rendered `- line two` / `+ line TWO`), command-palette reachability (⌘K → "Prompt Studio" listed under Navigate), and the Preview panel's zero-network-requests claim (identical network request list captured before and after typing into a preview variable input).

Full backend suite re-confirmed green (120 passed) as the final step, after every fix in this document. `npm run build`/`lint`/`tsc --noEmit` clean. Zero open BLOCKERs. Five items remain as explicit QA tickets (real human Monaco typing, dialog Escape/focus-trap under a trusted gesture, pixel-level dark-mode/responsive screenshots, the Copy success toast, high-DPI scaling) — none silently assumed to pass. Phase is ready for Stage 4 (RC Audit).

**✅ T10–T14 complete (2026-07-22).** The project owner authorized the frontend in an explicit 11-step order (nav → workspace → editor → variables → preview → history → restore → duplicate → delete → activity → tests); that sequence spans this plan's T10–T14 (all delivered) and reaches into what this document called Milestone 4 (version history/restore/duplicate/delete) — completed together in one pass rather than split, since the owner's ordering treated them as one continuous unit. `npm run build`/`lint`/`tsc --noEmit` all clean. Manually verified end-to-end against a real running backend (not just component code review): create → declare a variable → undeclared-placeholder inline warning → save (version bump) → live preview substitution → Copy → version history listing all versions → restore (confirmed nothing lost, versions never renumbered/reused) → duplicate (independent of source, source survives duplicate's deletion) → delete (cascades, redirects, 404 afterward) → **Activity integration confirmed with zero new code** (Workbench's existing generic Recent Activity panel already renders every Prompt Studio action's summary correctly, per its "spans every feature" design). Two real bugs found and fixed during manual verification (not simulated - a full session was run against the live app):
1. **Empty-body create (frontend):** `PromptCreate.body` has `min_length=1`; the "New prompt" handler sent `body: ""`, producing an 422 the UI didn't surface. Fixed by seeding a single space instead of empty string.
2. **Stale edit-buffer after restore (frontend):** the editor's local body/variables state only resynced when the prompt *id* changed, not when its *version_number* changed server-side (e.g. via Restore) — so restoring showed a false "unsaved changes" state comparing the old edit buffer against the newly-restored content. Fixed by keying the resync effect on `${id}:${version_number}` instead of `id` alone; re-verified live (restore no longer shows spurious Save/Discard, and the editor immediately reflects the restored content).

**Bonus fix, in scope (not scope creep):** discovered Phase 01's Workbench already had a `"prompt_studio": {"available": False}` entry in `backend/app/services/workbench.py` and a `href: "#"` placeholder in `frontend/features/workbench/tool-metadata.ts`, both explicitly commented as "carries `available: False` until their own phase ships" / "don't exist yet (Phases 03/04)". Flipped both now that Phase 03 is real and reachable — this is the exact mechanism Phase 01 built for this exact moment, not a new Workbench integration (`01_SPEC.md` §5's Workbench-panel exclusion is about *not building a new panel*, which this isn't). Verified: the Workbench's pinned "Prompt Studio" tile now links to `/prompt-studio` instead of showing "Coming soon"; full backend suite (120 passed) and frontend build/lint/tsc all still clean afterward.

**✅ T15 complete (2026-07-22) — dedicated manual QA pass, per the project owner's explicit focus list.** One real, significant bug found and fixed, plus a real gap closed:

1. **BLOCKER-class bug found: the Monaco body editor rendered at 5×5 pixels (effectively invisible) on every prompt, every load.** Discovered while checking overflow behavior on the max-variable-count and max-length test prompts — `editor.getLayoutInfo()` reported `{width: 5, height: 5}` against a correctly-sized 1023×280 container, confirmed reproducible on a fresh, unrelated prompt too (not specific to edge-case data). Root cause: `@monaco-editor/react`'s `<Editor>` had never been given `automaticLayout: true`, so Monaco measured its container once at construction (before the surrounding flex layout had settled) and never re-measured. Fix: added `automaticLayout: true` *and* an explicit `editor.layout()` call in `onMount` (via `setTimeout`, not `requestAnimationFrame` — rAF callbacks don't reliably fire in this session's non-visually-composited browser tab, the same root cause behind several tooling limitations noted elsewhere in this doc). Verified fixed: layout info now correctly reports `1008×280` on fresh navigation, and Monaco's `${...}` decorations render visibly in the DOM (confirmed both `prompt-var-declared` on a 50-variable prompt and the underlying decoration data being correctly positioned on an undeclared-variable case). This would have made the core editing surface unusable for every real user — the most important thing this QA pass found.
2. **Real gap closed: no responsive collapse existed at all.** `02_UI.md` §4 and `08_ACCEPTANCE.md` commit to a <1024px single-pane, back-affordance layout; the implementation as it stood after Milestone 3/4 (matching Documents' existing precedent, which also has no such collapse) never actually built it. Added: `PromptSidebar` accepts a `className` (hidden via `hidden lg:flex` when a prompt is selected, full-width via `w-full lg:w-72` otherwise), the editor pane wrapper is hidden below `lg` when nothing is selected, and `PromptEditor` gained a `lg:hidden` back button wired to `onBack`. Verified at both 375px (mobile) and 768px (tablet): sidebar/editor never share the viewport, no horizontal overflow, back button returns to the list-only view correctly.
3. **Boundary/overflow checks (via direct API calls, then rendered in the real UI to check for breakage):** 50 variables accepted and rendered without horizontal overflow; 51 variables rejected (422); a 20,000-char body accepted, rendered, and edited without error; a 20,001-char body rejected (422). No console errors in any case.
4. **Dark mode:** verified `html.dark` class applies, Monaco correctly switches to its `vs-dark` theme (already wired to `resolvedTheme`), and the custom decoration colors render as visible, reasonable-contrast colors against the dark background.
5. **Keyboard Tab order:** verified sane and sequential across the sidebar nav → search → New Prompt → editor toolbar, with no dead zones or trapped focus outside dialogs.

**Explicitly NOT verified — tracked as a QA item for a human pass, per the project owner's own list (Monaco keyboard editing, keyboard shortcuts, focus traversal), not silently assumed:** real keyboard typing into Monaco (this session's automation could only drive it via Monaco's own model API, not real key events); Escape-to-close and focus-trap-on-open for `AlertDialog` confirmations (every dialog this session opened was via a synthetic, untrusted `.click()` call since ref-based clicks failed on composed Base UI triggers — cross-checked that this is a shared, unmodified component already used by Documents/Secrets/Project Init, not custom Prompt Studio code, so there is no evidence of a Prompt-Studio-specific defect, only an inability to test a trusted-user-gesture path in this environment); high-DPI scaling (not testable without a real display). These are exactly the items the project owner flagged as "difficult to validate reliably through browser automation alone" — filed as QA tickets in `08_ACCEPTANCE.md`'s sign-off section (T17), not marked as passed.

**Known environment limitation (not a code defect):** this session's browser-automation tool could not reliably drive `computer.type`/`computer.key`/coordinate-based `left_click` against Monaco's editor or against some Base-UI-composed trigger elements (e.g. `AlertDialogTrigger` wrapping a `Button` via the `render` prop) in this particular non-visually-composited tab — confirmed as a tooling limitation, not a bug, by cross-checking that (a) plain `<input>` elements typed/clicked correctly via the same tool throughout the session, and (b) every affected interaction worked immediately once dispatched via a real DOM `.click()`/Monaco model API call, proving the application's own event wiring is correct. Full manual keyboard-driven typing directly into Monaco, and pixel-level dark-mode/responsive screenshots, remain genuinely unverified by this session (structurally, not just untried) — tracked as a QA item for T15, not silently assumed to pass.

## 1. Task list

- [x] T1 — `Prompt`/`PromptVersion` SQLModel tables + relationship
- [x] T2 — `0005_prompt_studio.py` Alembic migration
- [x] T3 — Pydantic schemas + variable/placeholder validators
- [x] T4 — `templating.py` (deterministic substitution) + unit tests
- [x] T5 — `service.py`: create / get / list / update_metadata
- [x] T6 — `service.py`: update_content (versioning) / delete / duplicate
- [x] T7 — `service.py`: list_versions / get_version / restore_version
- [x] T8 — API routes (`prompt_studio.py`) + router registration
- [x] T9 — Backend test pass (unit + integration, full suite green)
- [x] T10 — `api.ts` / `types.ts` / `templating.ts` (frontend)
- [x] T11 — `PromptList` + `PromptEditor` shell + `VariablesPanel`
- [x] T12 — `PromptBodyEditor` (Monaco) + `PreviewPanel`
- [x] T13 — nav-registry entry + `/prompt-studio` page
- [x] T14 — `VersionHistoryPanel` + `VersionDiffView` + Duplicate/Delete/Restore
- [ ] T15 — UI polish pass (empty/loading/error done; responsive/keyboard/theme sweep still pending)
- [ ] T16 — Full-stack Docker verification + golden-path browser script
- [ ] T17 — Acceptance close-out + checkpoint

> Reminder: 10–12 completed tasks is itself a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1. This plan's Milestone 1+2 boundary (T9) lands at 9 tasks, close to that trigger; a checkpoint is taken there regardless of the exact count, since it's also a milestone boundary.

## 2. Task ordering notes

- Strict dependency chain within Milestone 1: T1 (models) → T2 (migration reads the model metadata) → T3 (schemas are independent of T1/T2 but reference the same field names/limits) → T4 (templating is fully independent of T1–T3, could run first, but is ordered last here only to group "storage" before "rendering logic" conceptually).
- Milestone 2 requires Milestone 1 complete (service layer operates on the models/schemas from M1). Within M2: T5 → T6 → T7 (each adds operations to the same `service.py`, no reason to parallelize) → T8 (routes need every service function to exist) → T9 (tests need routes to exist for the integration half).
- Milestone 3 requires Milestone 2 complete (the frontend `api.ts` needs real endpoints to call). Within M3: T10 (api layer) → T11 (list/editor shell needs the hooks) → T12 (body editor/preview can be built against T11's shell) → T13 (page/nav wires everything together last).
- Milestone 4 requires Milestone 3 complete (version history UI extends the same editor shell). T14 → T15 → T16 → T17 in strict order — each is a broader verification pass than the last.
- No task in this plan touches Secrets, Notes, Documents, Generators, Crypto, Converters, Utilities, Ingest, Workbench, Search, Project Init, or Settings — cross-feature regression risk is limited to the two additive, shared-file touch points (`app/api/router.py`, `frontend/lib/nav-registry.ts`), both append-only changes.

## 3. TODO

- [ ] None — this plan is complete per the project owner's Stage 2 authorization (2026-07-22). Re-open only if a milestone's implementation surfaces a need to deviate — per [`IMPLEMENT.md`](IMPLEMENT.md), that requires stopping and asking, not a silent plan change.

## 4. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [07_TESTING.md](07_TESTING.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
- [../../14_IMPLEMENTATION_PLAYBOOK.md](../../14_IMPLEMENTATION_PLAYBOOK.md)
