# Model Playground — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in ../../09_CLAUDE_CODE_RULES.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Not authorized — 01_SPEC.md and 08_ACCEPTANCE.md are still template placeholders
> **Last Updated:** 2026-07-20

---


## Role

You are implementing the **Model Playground** phase of the Forge Development Kit, acting as the engineer of record for this phase. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific detail only.

## Mission

Provide a UI for testing and comparing LLM provider/model outputs side by side, with configurable API keys per provider.

New capability — the first Forge feature with first-class outbound LLM provider calls as its core purpose (Ingest's vision-LLM path is optional/secondary by comparison).

## Execution Rules

- [ ] Do not begin any task in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) until [`01_SPEC.md`](01_SPEC.md) and [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) are filled in and confirmed (currently template placeholders — this phase is **not yet authorized**).
- [ ] Follow [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) exactly — thin routers, `api.ts` as the only endpoint-shape-aware file, no cross-feature imports.
- [ ] Update [`CURRENT_STATE.md`](CURRENT_STATE.md) as work progresses, not only at checkpoints.

## Autonomy Rules

Inherits [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 in full. Phase-specific additions:

- [ ] TODO: note anything this phase needs to ask about beyond the repo-wide defaults (e.g. Phase 05 Model Playground and Phase 03 Prompt Studio must always ask before enabling a new outbound LLM provider integration by default).

## Quality Gates

Every task must clear [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) task-level checklist before being marked complete in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).

## Testing Rules

Follow [`07_TESTING.md`](07_TESTING.md) in full. No task is complete with failing or skipped tests.

## Checkpoint Rules

Follow [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) exactly:

- [ ] Checkpoint after every 10–12 completed tasks.
- [ ] Checkpoint at ~70% context usage.
- [ ] Checkpoint at every milestone completion (see [`README.md`](README.md) Milestones).
- [ ] Checkpoint immediately on any blocking architectural decision — draft it with [`../../decisions/ADR_TEMPLATE.md`](../../decisions/ADR_TEMPLATE.md) and stop for approval.
- [ ] Log every checkpoint to [`../../history/`](../../history/README.md).

## Definition of Done

This phase is done when [`README.md`](README.md) §"Definition of Complete" is fully satisfied.

## Stop Criteria

Stop immediately and do not proceed on assumption when:

- [ ] A checkpoint trigger from [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1 is hit.
- [ ] A task has no corresponding filled-in spec section.
- [ ] A decision would violate a principle in [`../../01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) or an invariant in [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2.
- [ ] Any global session safety rule (destructive git ops, external communication, credentials) would otherwise be triggered.

## Resume Criteria

A fresh session may resume this phase once it has read, in order: [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md), this file, [`CURRENT_STATE.md`](CURRENT_STATE.md), and the most recent entry in [`../../history/README.md`](../../history/README.md) if one exists.

## Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
