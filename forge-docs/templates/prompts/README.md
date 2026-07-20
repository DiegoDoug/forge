# Prompt Templates

> **Purpose:** Canonical, copy-pasteable prompts for the recurring session types this FDK produces, so a human never has to hand-write a session-kickoff or resume prompt from scratch.
> **Scope:** Prompt text templates only. The rules those prompts must satisfy live in [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) and [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md).
> **Ownership:** TODO — assign an owner.
> **Status:** Draft
> **Last Updated:** 2026-07-20

---

## 1. Available templates

| Template | Use when |
|---|---|
| [SESSION_START_PROMPT.md](SESSION_START_PROMPT.md) | Kicking off a fresh Claude Code session against a specific phase |
| [NEXT_TASK_PROMPT.md](NEXT_TASK_PROMPT.md) | Resuming after a checkpoint, using its "Recommended Next Prompt" output |

## 2. TODO

- [ ] TODO: Add a "phase kickoff" prompt template once Phase 01 provides a real worked example.
- [ ] TODO: Add a "blocking decision escalation" prompt template for the scenario in [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §6.

## 3. Cross-references

- [../README.md](../README.md)
- [../../../.claude/SESSION_TEMPLATE.md](../../../.claude/SESSION_TEMPLATE.md)
