# Checkpoint History

> **Purpose:** Durable, append-only log of every checkpoint produced under [10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md), so state survives even after a phase's `CURRENT_STATE.md` is overwritten by its next update. Also holds each frozen phase's archived end-of-phase artifacts (`Phase-NN/`) — see §2.1.
> **Scope:** Checkpoint records and frozen-phase archives. Architectural decisions belong in [`../decisions/`](../decisions/README.md), not here.
> **Ownership:** TODO — assign an owner.
> **Status:** 3 checkpoints logged (Phase 01, Milestones 1–3); Phase 01's post-freeze archive (`Phase-01/`) added
> **Version:** 0.3.0
> **Last Updated:** 2026-07-21
> **Depends On:** [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md), [../13_PHASE_LIFECYCLE.md](../13_PHASE_LIFECYCLE.md)
> **Supersedes:** —

---

## 1. How to add a checkpoint entry

At every checkpoint (per [`../10_CHECKPOINT_PROTOCOL.md`](../10_CHECKPOINT_PROTOCOL.md) §3):

1. Copy [`CHECKPOINT_LOG_TEMPLATE.md`](CHECKPOINT_LOG_TEMPLATE.md) to `YYYY-MM-DD-phase-NN-short-desc.md` in this folder.
2. Fill it in with the checkpoint's full required output (Completed Tasks, Modified Files, Current State, Remaining Work, Recommended Next Prompt, Known Risks).
3. Add a row to the index below.

## 2. Index

| Date | Phase | Trigger | File |
|------|-------|---------|------|
| 2026-07-21 | Phase-01-Workbench | Milestone completion (Milestone 1 — Foundation, T1–T4) | [2026-07-21-phase-01-milestone-1-foundation.md](2026-07-21-phase-01-milestone-1-foundation.md) |
| 2026-07-21 | Phase-01-Workbench | Milestone completion (Milestone 2 — Backend, T5–T8) | [2026-07-21-phase-01-milestone-2-backend.md](2026-07-21-phase-01-milestone-2-backend.md) |
| 2026-07-21 | Phase-01-Workbench | Milestone completion (Milestone 3 — Frontend, T9–T12) | [2026-07-21-phase-01-milestone-3-frontend.md](2026-07-21-phase-01-milestone-3-frontend.md) |

## 2.1 Frozen-phase archives

Per [`../13_PHASE_LIFECYCLE.md`](../13_PHASE_LIFECYCLE.md) §5, once a phase reaches **Frozen**, its end-of-phase artifacts (`10_RELEASE_NOTES.md`, `POST_IMPLEMENTATION_REVIEW.md`, `QA/`, `BUGS/`) move here, into `Phase-NN/`, out of the active `implementation/Phase-NN-Name/` folder.

| Phase | Folder | Released as |
|---|---|---|
| 01 — Workbench | [Phase-01/](Phase-01/) | `v0.1.0-workbench` |

## 3. TODO

- [ ] TODO: none currently open.

## 4. Cross-references

- [CHECKPOINT_LOG_TEMPLATE.md](CHECKPOINT_LOG_TEMPLATE.md)
- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../13_PHASE_LIFECYCLE.md](../13_PHASE_LIFECYCLE.md)
- [../../.claude/CHECKPOINT_TEMPLATE.md](../../.claude/CHECKPOINT_TEMPLATE.md)
