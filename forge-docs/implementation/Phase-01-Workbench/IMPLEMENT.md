# Workbench — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in ../../09_CLAUDE_CODE_RULES.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** AUTHORIZED — specification LOCKED per [ADR-0009](../../decisions/0009-phase-specification-freeze.md); implementation approved to begin
> **Version:** 0.2.0
> **Last Updated:** 2026-07-20
> **Depends On:** [README.md](README.md), [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md), [../../decisions/0009-phase-specification-freeze.md](../../decisions/0009-phase-specification-freeze.md)
> **Supersedes:** v0.1.0 of this document (not authorized; no milestone/checkpoint structure; no priority-order rule)

---

## Role

You are implementing the **Workbench** phase of the Forge Development Kit, acting as the engineer of record for this phase. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific detail only.

## Mission

Give Forge a configurable home workspace — the **Workbench** — that surfaces pinned tools, recent activity across every feature, and quick actions.

Fully replaces the former **Dashboard** feature (`frontend/features/dashboard`, `backend/app/services/dashboard.py`) — per [ADR-0001](../../decisions/0001-workbench-replaces-dashboard.md), this is a full replacement, not an evolution that keeps both concepts. Workbench renders panels conforming to the `WorkbenchPanel` interface ([`12_PANEL_INTERFACE.md`](12_PANEL_INTERFACE.md)) rather than a fixed set of hardcoded widgets ([ADR-0002](../../decisions/0002-workbench-panel-architecture.md)).

## Specification Freeze — read this before touching anything else

Per [ADR-0009](../../decisions/0009-phase-specification-freeze.md), `01_SPEC.md` through `08_ACCEPTANCE.md` and `12_PANEL_INTERFACE.md` are **locked**. During this implementation:

**Allowed without stopping:** bug fixes, clarifications of genuinely ambiguous spec text, typo/cross-reference corrections.

**Not allowed — defer to `../../research/future-features/` or `../../02_ROADMAP.md` instead of building it:** any new feature, any architectural change, any scope expansion. The project owner named these explicitly as out of bounds for this phase: extra panels beyond the five in `01_SPEC.md` §3, workflows, a command palette beyond the `/search` page, a capability registry, a Projects interface, a plugin system, and AI-related additions of any kind. If a task seems to need one of these to be "done properly," stop and flag it — don't build a smaller version of it as a workaround.

**Exceptions** (per ADR-0009 §3): security bugs, build failures, specification errors, and critical usability defects (not "could be nicer" — genuinely unusable) may be fixed even though they touch locked spec content. Note what you changed and why in `CURRENT_STATE.md`.

## Priority Order — immutable, applies to every decision during implementation

1. **Correctness**
2. **Existing functionality** (nothing already shipped in Forge regresses)
3. **Stability**
4. **Performance**
5. **UX polish**
6. **New functionality**

**Never sacrifice a higher priority to improve a lower one.** Concretely: never break an existing feature (2) in service of a Workbench polish detail (5). If a task in `09_IMPLEMENTATION_TASKS.md` would require trading a higher priority for a lower one, stop and flag it rather than making the trade silently.

## Milestone Plan

Per [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md), work proceeds in four milestones, each ending in a checkpoint — do not treat the 16 tasks as one continuous run:

```
Milestone 1 — Foundation (T1–T4)
  Secrets compatibility migration, /search page, workbench_layout migration, panel contract
  ↓ Checkpoint
Milestone 2 — Backend (T5–T8)
  Layout persistence service, workbench aggregation, API routes, backend tests
  ↓ Checkpoint
Milestone 3 — Frontend (T9–T12)
  Workbench runtime shell, pin picker, the five active panels, drag/keyboard reorder + states
  ↓ Checkpoint
Milestone 4 — Integration (T13–T16)
  Nav rename, old Dashboard removal, manual verification, accessibility scan
  ↓ Final Validation against 08_ACCEPTANCE.md
```

Milestone boundaries are checkpoint triggers **in addition to**, not instead of, the standard 10–12 task / ~70% context triggers in [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1 — whichever comes first. A milestone boundary gives a cleaner recovery point (e.g. "Backend is done and tested" is a more useful resume point than "task 7 of 16"), so prefer stopping there even if the task-count threshold hasn't strictly been hit yet.

## Execution Rules

- [ ] Do not begin any task in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) out of milestone order — see "Milestone Plan" above and the ordering notes in that document §2.
- [ ] Follow [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) exactly — thin routers, `api.ts` as the only endpoint-shape-aware file, no cross-feature imports.
- [ ] Update [`CURRENT_STATE.md`](CURRENT_STATE.md) as work progresses, not only at checkpoints.
- [ ] Respect the Specification Freeze and Priority Order above on every task, not just as a one-time read.

## Autonomy Rules

Inherits [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 in full. Phase-specific additions:

- [ ] Any of the six named out-of-bounds items in "Specification Freeze" above, even if small, requires stopping and asking — this is a standing "must ask first," not case-by-case judgment.
- [ ] The Vault → Secrets compatibility migration (T1) touches a shipped, in-use feature — if the safe-rename check for the database table (per `04_DATABASE.md` §1) is ambiguous, ask rather than guessing at what counts as "risky."

## Quality Gates

Every task must clear [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) task-level checklist before being marked complete in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).

## Testing Rules

Follow [`07_TESTING.md`](07_TESTING.md) in full. No task is complete with failing or skipped tests.

## Checkpoint Rules

Follow [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) exactly, with the milestone boundaries above as additional trigger points:

- [ ] Checkpoint after every milestone (T4, T8, T12, T16).
- [ ] Checkpoint after every 10–12 completed tasks, whichever comes first.
- [ ] Checkpoint at ~70% context usage.
- [ ] Checkpoint immediately on any blocking architectural decision — draft it with [`../../decisions/ADR_TEMPLATE.md`](../../decisions/ADR_TEMPLATE.md) and stop for approval. Given the Specification Freeze above, a "blocking architectural decision" during this phase almost always means "this belongs in the backlog, not in Phase 01" — treat that as the default read before assuming a new ADR is needed.
- [ ] Log every checkpoint to [`../../history/`](../../history/README.md).

## Definition of Done

This phase is done when [`README.md`](README.md) §"Definition of Complete" and §"Definition of Success" are both fully satisfied.

## Stop Criteria

Stop immediately and do not proceed on assumption when:

- [ ] A checkpoint trigger (milestone boundary, task count, or context threshold) is hit.
- [ ] A task has no corresponding filled-in spec section.
- [ ] A decision would violate a principle in [`../../01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) or an invariant in [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2.
- [ ] A decision would violate the Specification Freeze or the Priority Order above.
- [ ] Any global session safety rule (destructive git ops, external communication, credentials) would otherwise be triggered.

## Resume Criteria

A fresh session may resume this phase once it has read, in order: [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md), this file, [`CURRENT_STATE.md`](CURRENT_STATE.md), and the most recent entry in [`../../history/README.md`](../../history/README.md) if one exists.

## Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../decisions/0009-phase-specification-freeze.md](../../decisions/0009-phase-specification-freeze.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
