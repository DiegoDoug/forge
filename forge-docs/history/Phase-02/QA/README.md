# Project Initialization Engine — QA

> **Purpose:** Tracks QA work that is deliberately separate from implementation — criteria that need a real device/browser/keyboard session rather than an automated one, so they don't block Phase 02 sign-off while remaining genuinely open.
> **Scope:** This phase only.
> **Depends on:** [`../../../implementation/Phase-02-Project-Initialization-Engine/08_ACCEPTANCE.md`](../../../implementation/Phase-02-Project-Initialization-Engine/08_ACCEPTANCE.md) §2, [`../../../implementation/Phase-02-Project-Initialization-Engine/RC1_AUDIT.md`](../../../implementation/Phase-02-Project-Initialization-Engine/RC1_AUDIT.md) §4.3, [`../../../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md`](../../../implementation/Phase-02-Project-Initialization-Engine/CURRENT_STATE.md)

---

| Ticket | Title | Status |
|---|---|---|
| [QA-0001](QA-0001-keyboard-navigation.md) | Keyboard-only Tab-sequence walkthrough (kind picker, both forms, history actions) | Open |
| [QA-0002](QA-0002-pixel-level-screenshots.md) | Pixel-level screenshots: dark mode and the 375px mobile viewport | Open |

Both exist because the implementation session's environment lacked a real interactive input/rendering surface: the Browser pane's screenshot tool errored ("not displayed, so the page is not compositing frames"), and no Tab-key-sequence walkthrough was performed against a genuine trusted user gesture. Both were code-reviewed/structurally verified as correct (accessible-by-construction primitives; existing, already dark-mode-correct Tailwind tokens) and both `RC1_AUDIT.md` §4.3 and `08_ACCEPTANCE.md` §2 recommended filing them as QA tickets rather than treating them as failures. Neither blocks Phase 02's Released & Frozen status, per `12_BUG_CLASSIFICATION.md` §4 — they were ruled non-blocking at RC and remain non-blocking now; both must still be run and closed out by a human QA pass before Phase 02 is considered fully verified, not merely implemented.

**Filed retroactively on 2026-08-05**, two weeks after RC1_AUDIT.md (2026-07-22) first recommended them — see [`../../2026-08-05-phase-02-freeze-checkpoint.md`](../../2026-08-05-phase-02-freeze-checkpoint.md) Known Risks for why they weren't filed at release time.
