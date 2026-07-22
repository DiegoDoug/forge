# QA-0002 — Dialog Escape-to-close and focus-trap under a real user gesture

> **Purpose:** Confirm `AlertDialog` confirmations (Delete, Restore) trap focus and close on Escape when opened by a real, trusted click — every dialog this phase's automation opened was via a synthetic, untrusted `.click()` call, since ref-based clicks failed on composed Base UI triggers throughout the session.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual browser session (real device/keyboard)
> **Blocks Phase 03 sign-off:** No — see [`../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md`](../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md) Known Issues for why.

---

## Why this is a QA task, not an implementation task

`AlertDialog` (`frontend/components/ui/alert-dialog.tsx`, Base UI) is shared, unmodified code already used by Documents, Secrets, and Project Init — this phase does not implement any custom dialog/focus logic. When this phase's automation opened a dialog via a synthetic `.click()` (necessary because coordinate/ref-based clicks did not register on the `AlertDialogTrigger` composed element in this session's tab), pressing Escape did not close it. A real, trusted user click may behave differently — Base UI's own focus-management effects may depend on the triggering event being trusted. There is no evidence this is a Prompt-Studio-specific defect, only that this session could not verify the trusted-gesture path.

## Scope

Every `AlertDialog` in Prompt Studio: Delete-prompt confirmation and Restore-version confirmation (`frontend/features/prompt-studio/prompt-editor.tsx`, `version-history-sheet.tsx`).

## What to verify

- [ ] Click "Delete" (a real mouse click) on a prompt; confirm the dialog opens with focus moved into it (e.g. onto the Cancel or Delete button).
- [ ] Press Escape; confirm the dialog closes without deleting anything.
- [ ] Re-open it; Tab through — confirm focus stays trapped inside the dialog (doesn't reach the page behind it) and wraps around at the end.
- [ ] Repeat for the Restore-version confirmation dialog in Version History.
- [ ] Confirm focus returns to a sensible element (e.g. the triggering button) after the dialog closes, whether via Escape, Cancel, or completing the action.

## How to run it

1. Open Prompt Studio in a real browser, select a prompt with at least one saved version.
2. Click Delete (or open Version History and click Restore) with a real mouse click.
3. Verify each item above using only the keyboard once the dialog is open.

## Result

_Not yet run. Fill in with actual findings once done._

## Cross-references

- [../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md](../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md) Known Issues
- [../../implementation/Phase-03-Prompt-Studio/08_ACCEPTANCE.md](../../implementation/Phase-03-Prompt-Studio/08_ACCEPTANCE.md) §2
