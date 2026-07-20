# 09 — Claude Code Rules

> **Purpose:** The execution contract every Claude Code session operating in this repository must follow. This is the document a session should read first.
> **Scope:** How Claude Code should read this documentation system, what it may do autonomously, and what requires a stop-and-ask. Per-phase execution contracts live in each phase's `IMPLEMENT.md` and inherit from this document.
> **Ownership:** TODO — assign an owner (recommended: whoever directs Claude Code sessions day-to-day).
> **Status:** Draft
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md), [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)
> **Supersedes:** —

---

## 1. Read order for a new session

1. This document.
2. [02_ROADMAP.md](02_ROADMAP.md) — confirm which phase is currently active.
3. The active phase's `README.md` and `CURRENT_STATE.md` under `implementation/Phase-XX-*/`.
4. The active phase's `IMPLEMENT.md` — the actual execution contract for that phase.
5. Only then begin work.

Do not begin implementation work against a phase whose `01_SPEC.md` and `08_ACCEPTANCE.md` are still template placeholders (`[ ] TODO` only, no filled-in content) — that phase is not yet authorized. Flag this to the user instead of guessing.

## 2. Documentation-first rule

No code is written before the relevant spec exists. If a task is requested that has no corresponding spec section:

1. Stop.
2. Draft the missing spec section (or a proposed addition) first.
3. Get it confirmed (explicitly, or implicitly via the user proceeding after seeing it) before writing implementation code.

This mirrors [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md) §1.8.

## 3. Autonomy rules

**May do without asking:**
- Implement tasks already fully specified in an active phase's `09_IMPLEMENTATION_TASKS.md`.
- Write/update tests for code being changed in the same task.
- Update a phase's `CURRENT_STATE.md` as work progresses.
- Fix a bug in code being actively touched, if it's clearly in-scope and low-risk.

**Must ask first:**
- Anything listed as "Prohibited" or "Explicit permission required" under this session's top-level safety rules (destructive git operations, sending messages, publishing content, etc. — those rules are global and take precedence over everything in this file).
- Adding a new external dependency not already listed in [06_TECH_STACK.md](06_TECH_STACK.md).
- Any schema change that isn't a straightforward additive migration.
- Any decision that would need an entry in [`decisions/README.md`](decisions/README.md) — architectural exceptions, new cross-cutting systems, anything violating a principle in [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md).
- Starting a phase whose dependencies (per its `README.md` Dependencies section) aren't marked complete.

## 4. Quality gates

Every task must clear [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md) before being marked complete. Do not mark a task done in `09_IMPLEMENTATION_TASKS.md` if tests are failing or the implementation is partial.

## 5. Checkpoint discipline

Follow [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md) exactly — checkpoint at the thresholds it defines, and produce the exact output format it specifies. Do not skip a checkpoint because "it's almost done" — the whole point is that state is recoverable if the session ends unexpectedly.

## 6. Blocking architectural decisions

If a task requires a decision that isn't already settled in [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md) or [03_ARCHITECTURE.md](03_ARCHITECTURE.md):

1. Stop implementation.
2. Draft the decision as a candidate entry using [`decisions/ADR_TEMPLATE.md`](decisions/ADR_TEMPLATE.md).
3. Present it to the user as a checkpoint item ("blocking architectural decision requires approval" — see [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)).
4. Do not proceed on an assumption.

## 7. Relationship to this session's global safety rules

This document governs *project-specific* workflow (what order to read docs, when to checkpoint, which phase is active). It never overrides the global safety rules governing destructive actions, external communication, or credential handling — those apply regardless of what this file says.

## 8. TODO

- [ ] TODO: Once Phase 01 is underway, capture real examples of "blocking architectural decision" moments here to replace the hypothetical guidance above.
- [ ] TODO: Decide whether phase `IMPLEMENT.md` contracts may ever loosen these rules (recommendation: no — they may only add phase-specific detail).

## 9. Cross-references

- [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)
- [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md)
- [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md)
- [decisions/ADR_TEMPLATE.md](decisions/ADR_TEMPLATE.md)
- [../.claude/SESSION_TEMPLATE.md](../.claude/SESSION_TEMPLATE.md)
- [implementation/](implementation/) — each phase's `IMPLEMENT.md`
