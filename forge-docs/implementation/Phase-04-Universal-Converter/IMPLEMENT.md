# Universal Converter — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in ../../09_CLAUDE_CODE_RULES.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** **Implementation complete.** All seven milestones (T1–T21) done and approved, including Milestone 7's RC audit (T18–T21, with the T20a–e audit-scope expansion the project owner added 2026-07-25). Zero open BLOCKERs. The only remaining step is the project owner's formal Sign-off decision (per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md)) — not an implementation task.
> **Last Updated:** 2026-07-25

---


## Role

You are implementing the **Universal Converter** phase of the Forge Development Kit, acting as the engineer of record for this phase. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific detail only.

## Mission

Unify the existing Converters and Ingest feature areas into one universal format-conversion surface spanning text formats (JSON/YAML/XML/CSV/Markdown) and document formats (Office/PDF/images).

Consolidates the existing **Converters** (`frontend/features/converters`, `backend/app/converters`) and **Ingest** (`frontend/features/ingest`, `backend/app/ingest`) feature areas.

## Execution Rules

- [x] [`01_SPEC.md`](01_SPEC.md), [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md), and [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md)'s seven-milestone breakdown are filled in and **approved by the project owner (2026-07-23)** — this phase is authorized, starting from Milestone 1 / T1–T3.
- [ ] Follow [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) exactly — thin routers, `api.ts` as the only endpoint-shape-aware file, no cross-feature imports.
- [ ] Update [`CURRENT_STATE.md`](CURRENT_STATE.md) as work progresses, not only at checkpoints.
- [ ] **No milestone may introduce both an architectural change and a behavioral change simultaneously, unless the milestone's own stated objective in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) explicitly requires both** — a rule established by the project owner (2026-07-23) for this phase's implementation. "Architectural change" means introducing or modifying a structural abstraction (an interface, a registry, a module boundary). "Behavioral change" means altering what the system does for an input/endpoint/page that already existed, or exposing a wholly new capability to a caller. Concretely, under this rule: Milestone 2 must add the `ConverterProvider` protocol/registry with **zero** wiring to real behavior (proven only against a throwaway fake provider); Milestone 4's frontend manifest must not be consumed by any live page yet. Milestones 3 and 5 are the two milestones whose *stated objective* explicitly pairs an architectural change with a behavioral one (wiring the real provider + shipping the new endpoint; composing the unified page + shipping the redirect/nav change, respectively) — that pairing is the explicit exception the rule allows for those two milestones specifically, not a license to pair changes elsewhere. If implementation of any milestone surfaces a need to pair changes beyond what its stated objective already covers, stop and ask before proceeding, per the Stop Criteria below.
- [ ] **Review cadence (project owner, 2026-07-23):** a project-owner review happens at every milestone boundary (Milestone 1 → review → Milestone 2 → review → ... → Milestone 6 → review → Milestone 7 Release Candidate audit), not only at the end of the phase. Do not begin the next milestone's tasks until the current milestone's acceptance criteria (its slice of [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md)) are validated and the owner has reviewed.

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
- [ ] Checkpoint at every milestone completion (see [`README.md`](README.md) Milestones) — this checkpoint **is** the project-owner review gate per the cadence in Execution Rules above; do not start the next milestone's tasks before it.
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
