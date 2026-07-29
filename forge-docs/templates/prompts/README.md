# Prompt Templates

> **Purpose:** Canonical, copy-pasteable prompts for the recurring session types this FDK produces, so a human never has to hand-write a session-kickoff or resume prompt from scratch.
> **Scope:** Prompt text templates only. The rules those prompts must satisfy live in [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) and [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md).
> **Ownership:** TODO — assign an owner.
> **Status:** Draft
> **Version:** 0.1.0
> **Last Updated:** 2026-07-25
> **Depends On:** [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md), [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
> **Supersedes:** —

---

## 1. Available templates

| Template | Use when |
|---|---|
| [SESSION_START_PROMPT.md](SESSION_START_PROMPT.md) | Kicking off a fresh Claude Code session against a specific phase |
| [NEXT_TASK_PROMPT.md](NEXT_TASK_PROMPT.md) | Resuming after a checkpoint, using its "Recommended Next Prompt" output |
| [VERIFICATION_FRAMEWORK_KICKOFF_PROMPT.md](VERIFICATION_FRAMEWORK_KICKOFF_PROMPT.md) | One-time session to introduce the FDK Verification Framework (ADR-0010, `15_VERIFICATION_FRAMEWORK.md`, contract template, doc updates) |
| [VERIFICATION_IMPLEMENTATION_KICKOFF_PROMPT.md](VERIFICATION_IMPLEMENTATION_KICKOFF_PROMPT.md) | Operationalizing the Verification Framework: verifier subagents, orchestrator, repair loop, and FDK integration, across 4 gated milestones |

## 2. TODO

- [ ] TODO: Add a "blocking decision escalation" prompt template for the scenario in [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §6.

## 3. Cross-references

- [../README.md](../README.md)
- [../../../.claude/SESSION_TEMPLATE.md](../../../.claude/SESSION_TEMPLATE.md)
