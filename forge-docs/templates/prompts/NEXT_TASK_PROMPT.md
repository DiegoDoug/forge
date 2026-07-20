# Prompt Template — Resume After Checkpoint

> **Purpose:** Copy this prompt to resume a Claude Code session using a prior checkpoint's "Recommended Next Prompt" output.
> **Scope:** Mid-phase resumption only. For a brand-new phase kickoff, use [SESSION_START_PROMPT.md](SESSION_START_PROMPT.md) instead.
> **Ownership:** TODO — assign an owner.
> **Status:** Draft
> **Last Updated:** 2026-07-20

---

## Template

```
You are resuming a Claude Code session in the Forge repository.

The previous session ended with this checkpoint (from
forge-docs/history/[checkpoint-file].md):

[paste the "Recommended Next Prompt" and "Remaining Work" sections here]

Before continuing, re-read:
1. forge-docs/implementation/Phase-[NN]-[Name]/CURRENT_STATE.md
2. forge-docs/09_CLAUDE_CODE_RULES.md (in case anything there constrains the
   remaining work)

Then continue with the remaining work listed above, following the same
checkpoint protocol (forge-docs/10_CHECKPOINT_PROTOCOL.md).
```

## TODO

- [ ] TODO: Replace with a real worked example once the first checkpoint exists in [`../../history/`](../../history/README.md).

## Cross-references

- [README.md](README.md)
- [SESSION_START_PROMPT.md](SESSION_START_PROMPT.md)
- [../../history/README.md](../../history/README.md)
