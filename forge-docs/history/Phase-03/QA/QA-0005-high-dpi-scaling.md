# QA-0005 — High-DPI display scaling

> **Purpose:** Confirm Prompt Studio (particularly the Monaco editor and its `${...}` decorations) renders crisply on a high-DPI/Retina display.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual browser session (real high-DPI display)
> **Blocks Phase 03 sign-off:** No — not testable without real display hardware; not a pre-existing `08_ACCEPTANCE.md` criterion, but explicitly requested by the project owner to stay tracked during the T15 QA pass.

---

## Why this is a QA task, not an implementation task

There is no way to simulate real physical pixel density from this session's browser-automation environment. This is a request for coverage beyond what was originally specified, not a criterion this phase's spec ever committed to — tracked honestly as a gap rather than silently ignored.

## Scope

The entire `/prompt-studio` page, with particular attention to the Monaco editor (which does its own internal canvas/DOM rendering and historically has had DPI-scaling quirks in some browser/OS combinations) and the diff view.

## What to verify

- [ ] On a 2x (Retina) or higher display, confirm all text — including inside the Monaco editor — renders sharply, not blurred or doubled.
- [ ] Confirm icons (lucide-react) and the variable-declaration decoration underlines/colors remain crisp.
- [ ] Confirm no layout is visibly off (e.g. 1px gaps or misaligned borders that only appear at certain DPI scale factors).

## How to run it

1. Open Prompt Studio on a real high-DPI display (e.g. a modern MacBook's Retina screen, or a Windows machine with display scaling set above 100%).
2. Visually inspect the items above, in both light and dark mode.

## Result

_Not yet run. Fill in with actual findings once done._

## Cross-references

- [../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md](../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md) Known Issues
