# QA-0002 — Run a real screen-reader pass and an automated `axe` sweep once tooling exists

> **Purpose:** Close out the two accessibility-verification methods [`../08_ACCEPTANCE.md`](../08_ACCEPTANCE.md) AC46 calls for that this phase's toolchain cannot perform.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual screen-reader session + automated `axe`-core integration (neither exists in this repo's current toolchain — no frontend test runner exists per [`../07_TESTING.md`](../07_TESTING.md) §2, and no `axe`/equivalent package is installed)
> **Blocks Phase 09 sign-off:** No. Owner sign-off (2026-08-07) explicitly accepted AC46 as satisfied by its manual equivalent. Tracked here so the gap is neither silently dropped nor falsely checked off, per [`../../../13_PHASE_LIFECYCLE.md`](../../../13_PHASE_LIFECYCLE.md) §3.

---

## What Phase 09 did instead

T27 (Forge's first accessibility pass) substituted a manual equivalent for both methods this ticket exists to close:

- **Contrast:** measured live via a custom JS luminance/contrast script against every token pair actually rendered, in both themes — not an eyeball check. Found and fixed one real WCAG failure (Secrets' tag badges).
- **Accessible names / landmarks:** a manual sweep for missing `aria-label`s and `role="presentation"` misuse — found and fixed 9 unlabeled icon-only controls, 7 unlabeled note-color swatches, and one nav-landmark/grouping gap.

This is real, defect-finding coverage — not a rubber stamp — but it is not equivalent in *breadth* to either of the two methods below.

## What remains open

1. **A real screen-reader pass** (NVDA/JAWS/VoiceOver) across all 17 routes. An automated browser session cannot drive a screen reader meaningfully — there is no way to verify what is actually *announced*, only what is present in the accessibility tree. This class of gap is identical in kind to Phase 08's QA-0001 (automated sessions cannot exercise real assistive-technology or hardware-input behavior).
2. **An automated `axe`-core (or equivalent) sweep.** No such package exists in `frontend/package.json` — installing one is itself a frontend-tooling decision (see `CURRENT_STATE.md` Known Issue #2: no frontend test framework at all), not something to fold into a presentation-layer phase without a separate scoping decision.

## How to run it

1. **Screen reader:** open each of the 17 routes in a real browser with NVDA (Windows) or VoiceOver (macOS) running. Confirm: every icon-only control announces a name; every dialog/sheet announces its title on open; every landmark group is announced when navigating by region; every list surface announces item count/position where applicable.
2. **`axe`:** once a frontend test framework is chosen (tracked separately, not this ticket's job to pick), add `@axe-core/playwright` or `jest-axe` and run it against all 17 routes in both themes. Compare findings against T27's manual sweep — any *new* finding here is a real gap T27's manual method missed; anything already fixed by T27 should come back clean, which is itself a useful check that T27's manual work was accurate.

## Acceptance criteria

- [ ] A real screen-reader pass completed across all 17 routes, findings resolved or filed as new tickets.
- [ ] An automated `axe` (or equivalent) integration exists and has been run against all 17 routes in both themes, findings resolved or filed as new tickets.
- [ ] `08_ACCEPTANCE.md` AC46 updated from "partial — manual equivalent" to "satisfied" once both are done.

## Cross-references

- [../08_ACCEPTANCE.md](../08_ACCEPTANCE.md) AC46 — the criterion this defers
- [../CURRENT_STATE.md](../CURRENT_STATE.md) Known Issue #2 — no frontend test framework, the structural reason neither method is automatable today
- [../09_IMPLEMENTATION_TASKS.md](../09_IMPLEMENTATION_TASKS.md) T27 — the manual work this ticket builds on, not replaces
- [../../Phase-08-Developer-Toolkit/QA/QA-0001-tab-keyboard-activation.md](../../Phase-08-Developer-Toolkit/QA/QA-0001-tab-keyboard-activation.md) — the precedent for "automated session cannot close this, tracked rather than dropped"
