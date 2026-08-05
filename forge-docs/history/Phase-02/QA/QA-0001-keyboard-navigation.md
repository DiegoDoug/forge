# QA-0001 — Keyboard-only Tab-sequence walkthrough

> **Purpose:** Close out the one criterion in [`../../../implementation/Phase-02-Project-Initialization-Engine/08_ACCEPTANCE.md`](../../../implementation/Phase-02-Project-Initialization-Engine/08_ACCEPTANCE.md) §2 the implementation session left explicitly unchecked.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual Browser Session (not automatable in this repo's current toolchain — no frontend test runner exists per [`../../../implementation/Phase-02-Project-Initialization-Engine/07_TESTING.md`](../../../implementation/Phase-02-Project-Initialization-Engine/07_TESTING.md))
> **Blocks Phase 02 sign-off:** No — already ruled non-blocking at Release Candidate, see [`../../../implementation/Phase-02-Project-Initialization-Engine/RC1_AUDIT.md`](../../../implementation/Phase-02-Project-Initialization-Engine/RC1_AUDIT.md) §4.3 item 1.

---

## Why this is a QA task, not an implementation task

The implementation session's manual browser tool cannot reliably drive a genuine Tab-key sequence — it does not support interactive input capture in a way that distinguishes a real trusted keyboard event from a synthetic one. No automated re-attempt in that same tool would produce a more meaningful result; this needs a human at a real keyboard.

## Scope

The entire `/project-init` page: the kind picker, the FDK Phase Scaffold form, the AI Project Instructions form, the file preview disclosure, and every history-row action (re-download, delete + confirmation dialog).

## What to verify (from `08_ACCEPTANCE.md` §2)

- [ ] Tab from page load reaches the kind picker (`<button role="radio">` pair) in a sensible order, and Space/Enter/arrow keys select a kind per native radio-group conventions.
- [ ] Once a kind is selected, Tab continues into that kind's form fields in visual/logical order (FDK Phase: phase number → phase name → objective; AI Instructions: project name → description → tech stack → conventions → output-files checklist).
- [ ] The file-preview `Accordion` disclosure is reachable and toggleable via keyboard (Enter/Space) without a mouse.
- [ ] "Generate & Download" is reachable and activatable via keyboard, and its `disabled` state (on an invalid form) is honored — no Enter-key submission should succeed on an invalid form.
- [ ] In the history list, each row's re-download and delete actions are reachable via Tab; the delete confirmation `AlertDialog` traps focus while open and returns focus to a sensible element (ideally the triggering row) on close/cancel.
- [ ] No keyboard trap anywhere on the page — Tab (and Shift+Tab) can always move both forward and backward through every interactive element without getting stuck.

## Why this is expected to pass

Every component involved is an accessible-by-construction primitive already proven correct elsewhere in the app: native `<button role="radio">` for the kind picker, `<Label htmlFor>` associations on every form field, and the shared shadcn `Accordion`/`AlertDialog` primitives used unmodified by Documents, Secrets, and (later) Prompt Studio. This is a confirmation pass, not a from-scratch investigation — see [`../../../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md`](../../../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md) Known Issues for the original honest gap this ticket closes.

## How to run it

1. Open `/project-init` in a real browser tab, mouse untouched from page load.
2. Tab through the entire page top to bottom, narrating (or recording) which element has focus at each step.
3. Repeat once per kind (FDK Phase Scaffold, AI Project Instructions), and once more with at least one prior generation present in history (to exercise the history-row actions and the delete confirmation dialog).

## Result

_Not yet run. Fill in with actual findings and a pass/fail once done._

## Cross-references

- [../../../implementation/Phase-02-Project-Initialization-Engine/08_ACCEPTANCE.md](../../../implementation/Phase-02-Project-Initialization-Engine/08_ACCEPTANCE.md) §2
- [../../../implementation/Phase-02-Project-Initialization-Engine/RC1_AUDIT.md](../../../implementation/Phase-02-Project-Initialization-Engine/RC1_AUDIT.md) §4.3
- [../../../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md](../../../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md)
