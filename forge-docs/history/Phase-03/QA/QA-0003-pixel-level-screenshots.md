# QA-0003 — Pixel-level screenshots: dark mode and the <1024px responsive collapse

> **Purpose:** Confirm dark mode and the mobile/tablet responsive collapse actually look correct, visually — this phase's verification of both was structural (computed styles, DOM classes, viewport dimensions), not a real screenshot, because this session's screenshot tool failed outright.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual browser session (real device, visual inspection)
> **Blocks Phase 03 sign-off:** No — see [`../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md`](../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md) Known Issues for why.

---

## Why this is a QA task, not an implementation task

This session's `computer{action:"screenshot"}` tool failed with "Browser pane is not displayed, so the page is not compositing frames" every time it was tried. Dark mode was confirmed via `document.documentElement.className === "dark"`, Monaco's own `vs-dark` theme class, and `getComputedStyle` on decoration spans; the responsive collapse was confirmed via `getBoundingClientRect()`/`getComputedStyle().display` and `document.documentElement.scrollWidth` (no horizontal overflow) at 375px and 768px. These are strong structural signals but not the same as a human looking at the rendered page.

## Scope

The entire `/prompt-studio` page: sidebar, editor, variables panel, body editor, preview panel, version history sheet, diff view.

## What to verify

- [ ] Toggle dark mode; visually confirm no unstyled/white-on-white regions, no illegible text, and the Monaco editor's dark theme matches the rest of the app's dark palette.
- [ ] Resize to 375px (mobile): confirm the sidebar and editor genuinely never overlap or clip, the back button is reachable and visible, and text doesn't overflow its container.
- [ ] Resize to 768px (tablet): same checks.
- [ ] Open the Version History sheet at both the mobile and desktop widths; confirm it renders as a sensible full-screen or partial-width panel without clipping.
- [ ] Confirm the variables panel and preview panel remain usable (not squeezed unreadably) at 375px with several variables declared.

## How to run it

1. Open Prompt Studio in a real browser.
2. Toggle the app's dark mode setting; visually inspect every panel.
3. Use real browser devtools (or a real mobile device) to view at 375px and 768px widths; visually inspect.

## Result

_Not yet run. Fill in with actual screenshots/findings once done._

## Cross-references

- [../../implementation/Phase-03-Prompt-Studio/09_IMPLEMENTATION_TASKS.md](../../implementation/Phase-03-Prompt-Studio/09_IMPLEMENTATION_TASKS.md) — T15 completion note
- [../../implementation/Phase-03-Prompt-Studio/08_ACCEPTANCE.md](../../implementation/Phase-03-Prompt-Studio/08_ACCEPTANCE.md) §2
