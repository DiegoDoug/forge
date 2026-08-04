# 15 — Verification Framework

> **Purpose:** Define the Autonomous Multi-Agent Verification Framework — the Verification Orchestrator and its 8 specialized verifier subagents that automatically audit an implementation phase and gate progression to the next one, replacing the manual audit step with a contract-driven, repeatable process.
> **Scope:** The FDK development process only — how a phase's implementation gets audited and how the next phase's implementation begins. Does not touch Forge product UX ([01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md), [ADR-0004](decisions/0004-interactive-workflows-not-automation.md) govern that, unchanged), and does not touch release actions (git tag/merge/push) or any other externally visible or irreversible action.
> **Ownership:** TODO — assign an owner.
> **Status:** Draft
> **Version:** 0.2.0
> **Last Updated:** 2026-07-25
> **Depends On:** [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md), [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md), [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md), [13_PHASE_LIFECYCLE.md](13_PHASE_LIFECYCLE.md), [14_IMPLEMENTATION_PLAYBOOK.md](14_IMPLEMENTATION_PLAYBOOK.md), [decisions/0010-fdk-verification-automation-exception.md](decisions/0010-fdk-verification-automation-exception.md)
> **Supersedes:** —

---

## 1. Purpose and relationship to existing docs

This framework automates the Release Candidate audit step described in [13_PHASE_LIFECYCLE.md](13_PHASE_LIFECYCLE.md) and the manual "run an independent audit before signing off" step in [14_IMPLEMENTATION_PLAYBOOK.md](14_IMPLEMENTATION_PLAYBOOK.md) §6. Its authority to run without a human confirming each phase transition comes from [ADR-0010](decisions/0010-fdk-verification-automation-exception.md), which carves this specific exception out of [ADR-0004](decisions/0004-interactive-workflows-not-automation.md)'s operator-driven default.

What this framework changes: the audit that decides whether a phase's implementation is correct and complete runs automatically, on a contract, instead of waiting for a person to manually review it. On a PASS, the next phase's implementation starts immediately — no human confirms that specific transition.

What this framework does **not** change, per ADR-0010 §2:

- **Owner Sign-off** remains a recorded human decision in [13_PHASE_LIFECYCLE.md](13_PHASE_LIFECYCLE.md)'s lifecycle — this framework's PASS is an input to that decision, not a replacement for it.
- **The Released stage's tag/merge ceremony** ([14_IMPLEMENTATION_PLAYBOOK.md](14_IMPLEMENTATION_PLAYBOOK.md) §11) stays human-confirmed. A verifier PASS is a precondition for release, never a substitute for the explicit git actions that ship it.
- **Global safety rules** (destructive git operations, publishing, sending messages) govern regardless of anything this framework reports — see [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md) §7.
- **Forge product UX** is entirely untouched. ADR-0004 remains the default for every Forge feature.

## 2. High-level workflow

```
Implementation Agent completes a phase's implementation
        ↓
Verification Orchestrator loads the phase's Verification Contract
        ↓
Launches the required verifiers (§4) in parallel
        ↓
Aggregates results into a single PASS/FAIL decision (§6)
        ↓
   PASS ──────────────────────────────► Next phase's implementation begins
        ↓ FAIL
Consolidated remediation report generated (§7)
        ↓
Implementation Agent repairs the specific failures listed
        ↓
Verification re-runs
        ↓
   (repeat, capped at 3 cycles — §7)
        ↓
Retry limit exceeded, or an §8 escalation condition is hit
        ↓
Stop. Produce an escalation report. Wait for human input.
```

## 3. Verification Orchestrator responsibilities

The Orchestrator coordinates; it never evaluates implementation quality itself. Its responsibilities:

- Load the active phase's Verification Contract (§5).
- Launch every verifier the contract declares as required (§4), plus the UX verifier only if the contract declares it.
- Collect each verifier's result.
- Determine the overall PASS/FAIL decision — FAIL if any required verifier fails; PASS only if all required verifiers pass.
- Generate the consolidated report (§6).
- On FAIL: aggregate failures into a single remediation report, hand it to the Implementation Agent, and trigger re-verification once repairs are made.
- Enforce the retry limit (§7) and the escalation conditions (§8).
- On PASS: mark the phase's implementation as verified, persist the report (alongside the phase's `CURRENT_STATE.md`, per the checkpoint discipline in [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)), and begin the next phase's implementation.

## 4. The 8 specialized verifiers

Every verifier shares two rules: it evaluates only, and it never modifies production code. Where this repo already has a concrete mechanic for what a verifier checks, the verifier uses it rather than inventing a parallel one.

### 4.1 Specification Verifier
Validates every required task, acceptance criterion, and milestone in the phase's Verification Contract against what was actually built. Maps directly onto the phase's own `08_ACCEPTANCE.md` and `09_IMPLEMENTATION_TASKS.md` — an acceptance criterion that's provably false against the running app is the same BLOCKER condition already defined in [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md) §2.

### 4.2 Architecture Verifier
Validates architectural compliance: dependency direction, layering, no duplicated services or parser logic, no unnecessary abstractions, no circular imports, adherence to the invariants in [03_ARCHITECTURE.md](03_ARCHITECTURE.md) (thin routers, feature isolation, no cross-feature imports — the same invariants [14_IMPLEMENTATION_PLAYBOOK.md](14_IMPLEMENTATION_PLAYBOOK.md) §3 already asks implementers to follow).

### 4.3 Build Verifier
Runs lint, typecheck, and build (`tsc`, `eslint`, `next build`, backend test/build, `docker compose build`). Any failure is an immediate FAIL — this is the same BLOCKER build-failure criterion already defined in [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md) §2.

### 4.4 Test Verifier
Runs the phase's required test suites. Verifies tests pass, nothing is unexpectedly skipped, no snapshot regressions occurred, and coverage doesn't regress where coverage is tracked. Maps onto the testing requirements in [14_IMPLEMENTATION_PLAYBOOK.md](14_IMPLEMENTATION_PLAYBOOK.md) §5.

### 4.5 Regression Verifier
Confirms unrelated, previously-shipped functionality still works — routing, navigation, converters, shared components, activity logging, existing APIs. This is the same "no regressions in existing features" spot-check already listed in [14_IMPLEMENTATION_PLAYBOOK.md](14_IMPLEMENTATION_PLAYBOOK.md) §10 and the merge criteria in [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md) §6.

### 4.6 Code Quality Verifier
Inspects for duplicated logic, dead code, unreachable branches, stray `TODO`/`FIXME` markers, debug statements, unused exports, unnecessary dependencies, and orphaned files. It may recommend improvements, but — matching the MAJOR/MINOR-not-BLOCKER framing in [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md) §2 — it fails verification only when a finding violates a real project standard, not for stylistic preference.

### 4.7 Documentation Verifier
Confirms the documentation a phase is required to update actually was: implementation notes, `CURRENT_STATE.md`, `10_RELEASE_NOTES.md`, architecture docs, and root-level docs the phase touches. Maps onto [14_IMPLEMENTATION_PLAYBOOK.md](14_IMPLEMENTATION_PLAYBOOK.md) §8.

Deliberately simple: it checks §7 items that are marked `checked` against this run's changed files, and does not interpret conditional prose ("if X changes", "when applicable"). Contract §7 is authored with no unresolved conditionals by RC time — see [`VERIFICATION_CONTRACT_TEMPLATE.md`](implementation/VERIFICATION_CONTRACT_TEMPLATE.md) §7 for the required convention: resolve every conditional to either a concrete unconditional requirement (checked, and satisfied) or an explicitly-reasoned non-requirement (left unchecked) before running the RC pipeline.

**Lifecycle/roadmap documents are a Release-stage obligation, not an RC-stage one.** `02_ROADMAP.md` and `implementation/README.md`'s phase-status rows describe where a phase sits in [13_PHASE_LIFECYCLE.md](13_PHASE_LIFECYCLE.md)'s stage order (`... → Release Candidate → QA → Owner Sign-off → Released → Frozen → ...`). A phase that has only reached Release Candidate has, by definition, not yet reached the state those two documents would need to declare — updating them at RC time would make them state something not yet true. This repository's own precedent confirms the timing: Phase 06's roadmap update landed in the same commit as its freeze (`"Post-release: Freeze Phase 06, archive artifacts, update roadmap"`), after release, not during RC. Contract §7 should therefore leave `02_ROADMAP.md`/`implementation/README.md` items **unchecked at RC** (not required for this candidate) and require them as part of the Released/Frozen-stage process instead.

### 4.8 UX Verifier (conditional)
Runs only when the phase's Verification Contract declares user-visible functionality changed. Verifies layout, spacing, responsiveness, loading/empty states, accessibility basics, and dark mode — the same checks already listed in [14_IMPLEMENTATION_PLAYBOOK.md](14_IMPLEMENTATION_PLAYBOOK.md) §5 "Frontend" and may use screenshots where available. Acceptance criteria a verifier structurally cannot check (no real device, no screen reader) are not verifier failures — per [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md) §4, they're unverified claims tracked as `QA/` tickets, same as today.

## 5. The Verification Contract

Every FDK phase **from Phase 05 onward** defines a Verification Contract before implementation begins, using [`implementation/VERIFICATION_CONTRACT_TEMPLATE.md`](implementation/VERIFICATION_CONTRACT_TEMPLATE.md). The framework operates exclusively against this contract — it does not infer scope. A contract defines:

1. **Phase Metadata** — name, objective, dependencies, completion definition.
2. **Required Tasks** — a machine-verifiable checklist, drawn from the phase's `09_IMPLEMENTATION_TASKS.md`.
3. **Acceptance Criteria** — drawn verbatim from `08_ACCEPTANCE.md`; every criterion independently validated, no inferred success.
4. **Expected File Scope** — the files, directories, and modules a phase is expected to touch; unexpected modifications are reported, not silently allowed.
5. **Required Validation Commands** — lint, typecheck, build, test, integration test commands, drawn from `07_TESTING.md`.
6. **Architecture Constraints** — drawn from `03_ARCHITECTURE.md` and any phase-specific ADR.
7. **Documentation Requirements** — which docs this phase must update.
8. **Regression Targets** — the existing functionality this phase must not break.
9. **Required Verification Agents** — which of the 8 verifiers in §4 must run (UX only if declared).

Phases 01–04 are already Frozen or Released and are not retrofitted with a Verification Contract — per [13_PHASE_LIFECYCLE.md](13_PHASE_LIFECYCLE.md) §4, a frozen phase's spec cannot be reopened.

## 6. Verification report format

The Orchestrator produces one consolidated report per verification run, in this repo's plain Markdown style:

```markdown
## FDK Verification Report — Phase [NN]

| Verifier | Result |
|---|---|
| Specification | PASS |
| Architecture | PASS |
| Build | PASS |
| Tests | PASS |
| Regression | PASS |
| Code Quality | PASS |
| Documentation | PASS |
| UX | N/A |

**Overall status:** PASS
**Confidence:** [percentage]
**Recommendation:** CONTINUE

### Warnings
- [non-blocking findings, if any]

### Failures
- [none, on PASS]
```

On FAIL, the same table shows which verifiers failed, and the report adds:

```markdown
### Failed verifiers
- [verifier name]: [what failed]

### Recommended repairs
1. [specific, actionable repair item]
2. ...
```

## 7. Repair loop and retry policy

On FAIL:

1. Aggregate every verifier's failures into one consolidated remediation report.
2. Hand only the remediation items to the Implementation Agent — the verifier suite never edits production code itself.
3. The Implementation Agent repairs the specific failures listed.
4. Re-run every required verifier.
5. Repeat until PASS or the retry limit is reached.

**Retry limit: 3 automatic cycles.** This generalizes the RC1 → RC2 → ... pattern [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md) §5 already uses for Release Candidates, but gives it a hard cap instead of an open-ended loop — a phase that still fails after 3 repair cycles has a problem an automatic loop won't resolve (a wrong contract, a misunderstood requirement, a genuine architectural conflict), and needs human judgment rather than a 4th automatic attempt.

## 8. Escalation conditions

Stop immediately and produce an escalation report, per §3, when any of the following occurs. Each maps back to an existing "must ask first" trigger rather than inventing new escalation vocabulary:

| Escalation condition | Existing trigger it maps to |
|---|---|
| Architecture decision conflicts with the specification | [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md) §6 — blocking architectural decision |
| Requirements are ambiguous | [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md) §2 — documentation-first rule; draft the missing spec section and stop |
| A destructive operation is required to proceed | This session's global safety rules — destructive operations always require explicit permission |
| An external dependency blocks progress | [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md) §3 — adding a new external dependency requires asking first |
| Retry limit (§7) exceeded | New to this framework — see §7 |
| Verifier confidence falls below an acceptable threshold | Treated the same as a FAIL — the Orchestrator does not round a low-confidence PASS up to PASS |

## 9. Design principles

The framework stays:

- **Deterministic** — the same contract and the same implementation produce the same verdict.
- **Reproducible** — every verification run is a fresh evaluation, not a cached assumption.
- **Architecture-aware** — verifiers check against `03_ARCHITECTURE.md`, not just "does it run."
- **Phase-aware** — every run is scoped to one phase's contract, never a blend of phases.
- **Contract-driven** — the Orchestrator operates only against the declared Verification Contract, never inferred scope.
- **Extensible** — a phase can add a verifier the base 8 don't cover, the way [implementation/README.md](implementation/README.md) §2 already allows a phase to add a numbered doc beyond the standard 12.
- **Non-destructive** — no verifier modifies production code; only the Implementation Agent repairs.
- **Independent of the implementation agent** — the same verifier suite audits any implementation, regardless of who or what produced it.
- **Orchestrator-replaceable** — verifiers communicate only through the Verification Contract (§5) and the standardized report format (§6); the Orchestrator coordinates execution but contains no verifier-specific logic. Concretely: the Orchestrator can be replaced — for parallel execution, distributed execution, or a different coordination mechanism entirely — without changing a single verifier, and each verifier remains independently executable outside the Orchestrator for debugging and manual use. A verifier that only works when called by the Orchestrator, or an Orchestrator that special-cases a particular verifier's behavior, both violate this principle.

## 10. What's built vs. what's next

This document is the agreed specification for the framework. It does not, by itself, implement the framework. Not yet built, and out of scope for the session that wrote this document:

- [ ] The 8 verifier subagent definitions (`.claude/agents/*.md`) that Claude Code would actually launch.
- [ ] An orchestrating skill or command that invokes those subagents via the Agent/Workflow tools, aggregates their results, and drives the repair loop.
- [ ] A worked example of a phase (starting with Phase 05, once its `01_SPEC.md` and `08_ACCEPTANCE.md` are filled in) actually running a Verification Contract through this framework end-to-end.

Per [ADR-0010](decisions/0010-fdk-verification-automation-exception.md) §4, this framework should be revisited once a real phase has traversed it, to confirm the retry cap and escalation thresholds are calibrated against real usage rather than a hypothetical.

## 11. Cross-references

- [decisions/0010-fdk-verification-automation-exception.md](decisions/0010-fdk-verification-automation-exception.md) — the ADR authorizing this framework's automation
- [decisions/0004-interactive-workflows-not-automation.md](decisions/0004-interactive-workflows-not-automation.md) — the default this framework is a narrow, explicit exception to
- [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md)
- [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md)
- [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)
- [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md)
- [13_PHASE_LIFECYCLE.md](13_PHASE_LIFECYCLE.md)
- [14_IMPLEMENTATION_PLAYBOOK.md](14_IMPLEMENTATION_PLAYBOOK.md)
- [implementation/README.md](implementation/README.md) — where `VERIFICATION_CONTRACT.md` fits in a phase folder's shape
- [implementation/VERIFICATION_CONTRACT_TEMPLATE.md](implementation/VERIFICATION_CONTRACT_TEMPLATE.md)
