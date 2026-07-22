# Project Initialization Engine — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in ../../09_CLAUDE_CODE_RULES.md.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Implementation complete (T1–T14 done, Definition of Done satisfied — see CURRENT_STATE.md). Next per 13_PHASE_LIFECYCLE.md: Release Candidate audit, then Owner Sign-off.
> **Last Updated:** 2026-07-22

---


## Role

You are implementing the **Project Initialization Engine** phase of the Forge Development Kit, acting as the engineer of record for this phase. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific detail only.

## Mission

Build a scaffolding engine that generates new structured project layouts from templates — starting with generating new FDK-style phase folders within Forge itself.

New capability. Consumes and extends [`forge-docs/templates/project-initialization/`](../../templates/project-initialization/README.md).

## Execution Rules

- [x] [`01_SPEC.md`](01_SPEC.md) and [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) are filled in and confirmed — this phase is authorized.
- [x] Followed [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) exactly — thin routers, `api.ts` as the only endpoint-shape-aware file, no cross-feature imports.
- [x] Updated [`CURRENT_STATE.md`](CURRENT_STATE.md) at every checkpoint.

## Autonomy Rules

Inherits [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 in full. Phase-specific additions:

- This phase introduces no LLM provider or outbound network call of any kind (pure template rendering) — the "ask before enabling a new outbound LLM provider" concern that applies to Phase 03/05 does not apply here.
- No new external dependency is introduced (stdlib `string.Template` + `zipfile` only) — nothing to ask about under [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3's "adding a new external dependency" gate.

## Quality Gates

Every task must clear [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) task-level checklist before being marked complete in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).

## Testing Rules

Follow [`07_TESTING.md`](07_TESTING.md) in full. No task is complete with failing or skipped tests.

## Checkpoint Rules

Follow [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) exactly:

- [x] Checkpoint after every 10–12 completed tasks.
- [x] Checkpoint at ~70% context usage (n/a — phase completed before this threshold).
- [x] Checkpoint at every milestone completion (see [`README.md`](README.md) Milestones) — Milestone 1 and Milestones 2–3 both checkpointed.
- [x] No blocking architectural decision arose (n/a).
- [x] Every checkpoint logged to [`../../history/`](../../history/README.md).

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
