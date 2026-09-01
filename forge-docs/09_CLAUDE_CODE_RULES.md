# 09 — Claude Code Rules

> **Purpose:** The execution contract every Claude Code session operating in this repository must follow. This is the document a session should read first.
> **Scope:** How Claude Code should read this documentation system, what it may do autonomously, and what requires a stop-and-ask. Per-phase execution contracts live in each phase's `IMPLEMENT.md` and inherit from this document.
> **Ownership:** TODO — assign an owner (recommended: whoever directs Claude Code sessions day-to-day).
> **Status:** Draft
> **Version:** 0.3.0
> **Last Updated:** 2026-08-20
> **Depends On:** [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md), [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md), [15_VERIFICATION_FRAMEWORK.md](15_VERIFICATION_FRAMEWORK.md)
> **Supersedes:** —

---

## 1. Read order for a new session

1. This document.
2. [02_ROADMAP.md](02_ROADMAP.md) — confirm which phase is currently active.
3. The active phase's `README.md` and `CURRENT_STATE.md` under `implementation/Phase-XX-*/`.
4. The active phase's `IMPLEMENT.md` — the actual execution contract for that phase.
5. If the session is completing a phase's implementation or evaluating whether to continue to the next phase, [15_VERIFICATION_FRAMEWORK.md](15_VERIFICATION_FRAMEWORK.md) — the phases it applies to (Phase 05 onward) also need the active phase's `VERIFICATION_CONTRACT.md`.
6. Only then begin work.

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
- For phases with a `VERIFICATION_CONTRACT.md` (Phase 05 onward), run the Verification Framework after implementation completes, and — on a PASS result — continue directly into the next phase's implementation without waiting for confirmation of that specific transition. This is a narrow, ADR-0010-authorized exception to this session's normal confirm-before-proceeding posture; it does not extend to anything in "Must ask first" below, and it never authorizes release actions (tag/merge/push) on its own — see [15_VERIFICATION_FRAMEWORK.md](15_VERIFICATION_FRAMEWORK.md) §1.

**Must ask first:**
- Anything listed as "Prohibited" or "Explicit permission required" under this session's top-level safety rules (destructive git operations, sending messages, publishing content, etc. — those rules are global and take precedence over everything in this file).
- Adding a new external dependency not already listed in [06_TECH_STACK.md](06_TECH_STACK.md).
- Any schema change that isn't a straightforward additive migration.
- Any decision that would need an entry in [`decisions/README.md`](decisions/README.md) — architectural exceptions, new cross-cutting systems, anything violating a principle in [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md).
- Starting a phase whose dependencies (per its `README.md` Dependencies section) aren't marked complete.
- **Deleting or resetting any local database/data directory or Docker named volume** (`backend/.dev-data*`, `forge-data`/`<project>_forge-data`, or equivalent) that this session did not itself create earlier in the same task — even one that looks empty, unused, or disposable-by-convention. See §3.1 below for why this is a hard rule, not a judgment call.

### 3.1 Local dev-state and Docker volumes are never assumed disposable

**Found the hard way during Phase 11, Milestone 5 (2026-08-20):** a session preparing a live-verification run deleted `backend/.dev-data/` to get a clean state, without first checking whether it held real accumulated data. It happened to survive (the file was locked by a still-running process, and its actual contents turned out to be a single empty note from Phase 01) — but the reasoning that led to attempting the deletion was wrong, not merely lucky: "it's a gitignored `.dev-data*` directory, other sibling directories with similar names are clearly disposable verification sandboxes, so this one probably is too." That inference does not hold. A directory being gitignored means it isn't *tracked*, not that it isn't *real* — the operator's own months of manual cross-phase testing lives in exactly this kind of directory, and "looks like scratch space" is not the same as "confirmed to be scratch space."

**The rule, going forward:**
1. Never delete, truncate, or reset a local database file, data directory, or Docker named volume unless this session created it earlier in the same task (e.g., an isolated verification sandbox this session itself just spun up and will itself tear down).
2. Before touching anything else that looks like it might be dev/test state — a `.dev-data*` directory, a Docker volume, a `docker ps -a`/`docker volume ls` result predating this session — inspect it first (row counts, file timestamps, `docker inspect`) and form an actual conclusion about whether it holds real accumulated state, rather than inferring disposability from a naming convention or directory location.
3. When a task needs a clean environment (a fresh DB, an empty volume) and an existing one is in the way, default to creating a **new, separately-named** one (a different `FORGE_DATA_DIR`, a different Docker Compose project name via `-p`) instead of clearing the existing one — this is strictly safer and was, in fact, the approach that correctly protected the pre-existing `forge`-named Docker Compose project/volume later in that same Milestone 5 session, once the lesson had already been learned the hard way with the plain directory.
4. If a reset of existing state is genuinely necessary (not just convenient), stop and ask — this falls under "Must ask first" above, not "may do without asking."

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

- [15_VERIFICATION_FRAMEWORK.md](15_VERIFICATION_FRAMEWORK.md) — the automated phase-transition audit referenced in §1 and §3
- [decisions/0010-fdk-verification-automation-exception.md](decisions/0010-fdk-verification-automation-exception.md) — the ADR authorizing §3's verification-continuation exception
- [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)
- [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md)
- [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md)
- [decisions/ADR_TEMPLATE.md](decisions/ADR_TEMPLATE.md)
- [../.claude/SESSION_TEMPLATE.md](../.claude/SESSION_TEMPLATE.md)
- [implementation/](implementation/) — each phase's `IMPLEMENT.md`
