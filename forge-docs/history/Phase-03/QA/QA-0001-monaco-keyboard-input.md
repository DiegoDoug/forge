# QA-0001 — Real keyboard typing into the Monaco body editor

> **Purpose:** Confirm a real human, on a real keyboard, can type directly into the prompt body editor — this session's automation could only drive Monaco via its own public model API (`editor.getModel().setValue(...)`), never via actual key events.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual browser session (real device/keyboard)
> **Blocks Phase 03 sign-off:** No — see [`../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md`](../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md) Known Issues for why.

---

## Why this is a QA task, not an implementation task

Confirmed directly during this phase's own manual verification: `computer.type`/`computer.key` (the automation tool's synthetic input dispatch) worked correctly against plain `<input>` elements throughout the same session, but produced no change at all — not even to the raw textarea value — when targeted at Monaco's hidden input, even after explicitly focusing it via `element.focus()`. This is consistent with the tab's broader compositing limitation (see the QA folder [`README.md`](README.md)), not a defect in `PromptBodyEditor` — the component's `onChange` wiring was independently confirmed correct by setting the model's value via Monaco's own API and observing the rest of the UI (undeclared-variable detection, dirty-state Save/Discard, live preview) react correctly every time.

## Scope

`frontend/features/prompt-studio/prompt-body-editor.tsx` — the Monaco-based body editor on `/prompt-studio`.

## What to verify

- [ ] Click into the body editor and type a prompt body containing a `${variable}` placeholder using a real keyboard — confirm the text appears as typed, with no dropped/duplicated characters.
- [ ] Confirm the declared-vs-undeclared `${...}` decoration highlighting updates live as you type (green for declared, red/underlined for undeclared) without needing to blur the field or trigger a re-render some other way.
- [ ] Confirm standard editing operations work: undo/redo (Ctrl+Z/Ctrl+Y), select-all, cut/copy/paste, multi-line editing, word-wrap behavior at the editor's actual rendered width.
- [ ] Confirm typing a very long single line (well past 20,000 characters) doesn't freeze or visibly stutter the editor before the app's own length-limit warning kicks in.

## How to run it

1. Open Prompt Studio in a real browser (not an automation session) on a desktop, create or open a prompt.
2. Click into the Body editor and type normally.
3. Verify each item above.

## Result

_Not yet run. Fill in with actual findings once done._

## Cross-references

- [../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md](../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md) Known Issues
- [../../implementation/Phase-03-Prompt-Studio/09_IMPLEMENTATION_TASKS.md](../../implementation/Phase-03-Prompt-Studio/09_IMPLEMENTATION_TASKS.md) — T15 completion note (the Monaco `automaticLayout` bug this same limitation helped surface)
