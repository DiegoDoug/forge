# Claude MCP / Second Brain — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md).
> **Ownership:** Project owner.
> **Status:** ✅ **Milestone 1 complete and checkpointed — 2026-08-18. Milestone 2 NOT authorized.**
>
> Three gates recorded, in order, as separate, explicit acts — none implies the next, exactly as the planning package's own §17 required and as Phase 09's precedent established:
>
> 1. **Architecture direction approved (2026-08-18)** — the owner reviewed the full planning package (`01_SPEC.md` through `09_IMPLEMENTATION_TASKS.md`) and approved the architecture direction (Option A: in-process MCP server; bearer-token auth model), after requesting and receiving six amendments (bootstrap-token/persistent-token lifecycle, transactional/existence-checked delete, `forge_context` N+1 and project-scoping fixes, activity-log dedup, mandatory `get_note` service method — see `CURRENT_STATE.md` §4 for the full list).
> 2. **Milestone 1 implementation authorized (2026-08-18)** — granted explicitly, scoped to Milestone 1 **only**. The owner's own words: *"I would authorize Milestone 1 only. ... Then the new Agentic Review verifier gets its first real test."*
> 3. **Milestone 1 checkpointed, PASS (2026-08-18)** — mechanical verification 8/8, Agentic Review PASS after one repair cycle (a real BLOCKER found and fixed — see [`reviews/AGENTIC_REVIEW_M1.md`](reviews/AGENTIC_REVIEW_M1.md)). Full record: [`../../history/2026-08-18-phase-11-milestone-1-checkpoint.md`](../../history/2026-08-18-phase-11-milestone-1-checkpoint.md). **This is a checkpoint, not a release, freeze, or Milestone 2 authorization.**
>
> **⛔ Milestone 2 authorization is a separate, future, fourth gate — not implied by gate 3.** Nothing in this document authorizes any Milestone 2 task (M2-T0 through M2-T6). Milestone 2 introduces write/delete authority over real persistent knowledge for the first time, a materially different risk profile than Milestone 1's transport/auth foundation, and per the owner's explicit instruction is not to be rushed on the strength of Milestone 1's pass. When granted, record it here as gate 4, dated separately, the same way gates 1–3 are recorded above — never by editing the Status line without an explicit owner act behind it.
>
> [ADR-0018](../../decisions/0018-mcp-server-integrated-not-separate-process.md) and [ADR-0019](../../decisions/0019-mcp-bearer-token-authentication.md) are **Accepted** as of this review.
> **Last Updated:** 2026-08-18

---

## Role

You are implementing **Milestone 1 (MCP Foundation) of Phase 11 — Claude MCP / Second Brain**, acting as the engineer of record. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific and milestone-specific detail only.

## Mission

Prove the narrow vertical slice defined in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md)'s Milestone 1 section — transport, auth, scope enforcement, and MCP handshake — with **zero Notes/Documents/Projects CRUD tools**. This is deliberately the smallest possible end-to-end proof, so a transport/auth defect cannot hide behind a CRUD-tool bug. See `01_SPEC.md` §1, §3, §4 for the architecture this milestone stands up.

## Read order for a session working this milestone

1. [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md)
2. **This document**
3. [`CURRENT_STATE.md`](CURRENT_STATE.md) — the amendment history and current status
4. [`01_SPEC.md`](01_SPEC.md) §1, §3, §4, §7 — architecture, transport, auth, ADRs
5. [`03_BACKEND.md`](03_BACKEND.md) §1–§4 — package layout, auth dependencies, config
6. [`06_API.md`](06_API.md) §4a — the token-provisioning route (the only REST surface in this milestone)
7. [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) — Milestone 1's task table and gate criteria
8. [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §1 — the acceptance criteria this milestone must satisfy
9. [`VERIFICATION_CONTRACT.md`](VERIFICATION_CONTRACT.md) before declaring the milestone done

## Execution Rules

- [ ] **Scope is locked to Milestone 1's task table in `09_IMPLEMENTATION_TASKS.md`.** M1-T1 through M1-T9, and nothing from Milestone 2 onward. `forge_get_note`, any other tool, any tool registry with a non-empty tool list — all out of scope for this milestone, however small the addition might seem.
- [ ] **Zero MCP tools registered in this milestone.** The `/mcp` handshake must succeed and `tools/list` must return an empty (or correctly-shaped, zero-length) list. Registering even one tool "to make the milestone feel more complete" is scope creep and must not happen.
- [ ] **The bootstrap token must never be accepted by `/mcp`.** This is the single most important security property of this milestone — test it explicitly (AC1a), don't just implement it and assume.
- [ ] **`AuthDep`/`require_auth` and every existing `/api/*` route are untouched.** `git diff --stat` against any file under `api/routes/` other than the new `mcp_tokens.py` must be empty.
- [ ] **No Secrets/Settings/Crypto import anywhere under `app/mcp/` or `app/services/mcp/`.** Verified by AC10-equivalent static check even though Milestone 1 has no read/write tools yet — the import boundary should be correct from the first line of code, not retrofitted in Milestone 2.
- [ ] **Follow [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) exactly** — thin routers, logic in `services/`, models are schema source of truth, every schema change is an explicit Alembic migration.
- [ ] **The new `mcp` PyPI dependency is the only new external dependency this milestone introduces.** Record it in `06_TECH_STACK.md` per `03_ARCHITECTURE.md`'s "Integration points for new phases" checklist.
- [ ] Update `CURRENT_STATE.md` as work progresses.

## Autonomy Rules

Inherits [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 in full. Milestone-specific additions:

**Must ask first, beyond the repo-wide triggers:**
- [ ] Starting any Milestone 2 task, for any reason, including "it was faster to do while I was already in this file."
- [ ] Any deviation from the bootstrap/persistent-token model in `01_SPEC.md` §4.3.
- [ ] Any change to `AuthDep`, `require_auth`, or any existing `/api/*` route's dependency list.
- [ ] Declaring the milestone complete without an Agentic Review PASS (see Quality Gates below) — this is not a judgment call, it's a hard gate per the owner's explicit instruction.

**May do without asking:**
- [ ] Implement any task in Milestone 1's table exactly as specified in `01_SPEC.md`/`03_BACKEND.md`/`06_API.md`.
- [ ] Adapt the FastAPI-`Depends`-shaped pseudocode in `03_BACKEND.md` §3 to the MCP SDK's actual ASGI-app shape, provided the enforcement guarantee is preserved and the deviation is documented (see `01_SPEC.md`/ADR-0019 §4's implementation note — this adaptation is already pre-approved, not a new decision).
- [ ] Write and run tests for code being touched.
- [ ] Fix a low-risk in-scope bug discovered while implementing a Milestone 1 task.

## Quality Gates

Every task clears [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) before being marked complete.

**Milestone completion requires, in order:**
1. Every M1-T1..T9 task in `09_IMPLEMENTATION_TASKS.md` complete.
2. The complete mechanical verification contract run (`VERIFICATION_CONTRACT.md`, Milestone 1 section) — Specification, Architecture, Build, Test, Regression, Code Quality, Documentation verifiers, plus whatever `§5 Required Validation Commands` are declared.
3. The independent **Agentic Review** gate (`09_IMPLEMENTATION_TASKS.md` §0 and Milestone 1's gate criteria) invoked and returning **PASS**. Not self-declared by the implementing session — see `09_IMPLEMENTATION_TASKS.md` §0 for how this review is structured to be independent.
4. If the Agentic Review returns FAIL or PASS WITH REQUIRED FIXES: repair **only Milestone 1 scope**, then re-run the review. Do not expand scope to "fix it properly by also doing part of Milestone 2."
5. On PASS: stop. Update `CURRENT_STATE.md` to record the PASS and the milestone-complete status. **Do not release, merge, tag, freeze, or begin Milestone 2** without a separate, explicit owner authorization act.

## The specific ways this milestone can go wrong

1. **Scope creep toward "while I'm here."** The token-provisioning route and the auth middleware are genuinely useful groundwork for Milestone 2's tools — the temptation to also stub out `forge_get_note` "since the pattern is right there" must be resisted. Nothing from Milestone 2's task table gets touched.
2. **Self-graded review.** The whole point of the Agentic Review gate, per the owner's instruction, is that it is not the implementing session declaring its own work correct. Run it as a genuinely independent pass — a fresh reviewer perspective, adversarial by design — not a summary of what was built.
3. **Silently narrowing "PASS WITH REQUIRED FIXES."** The underlying FDK framework only has binary PASS/FAIL at the report level (`09_IMPLEMENTATION_TASKS.md` §0, point 3) — a FAIL with fixable findings must still be treated as "not done yet," repaired, and re-reviewed, not quietly reinterpreted as good enough.
4. **Declaring the bootstrap-token exclusion correct without testing it.** This is the property most likely to have a subtle bug (an `or` that should be an `and`, a fallback path left in by habit). It must be tested explicitly, not inferred from the code reading correctly.

## Cross-references

- [README.md](README.md) · [01_SPEC.md](01_SPEC.md) · [03_BACKEND.md](03_BACKEND.md) · [06_API.md](06_API.md) · [08_ACCEPTANCE.md](08_ACCEPTANCE.md) · [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md) · [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md) · [CURRENT_STATE.md](CURRENT_STATE.md)
- [../../decisions/0018-mcp-server-integrated-not-separate-process.md](../../decisions/0018-mcp-server-integrated-not-separate-process.md)
- [../../decisions/0019-mcp-bearer-token-authentication.md](../../decisions/0019-mcp-bearer-token-authentication.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md) · [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md) · [../../13_PHASE_LIFECYCLE.md](../../13_PHASE_LIFECYCLE.md) · [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md)
