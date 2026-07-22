# Workbench — QA

> **Purpose:** Tracks QA work that is deliberately separate from implementation — criteria that need a real device/browser/screen-reader session rather than an automated one, so they don't block Phase 01 sign-off while remaining genuinely open.
> **Scope:** This phase only.
> **Depends on:** [`../../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md`](../../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md) §§4–5, [`../../../implementation/Phase-01-Workbench/CURRENT_STATE.md`](../../../implementation/Phase-01-Workbench/CURRENT_STATE.md)

---

| Ticket | Title | Status |
|---|---|---|
| [QA-0001](QA-0001-drag-performance.md) | Verify Workbench drag performance (60 FPS, React Profiler, no unnecessary renders) | Open |
| [QA-0002](QA-0002-screen-reader-audit.md) | Screen reader audit (NVDA, VoiceOver, keyboard-only) | Open |

Both exist because T16's automated verification pass hit a real limitation of the automated browser tool used (it doesn't service animation frames at all in that session — see `08_ACCEPTANCE.md` §12), not because the underlying app behavior is known to be wrong. Neither blocks Phase 01 sign-off; both must be run and closed out by a human QA pass before Phase 01 is considered fully verified, not merely implemented.
