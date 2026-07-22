# Prompt Studio — Acceptance Criteria

> **Purpose:** The pass/fail checklist that decides whether this phase is complete — the authoritative list referenced by 08_DEFINITION_OF_DONE.md.
> **Scope:** This phase only. Each criterion must be independently verifiable.
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** Accepted — approved alongside [`01_SPEC.md`](01_SPEC.md) 2026-07-22. **T17 formal acceptance pass complete (2026-07-22)** — every criterion below is checked against direct evidence gathered this session (unit/integration tests, live browser verification against the dev server and a Docker Compose clean-room stack, or explicit code review), not assumed from the implementation existing. Items this environment structurally cannot verify are marked QA (not silently checked).
> **Last Updated:** 2026-07-22

---

## 1. Functional acceptance criteria

Each item traces to its numbered requirement in [`01_SPEC.md`](01_SPEC.md) §3.

- [x] A prompt can be created with name, description, tags, body, and zero or more variables; it starts at version 1. (§3.1–3.3) — verified live repeatedly (dev server and Docker); `test_create_starts_at_version_1_with_one_version_row`.
- [x] A variable's `name` is validated against the identifier pattern and uniqueness-within-prompt; an invalid or duplicate name is rejected with a 422 before any row is written. (§3.3) — `test_create_rejects_duplicate_variable_names`, `test_create_rejects_invalid_variable_name_pattern`; live-verified 51-variable and invalid-pattern rejections.
- [x] Saving a body that references a `${name}` not present in the declared variables is rejected (422); saving a body whose every `${name}` is declared succeeds. (§3.4) — `test_create_undeclared_placeholder_returns_422`, `test_update_content_with_undeclared_placeholder_creates_no_new_version`; live-verified via UI inline warning.
- [x] A literal `$` written as `$$` in the body is not treated as a placeholder and does not trigger the undeclared-variable rejection. (§3.4) — `test_create_accepts_escaped_dollar_without_requiring_a_variable`; `templating.ts`/`templating.py` unit tests for `$$` escaping.
- [x] The Preview panel renders the fully-substituted body from live-entered/default variable values, with zero network requests observed (confirmed via the browser's network panel during manual verification). (§3.5) — live-verified: typed into a preview variable input, compared the exact network request list before/after — identical, zero new requests; `preview-panel.tsx` has no `fetch`/API import at all (structurally incapable of a network call).
- [x] A required variable left blank in Preview renders its token as visibly unresolved, not as empty text. (§3.5) — live-verified ("Unresolved: audience", token rendered as `${audience}` not blank).
- [x] The Copy action places the rendered output on the clipboard with visible confirmation. (§3.6) — the error path is live-verified (a real gap was found and fixed here: `handleCopy` had no error handling at all; a clipboard-write failure — which reproduces in this automation environment because `document.hasFocus()` is false, a characteristic of the test tab, not of a real user's active browser tab — previously failed completely silently; now shows "Couldn't copy to clipboard."). The success-path toast text could not be triggered in this environment for the same `document.hasFocus()` reason; code-reviewed correct, not runtime-confirmed. **QA ticket**, not silently passed.
- [x] Saving a change to `body` or `variables` creates exactly one new immutable version and increments the version counter; saving a change to only `name`/`description`/`tags` does neither. (§3.7) — `test_update_content_bumps_version_and_creates_a_new_version_row`, `test_update_metadata_does_not_bump_version_or_create_a_version_row`; live-verified repeatedly.
- [x] Version History lists every version, newest first, each with its number, timestamp, and an auto-generated note. (§3.8) — live-verified multiple times (dev server and Docker), correct ordering/notes/timestamps.
- [x] Selecting two versions renders a diff of their bodies using the existing diff-viewer component. (§3.8) — live-verified this session: two-version diff correctly rendered `- line two` / `+ line TWO` with the unchanged line shown plain.
- [x] Restoring version N requires confirmation, snapshots the prompt's pre-restore content as a new version, then applies N's content as the new current content, incrementing the version counter — no existing version is lost or overwritten. (§3.9) — `test_restore_snapshots_current_first_and_never_reuses_a_version_number`, `test_restoring_again_to_a_different_version_preserves_every_prior_version`; live-verified repeatedly including in Docker.
- [x] Duplicate creates an independent new prompt (own id, own version-1 history) copying the source's current body/variables/tags, named with a `(copy)` suffix; subsequent changes to either prompt do not affect the other. (§3.10) — `test_duplicate_creates_independent_prompt_with_its_own_version_1`, `test_duplicate_is_unaffected_by_deleting_the_source`; live-verified (source survives duplicate's deletion) in both dev server and Docker sessions.
- [x] Search (name/description) and tag filter narrow the visible list client-side; an empty-result-from-filter state is visibly distinct from the true zero-prompts state. (§3.11) — live-verified ("No prompts match — clear filters" vs. "No prompts yet").
- [x] Deleting a prompt requires confirmation and cascades to delete all of its versions; the prompt and its versions are unreachable afterward (404). (§3.12) — `test_delete_cascades_to_versions`; live-verified repeatedly, including confirming a 404 via direct API check after deletion.
- [x] Create, content-update, restore, duplicate, and delete each produce exactly one Recent Activity entry with a human-readable summary, visible in the existing Activity view without any change to that view's own code. (§3.13) — `test_create_writes_exactly_one_activity_log_row`, `test_delete_activity_log_captures_name_before_row_is_gone`; live-verified in Docker (exactly 5 entries for 5 actions, 1:1); confirmed `recent-activity-panel.tsx` was never touched.
- [x] Prompt Studio is reachable from both the sidebar and the command palette. (§3.14) — live-verified: sidebar link present and navigable; command palette (⌘K) opened and "Prompt Studio" confirmed listed under Navigate.
- [x] Every validated field enforces the same limit client-side (inline error, no round trip needed to discover it) and server-side (422 if bypassed). (§3.15) — **a real gap was found and fixed during this T17 pass**: client-side limits (name/description `maxLength`, tag count/length inline error, variable name/description `maxLength`, a live body character counter with Save disabled over 20,000 chars, the 50-variable cap already disabling "Add variable") did not all exist before this check. Now implemented and live-verified (character counter renders correctly, e.g. "BODY (28/20,000)"); server-side 422s independently confirmed for all the same boundaries.
- [x] Rendering (both the backend save-time validation and the frontend preview) performs only substitution, escaping, and validation — a code review of `templating.py` and `templating.ts` confirms neither calls `eval`, a templating engine, or any mechanism supporting conditionals/loops/function calls/filters/includes/imports. (§3.16, project-owner requirement added 2026-07-22) — confirmed by code review, and mechanically by `test_templating_module_has_no_expression_language` (parses the module's AST and asserts only stdlib `string` is imported and no `eval`/`exec`/`compile` call exists anywhere in it).

## 2. UX acceptance criteria

Derived from [`02_UI.md`](02_UI.md):

- [x] List pane: empty, loading, error, populated, and zero-filter-result states are all implemented and visually distinct (§3 of `02_UI.md`) — live-verified: "No prompts yet", populated list, "No prompts match — clear filters" all confirmed distinct.
- [x] Editor pane: empty (no selection), loading, error, and populated states are all implemented (§3 of `02_UI.md`) — live-verified (empty-selection state with "New prompt" CTA, populated editor).
- [x] Version History panel: loading, error, and populated (list / single-version detail / two-version diff) states are all implemented (§3 of `02_UI.md`) — live-verified: list, single-version detail with Restore, and two-version diff all confirmed rendering correctly this session.
- [x] At ≥1024px, list and editor render side by side; below 1024px, the layout collapses to single-pane stack navigation with a working back affordance (§4 of `02_UI.md`) — **T15 found this did not exist at all** (matching Documents' own precedent, which also lacks it) despite this criterion already being accepted spec; implemented and live-verified at 375px and 768px: panes never share the viewport, zero horizontal overflow, back button returns to the list correctly.
- [ ] Every interactive element in the editor, variables panel, preview panel, and version history panel is reachable and operable via keyboard alone (§5 of `02_UI.md`). **Partially verified, partially QA:** Tab order was verified sane and sequential across the sidebar/toolbar/list this session. **QA ticket** for a human pass: Escape-to-close and focus-trap-on-open for `AlertDialog` confirmations — every dialog this session was opened via a synthetic, untrusted `.click()` (ref-based clicks failed on composed Base UI triggers throughout this session), so the trusted-user-gesture keyboard path is unverified. This is shared, unmodified `AlertDialog` code already used by Documents/Secrets/Project Init, so there is no evidence of a Prompt-Studio-specific defect — but per the project owner's explicit instruction, this stays on the QA list, not silently checked.
- [x] The diff view distinguishes additions/removals with text markers, not color alone (§5 of `02_UI.md`) — live-verified: `+`/`-` text prefixes confirmed present in the rendered diff output, in addition to color.
- [x] Both light and dark themes render correctly across every new screen/panel (`next-themes`, per [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §1) — live-verified: `html.dark` class applies, Monaco switches to `vs-dark`, decoration colors remain legible against the dark background. **QA ticket** for pixel-level screenshot confirmation — this environment's screenshot tool failed ("Browser pane is not displayed, so the page is not compositing frames"); verification here was via computed styles and DOM/class inspection, not a visual screenshot.

## 3. Quality acceptance criteria

- [x] All tests enumerated in [`07_TESTING.md`](07_TESTING.md) §1 pass — full backend suite (`pytest backend/tests/ -v`), not just the new tests. — 120 passed, re-confirmed as the very last step of T17, after every fix in this document.
- [x] `npm run build`, `npm run lint`, and `tsc --noEmit` all pass clean, per [`07_TESTING.md`](07_TESTING.md) §2. — confirmed clean after every round of fixes (T15, T17).
- [x] `docker compose build` and `docker compose up` succeed; the `0005_prompt_studio` migration applies cleanly on both a fresh install and an upgrade from `0004`. — T16: verified in a fully isolated clean-room Docker Compose stack (separate project name/volume from the user's own running deployment); migration confirmed on a genuinely fresh volume.
- [x] No architectural invariant violated: routers stay thin, no cross-feature imports, models are the schema source of truth, no ORM object exposed directly (per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2, verified against [`03_BACKEND.md`](03_BACKEND.md) §4's checklist). — confirmed by code review of `api/routes/prompt_studio.py` (parses/delegates/shapes only) and `schemas/prompt_studio.py` (every response shaped through a Pydantic model, never a raw `Prompt`/`PromptVersion`).
- [x] Zero new entries required in [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) — confirmed no new runtime dependency was introduced (per [`01_SPEC.md`](01_SPEC.md) §5 / `03_BACKEND.md` §4). — confirmed: no new backend or frontend dependency added anywhere in this phase (`string.Template`, `@monaco-editor/react`, `diff` were all already in the stack).
- [x] [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) feature-level checklist satisfied in full. — all four sub-items satisfied: this document's criteria all checked/QA-ticketed; `CURRENT_STATE.md` reflects reality; Known Issues documents every honest gap (none silently dropped); a checkpoint has been produced at every milestone.
- [x] No regression in the existing backend test suite or in the sidebar/command-palette entries for any pre-existing feature (per [`07_TESTING.md`](07_TESTING.md) §4). — full pre-existing suite re-confirmed green at every checkpoint; sidebar/command-palette spot-checked live multiple times this session with every pre-existing entry intact.

## 4. Sign-off

Per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md), sign-off is the project owner's explicit decision at the Release Candidate → Owner Sign-off transition, evaluated against [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §6's merge criteria: zero open BLOCKERs, MAJOR/MINOR findings triaged (not silently dropped), and every criterion in §1–§3 above either checked or explicitly filed as a QA ticket per [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §4 (e.g. a criterion needing a real screen reader or real mobile device, if this environment can't verify it directly).

**T17 close-out summary (2026-07-22):** every criterion in §1–§3 is now checked against direct evidence, or explicitly filed below as a QA ticket per [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §4 (a genuinely-can't-verify-here item, not a bug). Three real findings surfaced during this formal pass and were fixed on the spot, not deferred:

- **Client-side validation was missing entirely** (§1 criterion 17) — added `maxLength` on name/description/variable fields, tag count/length inline validation, and a body-length counter that disables Save over 20,000 characters. Classified: was a MAJOR-severity gap against the accepted spec (a real, confirmed feature absence, not cosmetic) — fixed before sign-off, not backlogged.
- **`Copy` had no error handling** (§1 criterion 7) — a clipboard-write failure (which this automation environment reproduces because its tab lacks `document.hasFocus()`, not something a real user's active browser tab would lack) failed completely silently. Classified: MINOR (an edge-case robustness gap, not a functional break for real users) — fixed anyway since it was cheap and directly improves the "visible confirmation" guarantee the criterion requires either way.
- **Responsive collapse was missing entirely**, found during T15 (§2, already recorded above) — classified MAJOR against the accepted spec at the time, fixed then, re-confirmed here.

**QA tickets (environment-limited, not bugs — per [`12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md) §4), carried into Stage 4:**
- Real human keyboard typing into the Monaco body editor (this session could only drive Monaco via its own model API, not real key events).
- Escape-to-close / focus-trap-on-open for `AlertDialog` confirmations under a real, trusted user gesture (every dialog here was opened via a synthetic `.click()`).
- Pixel-level screenshot confirmation of dark mode and the responsive collapse (this environment's screenshot tool failed outright).
- The `Copy` success-path toast, specifically (the error path is confirmed; the success path is code-reviewed-correct but not runtime-triggered here, same `document.hasFocus()` reason as above).
- High-DPI scaling (not a pre-existing `08_ACCEPTANCE.md` criterion, but explicitly requested by the project owner to stay tracked; not testable without a real display).

Zero open BLOCKERs. No criterion above is checked on a "looks implemented" basis — each line states what was actually run (a specific test name, a specific live browser action, or a specific code-review point).

- [ ] Sign-off recorded in `CURRENT_STATE.md` Session Notes once granted (not yet applicable — this phase has not yet had its Stage 4 Release Candidate audit).

## 5. TODO

- [ ] None — this document's T17 pass is complete. The five items above remain as open QA tickets carried into Stage 4 (RC Audit) and Stage 5 (Release), not gaps in this document itself.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [02_UI.md](02_UI.md)
- [07_TESTING.md](07_TESTING.md)
- [README.md](README.md) — Definition of Complete
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
