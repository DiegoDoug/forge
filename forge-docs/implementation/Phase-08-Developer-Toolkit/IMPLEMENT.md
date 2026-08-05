# Developer Toolkit — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in ../../09_CLAUDE_CODE_RULES.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** **Approved to begin — 2026-08-05.** Two distinct gates were cleared, in order, and both are recorded here deliberately because they are not the same thing:
>
> 1. **Specification approved in principle (2026-08-05)** — scope, route, navigation identity, top-level tab architecture, Utilities frontend-only conclusion, no-backend-abstraction decision, and ten-task shape. All [`01_SPEC.md`](01_SPEC.md) §7 open questions resolved; three requested corrections (FR1 wording, FR6 wording, T2/T3 atomicity) applied and consistency-checked across all eleven documents.
> 2. **Implementation authorization granted (2026-08-05)** — a separate, explicit act by the project owner, following their review of the corrected document set. Specification approval alone never constituted this authorization, and a future phase should not treat it as such.
>
> Per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md), this phase has therefore moved from **Specification** to **Authorized**, and is now in **Implementation**. Scope is locked to the approved specification — see Execution Rules below.
> **Last Updated:** 2026-08-05

---


## Role

You are implementing the **Developer Toolkit** phase of the Forge Development Kit, acting as the engineer of record for this phase. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific detail only.

## Mission

Consolidate Generators, Crypto, and Utilities under one unified Developer Toolkit page and nav entry, without changing any of their underlying service logic — see [`01_SPEC.md`](01_SPEC.md) §1 for the full, repository-grounded scope statement.

This is a smaller-shaped phase than its closest precedent, Universal Converter (Phase 04): no new backend abstraction, no schema change, no new endpoint. See [`03_BACKEND.md`](03_BACKEND.md) and [`04_DATABASE.md`](04_DATABASE.md).

## Execution Rules

- [x] Do not begin any task in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) until this document's Status line above reads "Approved to begin". **Satisfied 2026-08-05** — implementation authorization granted as a separate act from specification approval.
- [ ] **Scope is locked** to the approved specification. No addition beyond `01_SPEC.md` §3's nine functional requirements; no change to anything `01_SPEC.md` §5 places out of scope. Do not modify an existing feature implementation merely to make composition easier — if a component resists composition, that is a finding to report, not a license to edit it.
- [ ] **T2 and T3 must land as one atomic change.** `/generators`, `/crypto`, and `/utilities` must never resolve to a 404 at any commit on this branch — see [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) §1's T2+T3 entry.
- [ ] Follow [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) exactly — thin routers, `api.ts` as the only endpoint-shape-aware file, no cross-feature imports. (Largely inherited unmodified in this phase, since no router or `api.ts` is touched — see [`03_BACKEND.md`](03_BACKEND.md) §1, [`05_COMPONENTS.md`](05_COMPONENTS.md) §3.)
- [ ] Update [`CURRENT_STATE.md`](CURRENT_STATE.md) as work progresses, not only at checkpoints.
- [ ] Every component composed into the new unified page (T1 in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md)) must be **imported, not copied or rewritten** — a diff that duplicates a Generators/Crypto/Utilities component's source instead of importing it is out of contract for this phase. This is the counterpart to [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) FR6: importing and composing those components is expected and permitted; editing their internals is not.

## Autonomy Rules

Inherits [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 in full. Phase-specific additions:

- [ ] None beyond the repo-wide defaults — this phase introduces no new outbound network call, no new provider/API-key concept, and no schema change, so none of the additional-ask triggers other phases (Model Playground, Prompt Studio) carry apply here.

## Quality Gates

Every task must clear [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) task-level checklist before being marked complete in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).

## Testing Rules

Follow [`07_TESTING.md`](07_TESTING.md) in full. No task is complete with failing or skipped tests. Note [`07_TESTING.md`](07_TESTING.md) §2: the absence of a frontend test framework is a pre-existing, repository-wide gap, not something this phase's tasks are expected to fix.

## Checkpoint Rules

Follow [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) exactly:

- [ ] Checkpoint after every 10–12 completed tasks — this phase's entire proposed task list (T1–T10) fits within one such checkpoint window; treat completion of T10 as the phase's single milestone checkpoint.
- [ ] Checkpoint at ~70% context usage.
- [ ] Checkpoint at every milestone completion (see [`README.md`](README.md) Milestones).
- [ ] Checkpoint immediately on any blocking architectural decision — draft it with [`../../decisions/ADR_TEMPLATE.md`](../../decisions/ADR_TEMPLATE.md) and stop for approval. (None anticipated — see [`CURRENT_STATE.md`](CURRENT_STATE.md) Architectural Decisions.)
- [ ] Log every checkpoint to [`../../history/`](../../history/README.md).

## Definition of Done

This phase is done when [`README.md`](README.md) §"Definition of Complete" is fully satisfied.

## Stop Criteria

Stop immediately and do not proceed on assumption when:

- [ ] A checkpoint trigger from [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1 is hit.
- [ ] A task has no corresponding filled-in spec section.
- [ ] A decision would violate a principle in [`../../01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) or an invariant in [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2.
- [ ] Any global session safety rule (destructive git ops, external communication, credentials) would otherwise be triggered.
- [ ] Any of [`01_SPEC.md`](01_SPEC.md) §7's open questions turn out to be load-bearing for a task about to start, and haven't been resolved yet.

## Resume Criteria

A fresh session may resume this phase once it has read, in order: [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md), this file, [`CURRENT_STATE.md`](CURRENT_STATE.md), and the most recent entry in [`../../history/README.md`](../../history/README.md) if one exists.

## Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
