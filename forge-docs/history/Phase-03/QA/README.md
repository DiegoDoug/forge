# Prompt Studio — QA

> **Purpose:** Tracks QA work that is deliberately separate from implementation — items that need a real device/browser/keyboard session rather than an automated one, so they don't block Phase 03 sign-off while remaining genuinely open.
> **Scope:** This phase only.
> **Depends on:** [`../../implementation/Phase-03-Prompt-Studio/08_ACCEPTANCE.md`](../../implementation/Phase-03-Prompt-Studio/08_ACCEPTANCE.md), [`../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md`](../../implementation/Phase-03-Prompt-Studio/CURRENT_STATE.md)

---

| Ticket | Title | Status |
|---|---|---|
| [QA-0001](QA-0001-monaco-keyboard-input.md) | Real keyboard typing into the Monaco body editor | Open |
| [QA-0002](QA-0002-dialog-focus-behavior.md) | Dialog Escape-to-close and focus-trap under a real user gesture | Open |
| [QA-0003](QA-0003-pixel-level-screenshots.md) | Pixel-level screenshots: dark mode and the &lt;1024px responsive collapse | Open |
| [QA-0004](QA-0004-copy-success-toast.md) | Copy action's success-path toast confirmation | Open |
| [QA-0005](QA-0005-high-dpi-scaling.md) | High-DPI display scaling | Open |

All five exist because this phase's automated browser-automation tool ran in a tab that structurally could not composite frames or service `requestAnimationFrame` (confirmed directly — the screenshot tool itself failed with "Browser pane is not displayed, so the page is not compositing frames", and Monaco's own layout had to be fixed with a `setTimeout`-scheduled `editor.layout()` specifically because `requestAnimationFrame` never fired in that tab). None of these are known-wrong app behavior — each was either code-reviewed correct, or partially confirmed (e.g. the Copy action's *error* path was confirmed working live; only the *success* path's toast couldn't be triggered). None blocks Phase 03 sign-off; each must be run and closed out by a human QA pass before Phase 03 is considered fully verified, not merely implemented.
