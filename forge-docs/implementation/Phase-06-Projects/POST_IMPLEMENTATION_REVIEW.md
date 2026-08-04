# Projects — Post-Implementation Review

> **Purpose:** A retrospective on how Phase 06 actually went — not a restatement of what was built (see `CURRENT_STATE.md`/`08_ACCEPTANCE.md` for that), but what the process revealed.
> **Scope:** This phase's full arc: baseline inspection, specification, ADR-0014, implementation, testing, manual QA, and release.
> **Status:** Final — Phase 06 Released & Frozen as `v0.6.0-projects`.
> **Last Updated:** 2026-08-03
> **Depends On:** [../../implementation/Phase-06-Projects/CURRENT_STATE.md](CURRENT_STATE.md), [../../implementation/Phase-06-Projects/08_ACCEPTANCE.md](08_ACCEPTANCE.md)

---

## What Went Well

- **The baseline inspection caught that the phase wasn't actually authorized before any code was written.** Every Phase 06 doc (`01_SPEC.md` through `09_IMPLEMENTATION_TASKS.md`) was an unfilled template, and the repo's own `09_CLAUDE_CODE_RULES.md` §1–§2 explicitly says to stop and flag this rather than guess. Flagging it to the user, rather than inventing a spec unilaterally or refusing outright, produced a fast, concrete resolution (confirmed scope: grouping + per-project default AI provider/model) that the rest of the phase could build on with confidence.
- **Reusing Model Playground's `runs.create_run()` directly for AI execution, rather than building a second orchestration path, kept this phase's biggest risk (a second AI-credential surface) at zero.** No new outbound-call code was written; the project-level "quick run" is a thin caller of the exact same function Model Playground's own endpoint calls.
- **Manual verification used a real OpenAI API call (with an intentionally invalid test key), not a mock, for the browser QA pass.** Watching the actual 401 flow through to "Authentication failed - check the configured API key" end-to-end confirmed the whole chain (project → AI config → `runs.create_run()` → real adapter → real network call → clean error surfacing → project-scoped history) in one real test, the same technique Phase 05's review recommended repeating.
- **Deletion behavior (unscope, never cascade) was verified against the database directly, not just the UI.** After deleting a project through the UI, its former secret/note/document were re-fetched via direct `fetch()` calls in the browser console and confirmed to have `project_id: null` with every other field untouched — the exact scenario ADR-0014 was written to guarantee.
- **A single-session, non-branched workflow (spec → implement → test → QA → release, all in one continuous session) still produced two real bugs caught before release** — the migration downgrade's FK-drop issue and the missing default Workbench panel entry — both found by actually exercising the feature end-to-end rather than trusting that "it compiles and the happy path works" was sufficient.

## What Didn't

- **This phase didn't use a feature branch.** Every prior phase (01–05) followed feature branch → PR → squash-merge → tag → separate post-release freeze commit. This phase committed directly to `master` per the user's explicit instruction for this release. This was a deliberate, explicitly-authorized deviation for this session, not an oversight — but it means Phase 06 has no PR record the way Phases 01–05 do, which is a real, if intentional, gap in this phase's audit trail compared to precedent.
- **`10_RELEASE_NOTES.md`/`POST_IMPLEMENTATION_REVIEW.md` were written retroactively at release time, not incrementally through a Release Candidate stage**, unlike Phase 05 where `10_RELEASE_NOTES.md` was described as "written at RC, updated through sign-off." This phase compressed spec → implementation → RC → QA → sign-off into one continuous session, so there was no natural RC checkpoint to draft the release notes against as they came in. The content is accurate (written with full knowledge of what actually shipped) but the process didn't match the incremental-drafting precedent.

## Unexpected Problems

- **A `Select.Value` (Base UI) renders the raw item `value`, not its resolved label, unless given a render function.** The new `ProjectPicker` initially showed the literal sentinel string `__none__` instead of "No project," and the AI provider picker showed `openai` instead of "OpenAI." Confirmed via direct `getBoundingClientRect()`/DOM inspection that this wasn't a browser-tool artifact before concluding it was a real app bug — the pre-existing Secrets "Type" picker exhibits the identical raw-value-not-label behavior (confirmed via the same technique), meaning this is a pre-existing characteristic of the shared `components/ui/select.tsx` wrapper, not something Phase 06 introduced into shared code. Fixed narrowly, in only the two new components Phase 06 owns, using `Select.Value`'s children-as-function API — the shared component and its other consumers were left untouched, per scope discipline.
- **The same fix surfaced a second, related issue:** toggling a `Select`'s controlled `value` prop between `undefined` (on first render, when nothing is selected) and a defined string (once something is) produces a real React/Base UI console warning ("changing the uncontrolled value state of Select to be controlled"). Fixed by always passing a defined string (empty string for "nothing selected," never `undefined`) — verified fixed via an in-page `console.error` interception, not just by the warning no longer appearing in a stale log (the browser automation tool's console-message buffer persisted across page navigations in this session, which briefly looked like the fix hadn't taken effect until isolated with a fresh capture).
- **The automated browser tool's ref-based element clicking was unreliable against Base UI's portal-rendered `Select` popup options** — clicks resolved to coordinate `(0, 0)` even though the popup was genuinely open with correct real geometry (confirmed via `getBoundingClientRect()`). Dispatching a real `pointerdown`/`pointerup`/`click` sequence directly via `javascript_tool` against the actual DOM element (not through the ref-based bridge) worked reliably and exercises real event handling, not a bypass of it. Worth naming so a future session doesn't lose time on the same tooling friction.
- **The Browser pane in this session never composited a real screenshot** ("the Browser pane is not displayed"), so all verification was done via `read_page`/`get_page_text`/`javascript_tool` DOM/console inspection rather than visual screenshots. This didn't block verification — every functional and visual-structure claim (dark mode applying the `dark` class and computing a dark background, no horizontal overflow at mobile width) was confirmed via computed-style/DOM inspection instead — but it's a different verification modality than prior phases' screenshot-based passes.

## Architecture Changes

None beyond what ADR-0014 called for. Specifically confirmed:

- No new outbound-call code path — `services/projects/service.py::run_project_prompt` calls `model_playground.runs.create_run()` directly.
- No new credential storage — `Project.default_provider`/`.default_model` are plain strings, the same "snapshot, not FK" pattern `PlaygroundResult.provider`/`.model` already established (ADR-0011 §2.4).
- No cross-feature backend import beyond the one explicitly designed in ADR-0014 (`services/projects` → `services/model_playground`), which mirrors an already-accepted pattern (`services/model_playground/runs.py` itself depends on `services/model_playground/providers/`).
- One sanctioned frontend cross-feature import: `features/secrets`, `features/notes`, `features/documents` each import the shared `ProjectPicker` from `features/projects`, precedented by `features/notes/workbench-panel.tsx` already importing from `features/workbench`.
- `services/workbench.py`'s `DEFAULT_LAYOUT_PANELS` gained one entry (`recent_projects`) — the same registration point every prior panel-owning phase needed, per Phase 05's own review recommendation to "check whether a new feature needs registration in Workbench... early."

## Performance Notes

- Project list/detail counts are computed with one `COUNT` query per child table per request (no materialized counter column) — appropriate for Forge's stated data volumes (self-hosted, single-operator), not benchmarked under load.
- The AI quick-run path adds no new latency characteristics beyond what Model Playground's existing `runs.create_run()` already has (60s timeout, concurrent dispatch) — verified functionally via a real network call, not independently re-benchmarked, since it's the identical code path Model Playground itself uses.

## Accessibility Notes

- All new interactive elements (project picker, AI config selects, quick-run textarea, delete confirmation) are built from the same shared shadcn/Base UI primitives (`Select`, `Dialog`, `Textarea`, `Button`) used throughout the rest of the app, inheriting their existing keyboard/ARIA behavior rather than introducing new custom controls.
- Dark mode confirmed via computed-style inspection (the `dark` class applied to `<html>`, background computed to a dark value) rather than a visual screenshot comparison, since the Browser pane did not composite in this session (see Unexpected Problems).
- Mobile viewport (375×812) confirmed to introduce no horizontal overflow (`document.documentElement.scrollWidth === clientWidth`) on the Projects list page.
- Not independently re-verified in this phase: real-hardware keyboard-only activation (Enter/Space on a focused button), the same open QA item Phase 05's review carried forward — see that phase's `QA/QA-0001-keyboard-activation-audit.md`. Not re-opened as a new ticket here since it's an already-tracked, cross-phase tool characteristic, not something specific to this phase's controls.

## Lessons Learned

1. **When a phase's own documentation set is a template scaffold, say so and stop, rather than treating the mission's own framing as an implicit substitute spec.** The autonomous mission prompt for this phase described an AI-configuration-heavy feature; the actual repo objective was organizational grouping with AI configuration as a secondary concern. Surfacing the mismatch and asking, rather than picking one framing unilaterally, produced a scope decision the user actually wanted.
2. **A visually-correct DOM state and a tooling-reported interaction failure are two different claims — verify which one is actually true before concluding either "it's a real bug" or "the tool is wrong."** The `(0, 0)` click-coordinate issue looked identical whether it meant "the popup genuinely isn't rendering" (an app bug) or "the accessibility-tree bridge has a timing race" (a tool limitation) until `getBoundingClientRect()` was checked directly — which is what turned up the real, separate `Select.Value` label bug hiding underneath the false alarm.
3. **A registered capability (a Workbench panel, in this case) and a *discoverable* capability are not the same thing** — frontend registration alone doesn't make a panel appear; it also needs a corresponding entry in the backend's default set. This is a two-sided contract worth checking explicitly for any future phase that registers a new panel, matching Phase 05's own recommendation to check Workbench integration early — this phase confirms that recommendation was necessary but not sufficient by itself, since even having read it, the panel-registration half was still missed until QA actually looked for the panel in the running app.

## Recommendations for Phase 07

- **Check `Select.Value`'s label-rendering behavior early if Knowledge Hub introduces new provider/category pickers** — the underlying `components/ui/select.tsx` wrapper renders raw item values by default; any new consumer needs the children-as-function workaround unless the shared wrapper itself is fixed (a cross-cutting change deliberately left out of this phase's scope).
- **When adding a new Workbench panel, add it to both `registerWorkbenchPanel` (frontend) and `DEFAULT_LAYOUT_PANELS` (`app/services/workbench.py`, backend) in the same commit** — verify by actually loading the Workbench page (or resetting layout) in manual QA, not just by confirming the component compiles.
- **If a future phase's release also skips the feature-branch/PR flow (direct-to-master, as this phase did per explicit instruction), say so explicitly in that phase's own release notes and post-implementation review**, the way this document does — so the audit trail stays honest about which phases have a PR record and which don't, rather than letting readers assume every phase followed the same process.

## Cross-references

- [../../implementation/Phase-06-Projects/CURRENT_STATE.md](CURRENT_STATE.md)
- [../../implementation/Phase-06-Projects/08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../implementation/Phase-06-Projects/09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [10_RELEASE_NOTES.md](10_RELEASE_NOTES.md)
- [../../decisions/0014-project-data-model-shape.md](../../decisions/0014-project-data-model-shape.md)
- [../Phase-05-Model-Playground/](../../history/Phase-05/POST_IMPLEMENTATION_REVIEW.md)
