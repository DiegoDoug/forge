# Model Playground — QA

> **Purpose:** Tracks QA work that is deliberately separate from implementation — a criterion that needs a real keyboard/hardware session rather than an automated one, so it doesn't block Phase 05 sign-off while remaining genuinely open.
> **Scope:** This phase only.
> **Depends on:** [`../../../implementation/Phase-05-Model-Playground/08_ACCEPTANCE.md`](../../../implementation/Phase-05-Model-Playground/08_ACCEPTANCE.md) §2, [`../../../implementation/Phase-05-Model-Playground/CURRENT_STATE.md`](../../../implementation/Phase-05-Model-Playground/CURRENT_STATE.md)

---

| Ticket | Title | Status |
|---|---|---|
| [QA-0001](QA-0001-keyboard-activation-audit.md) | Keyboard-only activation audit (real hardware, not scripted key-dispatch) | Open |

This exists because the automated browser session used for this phase's manual verification pass reproduced the exact synthetic-keyboard-event limitation already documented in [Phase 01's `POST_IMPLEMENTATION_REVIEW.md`](../../../history/Phase-01/POST_IMPLEMENTATION_REVIEW.md) ("Unexpected Problems": dispatched Enter/Space key presses arrive with an empty `key` field, silently defeating native `<button>` activation) — a known property of the tool, not a defect in this phase's code. It does not block Phase 05 sign-off, but must be run and closed out by a human with real keyboard hardware before this phase's accessibility posture is considered fully verified, not merely implemented.
