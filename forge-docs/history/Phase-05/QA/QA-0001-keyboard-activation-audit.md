# QA-0001 — Keyboard-only activation audit

> **Purpose:** Close out [`../../../implementation/Phase-05-Model-Playground/08_ACCEPTANCE.md`](../../../implementation/Phase-05-Model-Playground/08_ACCEPTANCE.md) AC18 (keyboard navigation reaches every interactive element) with a real-hardware pass, since this session's automated browser could not conclusively verify Enter-key *activation* (only Tab focus order).
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual audit — real keyboard hardware, no mouse
> **Blocks Phase 05 sign-off:** No — tracked here specifically so it does not block. See [`../../../implementation/Phase-05-Model-Playground/08_ACCEPTANCE.md`](../../../implementation/Phase-05-Model-Playground/08_ACCEPTANCE.md) §2 (AC18) and [`../../../implementation/Phase-05-Model-Playground/CURRENT_STATE.md`](../../../implementation/Phase-05-Model-Playground/CURRENT_STATE.md) for why.

---

## Why this is a QA task, not a bug

During manual verification, Tab order through the Model Playground page was confirmed correct (sidebar → theme toggle → Lock → provider Configure buttons → prompt textarea → provider/model checkboxes → submit → history rows, in a sensible sequence). Attempting to *activate* a focused button with a synthetic Enter or Space keypress (via the automated browser tool) did not open the credential dialog, even though a mouse click on the identical, already-focused element worked immediately.

This was not treated as a real bug because the identical non-activation was reproduced on the pre-existing, already-shipped Secrets page's "New secret" button — a control this phase never touched. [Phase 01's `POST_IMPLEMENTATION_REVIEW.md`](../../../history/Phase-01/POST_IMPLEMENTATION_REVIEW.md) independently documented the same root cause over a month earlier: *"the same tool's synthetic keyboard events were subtly malformed (dispatched Enter/Space key presses arrived with an empty `key` field), which silently defeats native `<button>` Enter/Space activation — a browser platform guarantee that has nothing to do with app code."* Per [`../../../12_BUG_CLASSIFICATION.md`](../../../12_BUG_CLASSIFICATION.md) §4, an acceptance criterion that's unverified because the verification environment structurally can't check it is not a BLOCKER/MAJOR/MINOR bug — it's an unverified claim, tracked as a QA ticket.

## Scope

- Model Playground page (`/model-playground`): provider Configure/Replace-key/Remove-key buttons, credential-form dialog (label/API-key inputs, Save/Cancel), prompt textarea, provider/model checkboxes, "Run comparison" submit, result-panel retry/copy actions, history row selection and delete (with its confirmation dialog).

## Acceptance criteria (from `08_ACCEPTANCE.md` §2, AC18)

- [ ] Real keyboard hardware (no scripted key-dispatch): Tab/Shift+Tab reaches every interactive element in the scope above, in a sensible order (already confirmed automatically — re-confirm with a human).
- [ ] Enter and Space both activate every button reached via Tab (Configure/Replace/Remove key, checkboxes, Run comparison, history row, delete confirmations) — this is the specific claim the automated session could not verify.
- [ ] Focus lands sensibly after a dialog opens/closes (credential dialog, delete-confirmation `AlertDialog`s) and doesn't get lost or reset to the top of the page.

## How to run it

1. Use a real keyboard on real hardware (not a scripted/CDP-dispatched key event) — unplug or ignore the mouse.
2. Configure a provider key, replace it, remove it, submit a run, select/delete a history entry — all via Tab + Enter/Space only.
3. Note anything that's reachable by Tab but doesn't activate on Enter/Space, or where focus is lost/unclear after a dialog opens or closes.

## Result

_Not yet run. Fill in with findings and a pass/fail once done._

## Cross-references

- [../../../implementation/Phase-05-Model-Playground/08_ACCEPTANCE.md](../../../implementation/Phase-05-Model-Playground/08_ACCEPTANCE.md) §2 (AC18)
- [../../../implementation/Phase-05-Model-Playground/07_TESTING.md](../../../implementation/Phase-05-Model-Playground/07_TESTING.md) §3
- [../../../implementation/Phase-05-Model-Playground/CURRENT_STATE.md](../../../implementation/Phase-05-Model-Playground/CURRENT_STATE.md)
- [../Phase-01/POST_IMPLEMENTATION_REVIEW.md](../Phase-01/POST_IMPLEMENTATION_REVIEW.md) — "Unexpected Problems" (same tool limitation, documented independently a month earlier)
