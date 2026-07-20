# Checkpoint History

> **Purpose:** Durable, append-only log of every checkpoint produced under [10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md), so state survives even after a phase's `CURRENT_STATE.md` is overwritten by its next update.
> **Scope:** Checkpoint records only. Architectural decisions belong in [`../decisions/`](../decisions/README.md), not here.
> **Ownership:** TODO — assign an owner.
> **Status:** One checkpoint logged
> **Version:** 0.2.0
> **Last Updated:** 2026-07-21
> **Depends On:** [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
> **Supersedes:** —

---

## 1. How to add an entry

At every checkpoint (per [`../10_CHECKPOINT_PROTOCOL.md`](../10_CHECKPOINT_PROTOCOL.md) §3):

1. Copy [`CHECKPOINT_LOG_TEMPLATE.md`](CHECKPOINT_LOG_TEMPLATE.md) to `YYYY-MM-DD-phase-NN-short-desc.md` in this folder.
2. Fill it in with the checkpoint's full required output (Completed Tasks, Modified Files, Current State, Remaining Work, Recommended Next Prompt, Known Risks).
3. Add a row to the index below.

## 2. Index

| Date | Phase | Trigger | File |
|------|-------|---------|------|
| 2026-07-21 | Phase-01-Workbench | Milestone completion (Milestone 1 — Foundation, T1–T4) | [2026-07-21-phase-01-milestone-1-foundation.md](2026-07-21-phase-01-milestone-1-foundation.md) |

## 3. TODO

- [ ] TODO: none — first checkpoint logged.

## 4. Cross-references

- [CHECKPOINT_LOG_TEMPLATE.md](CHECKPOINT_LOG_TEMPLATE.md)
- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../../.claude/CHECKPOINT_TEMPLATE.md](../../.claude/CHECKPOINT_TEMPLATE.md)
