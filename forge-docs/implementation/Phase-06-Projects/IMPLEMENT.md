# Projects — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in ../../09_CLAUDE_CODE_RULES.md.
> **Ownership:** Project owner (confirmed 2026-08-02)
> **Status:** Complete — implementation finished, tested, QA'd, and documented
> **Last Updated:** 2026-08-03

---


## Role

You are implementing the **Projects** phase of the Forge Development Kit, acting as the engineer of record for this phase. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific detail only.

## Mission

Introduce a cross-feature 'Project' grouping concept so Vault secrets, Notes, and Documents can be organized per project or workspace instead of one flat list each, with an optional per-project default AI provider/model built on the Phase 05 abstraction.

New organizational layer. Touches the existing **Secrets**, **Notes**, and **Documents** data models via an additive, nullable `project_id` foreign key on each — resolved by [ADR-0014](../../decisions/0014-project-data-model-shape.md), not a rewrite of any of them.

## Execution Rules

- [x] [`01_SPEC.md`](01_SPEC.md) and [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) are filled in and confirmed; the user gave explicit go-ahead and implementation is complete.
- [x] Followed [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) — thin routers, `api.ts` as the only endpoint-shape-aware file, no cross-feature imports beyond the explicitly-approved `project-picker.tsx`/`useProviders()` reuse documented in `05_COMPONENTS.md` §1 (precedented by `features/notes/workbench-panel.tsx`).
- [x] `CURRENT_STATE.md` updated to reflect final completion.

## Autonomy Rules

Inherits [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 in full. Phase-specific additions:

- Do not add a new AI provider to `PROVIDER_REGISTRY`, or any new outbound-call code path outside `model_playground.runs.create_run()`, without stopping and asking — this phase's entire AI surface is a thin reference to Phase 05's existing abstraction (per ADR-0014 §2), and any deviation is a blocking architectural decision under `../../09_CLAUDE_CODE_RULES.md` §6.

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
