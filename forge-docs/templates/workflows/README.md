# Workflow Templates

> **Purpose:** Hold reusable multi-agent workflow patterns (for the `Workflow` tool) specific to this repository — e.g. a standard "review a phase's implementation" fan-out, or a standard "migrate a feature" pipeline.
> **Scope:** Workflow *script patterns and when-to-use guidance*, not one-off scripts for a single task — those are run directly, not stored here.
> **Ownership:** TODO — assign an owner.
> **Status:** Empty — no repo-specific workflow patterns captured yet
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
> **Supersedes:** —

---

## 1. Candidate workflows (not yet written)

- [ ] TODO: A "phase readiness review" workflow — fans out across a phase's `01_SPEC.md` through `08_ACCEPTANCE.md` to check completeness before `IMPLEMENT.md` is authorized (ties into [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §1).
- [ ] TODO: A "cross-phase consistency audit" workflow — checks that consolidation phases (04 Universal Converter, 07 Knowledge Hub, 08 Developer Toolkit) don't duplicate logic already in the features they're consolidating.

## 2. Usage note

Workflow orchestration (the `Workflow` tool) is only invoked when the user explicitly opts in — see this session's own tool-use rules. This folder documents *patterns*, worth reaching for once opted in; it does not itself trigger orchestration.

## 3. Cross-references

- [../README.md](../README.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
