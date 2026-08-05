# QA-0002 — Pixel-level screenshots: dark mode and the 375px mobile viewport

> **Purpose:** Confirm dark mode and the 375px mobile layout actually look correct, visually — this phase's own verification of both was structural (accessibility tree, computed disabled-state checks), not a real screenshot, because the implementation session's screenshot tool was unavailable.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual browser session (real device or real browser tab, visual inspection)
> **Blocks Phase 02 sign-off:** No — already ruled non-blocking at Release Candidate, see [`../../../implementation/Phase-02-Project-Initialization-Engine/RC1_AUDIT.md`](../../../implementation/Phase-02-Project-Initialization-Engine/RC1_AUDIT.md) §4.3 item 2.

---

## Why this is a QA task, not an implementation task

The implementation session's `computer{action:"screenshot"}` tool was unavailable ("not displayed, so the page is not compositing frames" per [`../../../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md`](../../../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md) Known Issues). Dark mode and the 375px viewport were confirmed structurally instead — accessibility-tree inspection and computed-state checks using the same semantic Tailwind tokens and responsive utility classes already proven visually correct elsewhere in the app. That is a strong signal, not a substitute for a human actually looking at the rendered page.

## Scope

The entire `/project-init` page: kind picker, both forms (FDK Phase Scaffold, AI Project Instructions), the file-preview disclosure, and the history list with its row actions and delete-confirmation dialog.

## What to verify

- [ ] Toggle dark mode; visually confirm no unstyled/white-on-white regions, no illegible text, and every form field, badge, and button reads correctly against the dark background.
- [ ] Resize to 375×812 (mobile): confirm the kind picker, form fields, file-preview accordion, and history list never overlap or clip, and no control requires horizontal scrolling to reach.
- [ ] At 375px, open the delete-confirmation `AlertDialog`; confirm it renders as a legible, non-clipped dialog at that width.
- [ ] At 375px with dark mode also toggled (both together), repeat a spot check of the above — combined states sometimes surface issues neither does alone.

## How to run it

1. Open `/project-init` in a real browser.
2. Toggle the app's dark mode setting; visually inspect every screen/state (kind picker, both forms, preview, history list, delete dialog).
3. Use real browser devtools (or a real mobile device) to view at 375px width; visually inspect the same set of screens/states.
4. Combine both (dark mode + 375px) for a final spot check.

## Result

_Not yet run. Fill in with actual screenshots/findings once done._

## Cross-references

- [../../../implementation/Phase-02-Project-Initialization-Engine/08_ACCEPTANCE.md](../../../implementation/Phase-02-Project-Initialization-Engine/08_ACCEPTANCE.md) §2
- [../../../implementation/Phase-02-Project-Initialization-Engine/RC1_AUDIT.md](../../../implementation/Phase-02-Project-Initialization-Engine/RC1_AUDIT.md) §4.3
- [../../../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md](../../../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md)
