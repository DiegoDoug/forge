# 08 — Definition of Done

> **Purpose:** The single checklist that decides whether a task, feature, or phase is actually finished — not "mostly working."
> **Scope:** Applies to every implementation task under `implementation/Phase-*/09_IMPLEMENTATION_TASKS.md` and every checkpoint in [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md).
> **Ownership:** TODO — assign an engineering owner.
> **Status:** Draft
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md)
> **Supersedes:** —

---

## 1. Task-level Definition of Done

A single implementation task is done only when **all** of the following hold:

- [ ] Code compiles/builds with no new errors or warnings introduced.
- [ ] Relevant tests (unit and/or integration per [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md) §4) pass locally.
- [ ] No `TODO` left in shipped code without a corresponding tracked entry in the relevant phase's `CURRENT_STATE.md` "Known Issues" section.
- [ ] The change matches the spec in the phase's `01_SPEC.md` — or the spec was updated first if reality diverged.
- [ ] UI changes reviewed against [04_UI_GUIDELINES.md](04_UI_GUIDELINES.md) (empty/loading/error states, keyboard access, dark mode).
- [ ] Backend changes respect the architectural invariants in [03_ARCHITECTURE.md](03_ARCHITECTURE.md) (thin routers, schema migrations, no cross-feature imports).
- [ ] Documentation touched where behavior changed (`../docs/*.md` for shipped-app docs, the phase's own docs for in-progress work).

## 2. Feature-level Definition of Done

A feature (a full phase, or a major slice of one) is done only when, in addition to every task within it meeting §1:

- [ ] The phase's `08_ACCEPTANCE.md` criteria are all checked off.
- [ ] `CURRENT_STATE.md` reflects reality (no stale "In Progress" items for work that shipped).
- [ ] Known Issues are either resolved or explicitly deferred with a reason (honest gaps, per [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md) §1.3) — never silently dropped.
- [ ] A checkpoint has been produced per [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md).

## 3. Explicitly NOT Done (common false positives)

- ❌ "It works on my machine" without the test suite passing.
- ❌ UI implemented without an empty/error/loading state.
- ❌ A stub that looks complete but silently no-ops on the hard part (see the PGP precedent — track it, don't hide it).
- ❌ A schema change made directly against the database without an Alembic migration.
- ❌ A checkpoint skipped because "it was a small change" when the task-count or context threshold in [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md) was already hit.

## 4. TODO

- [ ] TODO: Define measurable test-coverage thresholds, if any, once frontend testing tooling is chosen (see [06_TECH_STACK.md](06_TECH_STACK.md) §5).
- [ ] TODO: Define a security-review gate for phases that introduce outbound network calls (Model Playground, Prompt Studio) — likely an addendum here plus updates to `../docs/Security.md`.

## 5. Cross-references

- [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md)
- [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md)
- [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)
- [implementation/](implementation/) — each phase's `08_ACCEPTANCE.md` and `09_IMPLEMENTATION_TASKS.md`
