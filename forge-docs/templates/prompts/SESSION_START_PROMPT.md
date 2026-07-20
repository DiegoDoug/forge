# Prompt Template — Session Start

> **Purpose:** Copy this prompt (filling in the bracketed values) to start a new Claude Code session against a specific FDK phase.
> **Scope:** Phase-kickoff sessions only. For resuming mid-phase, use [NEXT_TASK_PROMPT.md](NEXT_TASK_PROMPT.md) instead.
> **Ownership:** TODO — assign an owner.
> **Status:** Draft
> **Last Updated:** 2026-07-20

---

## Template

```
You are working in the Forge repository as a Claude Code session.

Read, in order:
1. forge-docs/09_CLAUDE_CODE_RULES.md
2. forge-docs/implementation/Phase-[NN]-[Name]/README.md
3. forge-docs/implementation/Phase-[NN]-[Name]/CURRENT_STATE.md
4. forge-docs/implementation/Phase-[NN]-[Name]/IMPLEMENT.md

Then begin work on: [specific task or "the next unchecked item in 09_IMPLEMENTATION_TASKS.md"].

Follow the checkpoint protocol in forge-docs/10_CHECKPOINT_PROTOCOL.md exactly —
stop and produce a checkpoint at its defined thresholds, not before and not after.

Do not begin implementation if 01_SPEC.md or 08_ACCEPTANCE.md for this phase
are still unfilled templates — flag that instead and stop.
```

## TODO

- [ ] TODO: Replace the bracketed placeholders with a real worked example after Phase 01's first session.

## Cross-references

- [README.md](README.md)
- [NEXT_TASK_PROMPT.md](NEXT_TASK_PROMPT.md)
