# 10 — Checkpoint Protocol

> **Purpose:** Define exactly when a Claude Code session must pause and produce a checkpoint, and the exact shape that checkpoint must take, so work is always recoverable.
> **Scope:** Applies to every phase's implementation work. Referenced by every phase's `IMPLEMENT.md`.
> **Ownership:** TODO — assign an owner.
> **Status:** Draft
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md)
> **Supersedes:** —

---

## 1. Stop conditions

A checkpoint is triggered — and **only** triggered — by one of these four conditions:

- [ ] **Task volume:** 10–12 implementation tasks from a phase's `09_IMPLEMENTATION_TASKS.md` have been completed since the last checkpoint.
- [ ] **Context usage:** Conversation context usage is approximately 70% or higher.
- [ ] **Milestone completion:** A milestone listed in the active phase's `README.md` has just finished.
- [ ] **Blocking architectural decision:** A decision requiring approval has come up (per [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md) §6).

Do not checkpoint more eagerly than this — frequent, low-content checkpoints are as unhelpful as none. Do not checkpoint less eagerly than this — running past a stop condition risks losing unrecoverable context.

## 2. Required checkpoint output

Every checkpoint, regardless of which condition triggered it, must produce exactly these sections, in this order:

```markdown
## Checkpoint — [Phase name] — [date]

### Completed Tasks
- [list of tasks completed since the last checkpoint, referencing 09_IMPLEMENTATION_TASKS.md IDs]

### Modified Files
- [list of every file created or changed since the last checkpoint]

### Current State
- [what the system does right now, in plain terms — what a fresh session would need to know]

### Remaining Work
- [what's left in the current phase/milestone, pulled from 09_IMPLEMENTATION_TASKS.md]

### Recommended Next Prompt
- [a single, copy-pasteable prompt the user can hand to the next session to resume exactly where this one left off]

### Known Risks
- [anything uncertain, deferred, or that could break — including any Known Issues carried into CURRENT_STATE.md]
```

## 3. What to update at every checkpoint

- [ ] The active phase's `CURRENT_STATE.md` — all ten sections (Current Status, Completed, In Progress, Remaining, Known Issues, Architectural Decisions, Modified Files, Next Milestone, Next Claude Prompt, Session Notes).
- [ ] The active phase's `09_IMPLEMENTATION_TASKS.md` — checked-off tasks marked complete.
- [ ] A new entry in [`history/`](history/) using [`history/CHECKPOINT_LOG_TEMPLATE.md`](history/CHECKPOINT_LOG_TEMPLATE.md), so the checkpoint is preserved even after `CURRENT_STATE.md` is overwritten by the next one.

## 4. Blocking-decision checkpoints specifically

When the trigger is a blocking architectural decision, the checkpoint's "Known Risks" section must include the drafted decision (using [`decisions/ADR_TEMPLATE.md`](decisions/ADR_TEMPLATE.md)) and the checkpoint must end with an explicit question to the user rather than a "Recommended Next Prompt" that assumes an answer.

## 5. TODO

- [ ] TODO: Once a few real checkpoints exist in `history/`, review whether the 10–12 task window is too tight or too loose for this repo's actual task granularity.
- [ ] TODO: Decide whether checkpoints should be committed to git automatically or left for the user to commit.

## 6. Cross-references

- [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md)
- [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md)
- [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md) — triage matrix + RC/merge-criteria workflow for closing out a phase
- [history/README.md](history/README.md)
- [decisions/ADR_TEMPLATE.md](decisions/ADR_TEMPLATE.md)
- [../.claude/CHECKPOINT_TEMPLATE.md](../.claude/CHECKPOINT_TEMPLATE.md)
- [implementation/](implementation/) — each phase's `IMPLEMENT.md` Checkpoint Rules section
