# QA-0004 — Copy action's success-path toast confirmation

> **Purpose:** Confirm the Preview panel's Copy button shows its success toast ("Copied rendered prompt to clipboard.") on a real click in a real, focused browser tab.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual browser session
> **Blocks Phase 03 sign-off:** No — see [`../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md`](../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md) Known Issues for why.

---

## Why this is a QA task, not an implementation task

`navigator.clipboard.writeText` requires the document to have focus (`document.hasFocus()`); this session's automation tab reported `document.hasFocus() === false`, so every Copy attempt hit the *error* path rather than the success path — which is exactly how a real defect was found and fixed here: `handleCopy` originally had no error handling at all, so a clipboard failure failed completely silently. The error path (`"Couldn't copy to clipboard."` toast) was confirmed working live. The success path (`"Copied rendered prompt to clipboard."` toast) is code-reviewed correct but was never actually triggered in this session, since the tab was never in a state where the clipboard write could succeed.

## Scope

`frontend/features/prompt-studio/preview-panel.tsx`'s `handleCopy`.

## What to verify

- [ ] In a real, focused browser tab, fill in a prompt's preview variables and click "Copy".
- [ ] Confirm a success toast reading "Copied rendered prompt to clipboard." appears.
- [ ] Paste from the clipboard somewhere (e.g. a text field) and confirm the pasted text matches exactly what the Preview panel was showing.
- [ ] Click Copy again immediately; confirm the toast reappears (not suppressed by toast-deduplication) and the "Copy" button's icon briefly shows a checkmark before reverting.

## How to run it

1. Open Prompt Studio in a real browser, select or create a prompt with at least one variable.
2. Fill in the preview value(s), click Copy, and verify each item above.

## Result

_Not yet run. Fill in with actual findings once done._

## Cross-references

- [../../implementation/Phase-03-Prompt-Studio/08_ACCEPTANCE.md](../../implementation/Phase-03-Prompt-Studio/08_ACCEPTANCE.md) §1 (criterion 7)
- [../../implementation/Phase-03-Prompt-Studio/09_IMPLEMENTATION_TASKS.md](../../implementation/Phase-03-Prompt-Studio/09_IMPLEMENTATION_TASKS.md) — T17 completion note (the Copy error-handling fix)
