# Workbench — Post-Implementation Review

> **Purpose:** A retrospective on how Phase 01 actually went — not a restatement of what was built (see `CURRENT_STATE.md`/`08_ACCEPTANCE.md` for that), but what the process revealed. Recommended by the project owner as a standing per-phase document, starting here.
> **Scope:** This phase's implementation, T1–T16, plus the post-T16 independent audit.
> **Status:** Final — Phase 01 released as `v0.1.0-workbench` and frozen; archived here per the project owner's direction to keep the active implementation folder focused on the specification. QA-0001/QA-0002 and the 4 non-blocking `BUGS/` findings remain open per the release notes, but don't change this review's content.
> **Last Updated:** 2026-07-21
> **Depends On:** [../../implementation/Phase-01-Workbench/CURRENT_STATE.md](../../implementation/Phase-01-Workbench/CURRENT_STATE.md), [../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md](../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md), [QA/README.md](QA/README.md)

---

## What Went Well

- **The milestone/checkpoint structure held up.** Four milestones (Foundation, Backend, Frontend, Integration), each ending in a real checkpoint with a `history/` record, meant every session picked up with full context instead of re-deriving it. No milestone had to be redone or reordered.
- **The panel-registry architecture (ADR-0002) delivered on its promise inside this phase.** `RecentNotesPanel` living in `frontend/features/notes/` and registering itself through `register-all.ts` — not special-cased anywhere in `WorkbenchGrid` — is a real, working instance of the extensibility contract, not just a design on paper. (The post-audit review did find that this same architecture has a real gap in how it treats *unregistered* panel types during persistence — see "What Didn't" — but the registration/rendering half of the contract is solid.)
- **The compatibility-migration pattern (Vault→Secrets, T1) avoided a breaking change.** Aliasing `/api/vault`→`/api/secrets` and redirecting `/vault`→`/secrets` instead of a hard cutover meant the rename shipped with zero risk to anything still pointing at the old path — a real, working example of the phase's own "existing functionality > new functionality" priority order.
- **The staged Dashboard→Workbench cutover (backend live at both `/api/dashboard` and `/api/workbench` through T5–T12, frontend staged at `/workbench` through T9–T12, both cut over together at T13/T14) meant the old surface was never at risk of breaking mid-phase.** Nothing was ever in a half-migrated state that a bug could hit.
- **Manual/scripted verification caught two real, non-trivial bugs before they shipped as "verified":**
  - T11: the panel-registration bootstrap import lived in a Server Component, where it wasn't guaranteed to execute in the browser bundle — found by actually testing in a browser, not by code review.
  - T15/post-audit: `AlertDialogAction` never closed its dialog (Base UI has no auto-closing "Action" primitive, unlike Radix) — a bug that also silently affected the pre-existing Secrets delete-confirmation flow, caught only because T15's manual pass happened to exercise the Reset confirmation dialog specifically.

## What Didn't

- **The independent post-T16 audit found 5 issues that the phase's own verification tasks (T15 manual pass, T16 axe scan, backend test suite) all missed**, none of which are exotic — they were findable by careful code reading against the spec, without running anything:
  - A real data-loss bug: panel drag-reorder/visibility-toggle silently strips unregistered panel types from the persisted layout, contradicting the panel-registry's own stated extensibility guarantee.
  - Asymmetric validation: pinned-tool duplicates aren't rejected, panel-type duplicates are.
  - Inconsistent failure UX: 3 of 4 layout-mutating actions show no error toast on failure, only 1 does.
  - Dead backend computation: `recent_notes` is computed and returned by `get_workbench()` but never consumed by any panel.
  - An unused contract surface: the `onError` panel prop is never called by any of the five shipped panels.
  - This suggests the phase's testing strategy (manual functional pass + one automated scan + backend unit tests) is good at catching "does the happy path work" and "is this accessible" but weak at catching "does every code path that *can* run actually get exercised, and does the implementation match the spec's stated guarantees in every corner, not just the ones a manual walkthrough happens to hit." A structured code-review pass against the spec, done deliberately and separately from functional verification, caught things functional verification structurally couldn't.
- **Two of `08_ACCEPTANCE.md`'s criteria (drag FPS/Profiler, live screen-reader pass) were unverifiable by construction in this environment**, not because anyone skipped them — an automated Claude Code browser session cannot service animation frames or run NVDA/VoiceOver. This wasn't discovered until T16, at the very end. A phase that plans for automated-only verification should flag upfront which acceptance criteria structurally require a human/device session, rather than discovering it during Final Validation.

## Unexpected Problems

- **The automated browser tool used for T13 through the post-audit had a compositor that never serviced animation frames** — confirmed directly (`element.getAnimations()[0].currentTime` stuck at exactly `0` across multiple real elapsed seconds; a scheduled `requestAnimationFrame` never fired). This single root cause explained three separate symptoms that initially looked like three separate bugs: dismissed dialogs appearing to "stick" open visually, the customize-mode focus-management code not visibly taking effect, and the inability to measure drag FPS. Diagnosing "is this a real bug or a tool artifact" took real, deliberate investigation each time (dispatching synthetic `animationend` events, forcing `Animation.finish()`, checking `getAnimations()` state) rather than being obvious from the symptom alone.
- **The same tool's synthetic keyboard events were subtly malformed** (dispatched `Enter`/`Space` key presses arrived with an empty `key` field), which silently defeats native `<button>` Enter/Space activation — a browser platform guarantee that has nothing to do with app code. This had already been documented once, at T12, for dnd-kit's keyboard sensor specifically; it resurfaced at T16 for plain button activation, meaning it's a general property of the tool, not something specific to one library's event handling.
- **The `computer` tool's `screenshot`/`zoom` actions consistently timed out** in the verification sessions used for this phase, regardless of page state. Verification had to lean entirely on the accessibility tree, direct DOM/CSS inspection via injected JavaScript, and network-timing APIs — which turned out to be sufficient, but wasn't the first-choice tool for the job.
- **Two local dev-server data directories were used across the phase** (`backend/.dev-data/` for the persistent dev session, `backend/.dev-data-verify/` created fresh for each verification pass) specifically to avoid colliding with a previously-completed `/api/setup` from an unrelated already-running Docker Compose stack on this machine. Worth calling out because it's exactly the kind of environment detail that silently derails a session if not noticed early (as happened once, at T9, before the pattern was established).

## Architecture Changes

None beyond what the spec already called for. Specifically confirmed **not** introduced, per the ADR-0009 freeze and the post-audit's explicit scope-freeze check (grepped for `CapabilityRegistry`/`ProjectProvider`/`ProjectContext`/`workflow` across the whole diff — zero matches):

- No generalized Capability Registry (ADR-0008 stays `Proposed`).
- No `ProjectProvider`/`ProjectContext`/Projects interface (ADR-0005's Phase 06 scope untouched).
- No workflow-related code.
- No command-palette expansion beyond the plain `/search` page (ADR-0007 §6's future direction stays deferred).

The one deliberate, spec-authorized deviation: `03_BACKEND.md` §1 described the Dashboard→Workbench move as a rename "in place" (`dashboard.py` → `workbench.py`, one file). In practice it shipped as two files coexisting (`dashboard.py` untouched, `workbench.py` new) from T5 through T14, because the old route had to keep working until the new frontend was proven. This was recorded as a clarification against the locked spec (ADR-0009 §2 permits clarifications), not a scope change, and resolved for real at T14 when the old files were deleted outright.

## Performance Notes

- Initial Workbench render (cold load through `GET /api/workbench` resolving): ~644ms against the dev server (`next dev --turbopack`), comfortably under the 1s budget. Not independently re-measured against the Docker Compose production build specifically, though that build was confirmed to succeed at both T12 and T16.
- `PUT /api/workbench/layout` round-trip: 18.3ms measured, an order of magnitude under the 200ms budget.
- Drag-reorder FPS and React DevTools Profiler re-render counts are **not measured at any point in this phase** — see QA-0001. This is a real gap, not a formality; dnd-kit's transform-based dragging is the right *approach* for 60fps, but "the right approach" and "measured at 60fps" are different claims and only the first one is backed by anything here.
- The post-audit found one concrete performance issue worth fixing regardless of QA-0001's outcome: `get_workbench()` runs a real SQL query (`select(Note)...limit(6)`) and serializes its result into every single `/api/workbench` response, for a field (`recent_notes`) that no panel reads. Small in absolute terms, but it's waste on the hottest endpoint in the feature (every page load, every optimistic-update settle).

## Accessibility Notes

- Full keyboard-Tab navigation, ARIA labeling on every Workbench-owned control (visibility switches, drag handles, pin/unpin switches), and an automated `axe-core` scan (zero violations scoped to Workbench's own `<main>` in both modes, the pin picker, and `/search`) are all verified.
- Keyboard-only drag-and-drop reorder (dnd-kit's `KeyboardSensor`, Space/Arrow/Space) is verified end-to-end for both panel reorder and pin reorder, including real persistence — this required dispatching synthetic `KeyboardEvent`s directly rather than using the browser tool's built-in key-press action, per the tool limitation noted above.
- Two real, but explicitly out-of-scope, accessibility bugs were found in *global app-shell chrome* while verifying Workbench (not introduced by this phase, predate it, and touch no file any Workbench task owns): the mobile-nav hamburger button has no accessible name at all, and the sidebar footer text plus the command palette's dialog header each trip a minor axe violation. Both are filed as separate background tasks rather than folded into this phase's scope.
- Not verified: a live screen-reader pass (VoiceOver/NVDA) and real-hardware keyboard-only walkthrough — see QA-0002. Focus-management code (customize-mode enter/exit, pin-picker open/close) was reviewed and judged correct but couldn't be observed live in this environment for the `requestAnimationFrame` reason noted above.

## Lessons Learned

1. **"Verified" needs to specify verified *how*.** T15/T16's own documentation was careful to distinguish "browser-verified end-to-end" from "code-reviewed as correct, not live-observed" — that discipline is exactly what made it possible to tell, later, which unverified claims were honest gaps (FPS, screen-reader) versus which were bugs nobody had looked hard enough to find (the panel-deletion bug). A phase that just says "tested" without saying what kind of test would have made this review much less useful.
2. **A dedicated, adversarial code-review pass — done by someone (or something) told to assume the implementation is wrong until proven otherwise — finds a different class of bug than functional verification does.** Functional verification confirms the paths you think to walk work. A structured comparison of every implementation file against every spec sentence finds the paths nobody thought to walk. Both are needed; neither substitutes for the other.
3. **When an automated verification environment misbehaves (frozen animation clock, malformed synthetic events, timing-out tool actions), the instinct to "just note it and move on" is right, but only after confirming it's actually an environment issue and not the app.** Every environment-limitation claim in this phase's docs is backed by a specific, reproducible piece of evidence (`getAnimations().currentTime` stuck at 0, `event.key` empty, etc.), not just "seemed flaky." That discipline is what let a later reviewer (this document) trust those claims instead of having to re-litigate them.
4. **Symmetric-looking code paths should get symmetric validation and symmetric UX, and the asymmetries are often invisible until someone puts the two side by side.** `_validate_panels` and `_validate_pinned_tools` sit three lines apart in the same file and diverge on duplicate-checking; the Pin Picker's toggle and the other three layout-mutating handlers sit in sibling files and diverge on error-toast behavior. Neither asymmetry was an intentional design choice recorded anywhere — both look like one code path getting a feature the other should have gotten too, and nobody went back to check.
5. **"Owns its own data" (the panel-registry principle) and "the aggregate endpoint still computes it anyway" can both be true at once, silently, for a long time.** `RecentNotesPanel` correctly fetches independently per the architecture's own stated preference; nobody removed the now-orphaned `recent_notes` field from the backend response when that choice was made. Architectural correctness at the consumption site doesn't automatically clean up the production site.

## Recommendations for Phase 02

- **Budget an explicit code-review/audit pass, separate from functional verification, before calling a phase's implementation done** — not as a replacement for the manual/automated verification this phase already does well, but as a second, differently-shaped pass. This phase's 5 late-found issues are the concrete argument for it.
- **Identify which acceptance criteria structurally require a human/device session up front, at spec time, not at Final Validation.** `08_ACCEPTANCE.md` could have flagged "these two need a real browser + human, not automation" back when it was drafted, saving the discovery for T16.
- **When two code paths do conceptually the same kind of thing (two validators, four mutation handlers, N panels), check them against each other, not just against the spec individually.** This phase's asymmetries (duplicate-checking, error toasts) would have been easy one-line greps if anyone had thought to compare siblings directly.
- **Watch for "the architecture moved but the old computation didn't get cleaned up" specifically at panel/data-ownership boundaries**, since Phase 02 will add more panels and more owning-feature data fetches, and each one is a chance to leave the aggregate endpoint computing something nobody reads anymore.
- **Carry forward the environment-limitation documentation discipline** (specific reproducible evidence, not vague "this seemed off") — it's what made this review possible to write with confidence instead of re-investigating everything from scratch.

## Cross-references

- [../../implementation/Phase-01-Workbench/CURRENT_STATE.md](../../implementation/Phase-01-Workbench/CURRENT_STATE.md)
- [../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md](../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md)
- [QA/README.md](QA/README.md)
- [../../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md](../../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md)
- [10_RELEASE_NOTES.md](10_RELEASE_NOTES.md)
- [README.md](../README.md) — checkpoint/history index
