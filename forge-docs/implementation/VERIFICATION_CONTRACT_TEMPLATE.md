# [Phase Name] — Verification Contract

> **Purpose:** The machine-verifiable contract the Verification Orchestrator operates against for this phase — see [`../15_VERIFICATION_FRAMEWORK.md`](../15_VERIFICATION_FRAMEWORK.md) §5. Fill this in before implementation begins, alongside `01_SPEC.md` through `08_ACCEPTANCE.md`; it draws from them, it doesn't replace them.
> **Scope:** This phase only.
> **Status:** Draft — fill in before implementation begins; keep in sync if the spec changes.
> **Version:** 0.1.0
> **Last Updated:** [date]
> **Depends On:** [01_SPEC.md](01_SPEC.md), [07_TESTING.md](07_TESTING.md), [08_ACCEPTANCE.md](08_ACCEPTANCE.md), [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md), [../15_VERIFICATION_FRAMEWORK.md](../15_VERIFICATION_FRAMEWORK.md)

---

## 1. Phase Metadata

- **Phase name:** [TODO]
- **Phase objective:** [TODO — one or two sentences, copied from `README.md`'s Objective]
- **Dependencies:** [TODO — other phases or systems this phase depends on, from `README.md`'s Dependencies section]
- **Completion definition:** [TODO — copy `README.md`'s Definition of Complete]

## 2. Required Tasks

- [ ] TODO: one line per task in `09_IMPLEMENTATION_TASKS.md`, referenced by task ID (T1, T2, ...) — not restated, just referenced, so this contract can't drift from the actual task list.

## 3. Acceptance Criteria

- [ ] TODO: every criterion from `08_ACCEPTANCE.md` §1–§3, referenced by section/item. No inferred success — each one is independently validated by the Specification Verifier.

## 4. Expected File Scope

- **Expected new/modified files or directories:** [TODO — e.g. `backend/app/services/feature-name/`, `frontend/features/feature-name/`]
- **Explicitly out of scope:** [TODO — files or areas this phase must not touch; the Architecture Verifier reports anything modified outside this list as unexpected]

## 5. Required Validation Commands

- [ ] TODO: lint command(s)
- [ ] TODO: typecheck command(s)
- [ ] TODO: build command(s)
- [ ] TODO: test command(s) (unit, integration — from `07_TESTING.md`)
- [ ] TODO: full-stack command (`docker compose build` / `docker compose up`, if applicable)

## 6. Architecture Constraints

- [ ] TODO: derive from `../../03_ARCHITECTURE.md` §2 invariants that apply to this phase (e.g. no duplicated parser logic, no duplicated services, preserve dependency boundaries, no cross-feature imports).
- [ ] TODO: any phase-specific ADR constraints (e.g. a spec-freeze ADR, if one exists for this phase).

## 7. Documentation Requirements

- [ ] TODO: which docs this phase must update as part of being complete (e.g. `CURRENT_STATE.md`, `10_RELEASE_NOTES.md`, `../../docs/*.md` for shipped-app docs, root FDK docs if this phase changes process).

> **No unresolved conditionals at RC time.** The Documentation Verifier checks only whether a *checked* item's file appears among this run's changed files — it does not, and will not, interpret conditional prose ("if X changes", "when applicable", "unless..."). Every item here must be resolved to an unconditional state before the RC run:
> - If the condition is **true**, rewrite the item as a concrete, unconditional requirement (drop the "if") and satisfy it before RC.
> - If the condition is **false**, leave the item **unchecked** and record the reason inline (e.g. "not required — no documented boundary changed this phase").
> Do not leave a checked item with conditional language still attached — checked means "required and satisfied," not "required if some condition I haven't evaluated holds."
>
> **`02_ROADMAP.md` and `implementation/README.md` are Release-stage items, not RC-stage items** — per [`../13_PHASE_LIFECYCLE.md`](../13_PHASE_LIFECYCLE.md) and [`../15_VERIFICATION_FRAMEWORK.md`](../15_VERIFICATION_FRAMEWORK.md) §4.7, a phase's roadmap/README status can't correctly describe a stage (Released/Frozen) it hasn't reached yet. Leave these **unchecked** here at RC time (with that reason recorded inline) and update them as part of the Released/Frozen-stage process instead — do not check them at RC to reflect an implementation-complete-but-unreleased candidate.

## 8. Regression Targets

- [ ] TODO: existing, previously-shipped functionality this phase must not break — name the specific features/flows (e.g. routing, navigation, an existing converter, shared components, activity logging, an existing API), not just "everything."

## 9. Required Verification Agents

- [ ] Specification
- [ ] Architecture
- [ ] Build
- [ ] Test
- [ ] Regression
- [ ] Code Quality
- [ ] Documentation
- [ ] UX — [TODO: required / not required — required only if this phase changes user-visible functionality, per [`../15_VERIFICATION_FRAMEWORK.md`](../15_VERIFICATION_FRAMEWORK.md) §4.8]

## 10. TODO

- [ ] This document is a template placeholder — fill in against `01_SPEC.md` and `08_ACCEPTANCE.md` before implementation begins, and keep it in sync as the spec evolves.

## 11. Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../15_VERIFICATION_FRAMEWORK.md](../15_VERIFICATION_FRAMEWORK.md)
- [../12_BUG_CLASSIFICATION.md](../12_BUG_CLASSIFICATION.md)
