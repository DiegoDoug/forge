# Checkpoint History

> **Purpose:** Durable, append-only log of every checkpoint produced under [10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md), so state survives even after a phase's `CURRENT_STATE.md` is overwritten by its next update.
> **Scope:** Checkpoint records only. Architectural decisions belong in [`../decisions/`](../decisions/README.md), not here.
> **Ownership:** TODO — assign an owner.
> **Status:** Empty — no checkpoints logged yet
> **Last Updated:** 2026-07-20

---

## 1. How to add an entry

At every checkpoint (per [`../10_CHECKPOINT_PROTOCOL.md`](../10_CHECKPOINT_PROTOCOL.md) §3):

1. Copy [`CHECKPOINT_LOG_TEMPLATE.md`](CHECKPOINT_LOG_TEMPLATE.md) to `YYYY-MM-DD-phase-NN-short-desc.md` in this folder.
2. Fill it in with the checkpoint's full required output (Completed Tasks, Modified Files, Current State, Remaining Work, Recommended Next Prompt, Known Risks).
3. Add a row to the index below.

## 2. Index

| Date | Phase | Trigger | File |
|------|-------|---------|------|
| _(none yet)_ | | | |

## 3. TODO

- [ ] TODO: Log the first checkpoint once Phase 01 work begins.

## 4. Cross-references

- [CHECKPOINT_LOG_TEMPLATE.md](CHECKPOINT_LOG_TEMPLATE.md)
- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../../.claude/CHECKPOINT_TEMPLATE.md](../../.claude/CHECKPOINT_TEMPLATE.md)
