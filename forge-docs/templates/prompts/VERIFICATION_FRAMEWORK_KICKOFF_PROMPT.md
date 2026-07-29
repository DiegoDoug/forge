# Prompt Template — FDK Verification Framework Kickoff

> **Purpose:** Copy this prompt to start a Claude Code session that implements the FDK Autonomous Multi-Agent Verification Framework — the ADR, the framework spec, the contract template, and the doc updates that introduce it into FDK's phase lifecycle.
> **Scope:** One-time framework-introduction session. Not for phase implementation work — for that, use [SESSION_START_PROMPT.md](SESSION_START_PROMPT.md).
> **Ownership:** TODO — assign an owner.
> **Status:** Draft
> **Last Updated:** 2026-07-25

---

## Template

```
This prompt initiates implementation of the FDK Verification Framework.
Treat this prompt as the authoritative task description. Do not assume
prior conversation context beyond the repository contents and the
instructions below.

You are working in the Forge repository as a Claude Code session. The task
is to introduce an Autonomous Multi-Agent Verification Framework into FDK
(Forge Development Kit, forge-docs/) — a Verification Orchestrator plus 8
specialized verifier subagents (Specification, Architecture, Build, Test,
Regression, Code Quality, Documentation, and an optional UX verifier) that
run after an implementation phase completes, aggregate a single PASS/FAIL
decision, drive an automatic repair loop on FAIL (capped at 3 cycles), and
on PASS continue straight into the next phase's implementation without a
human confirmation step. Humans are only pulled in on genuine escalation:
retry limit exceeded, ambiguous requirements, destructive operations
required, blocked external dependencies, or confidence below threshold.

This is a documentation-only pass. Do not create any .claude/agents/*
subagent definition files, and do not build an orchestrating skill or
command that invokes the Agent/Workflow tools. Those are follow-up
implementation work for a later session — this session produces the
agreed specification and contract those future subagents/orchestrator
will be built against, not the subagents themselves.

Read, in order, before writing anything:
1. forge-docs/09_CLAUDE_CODE_RULES.md
2. forge-docs/decisions/0004-interactive-workflows-not-automation.md
3. forge-docs/decisions/ADR_TEMPLATE.md
4. forge-docs/decisions/README.md
5. forge-docs/13_PHASE_LIFECYCLE.md
6. forge-docs/14_IMPLEMENTATION_PLAYBOOK.md
7. forge-docs/implementation/README.md

Step 1 — Draft the ADR, then STOP:

Draft forge-docs/decisions/0010-fdk-verification-automation-exception.md
using ADR_TEMPLATE.md's exact section shape (Context / Decision /
Alternatives considered / Consequences / Cross-references) and this
repo's standard frontmatter block. Set its Status to "Proposed", not
"Accepted". The decision it records:

- FDK's own build/verification meta-process (defined in the
  forge-docs/15_VERIFICATION_FRAMEWORK.md this prompt asks you to write
  next) is exempt from ADR-0004's operator-driven default.
- ADR-0004 remains fully in force for Forge product features (Prompt
  Studio, Ingest, Model Playground, etc.) — this exception does not touch
  product UX in any way.
- The exception never reaches this session's own global safety rules:
  git push/tag/merge, publishing, and sending messages stay
  explicit-permission-gated regardless of what a verifier reports as
  PASS. Verification automates the audit gate between "implementation
  done" and "next phase's implementation starts" — it does not automate
  release actions.

In "Alternatives considered", address: (a) scaling back to "auto-verify,
but a human still confirms the phase transition" — rejected in favor of
full automation, per the project owner's explicit choice; (b) treating
the FDK process as already outside ADR-0004's scope with no new ADR
needed — rejected, because 09_CLAUDE_CODE_RULES.md §6 requires drafting
a candidate decision for exactly this kind of cross-cutting call, and
skipping that step because it's "process not product" would be the same
shortcut ADR-0004 itself exists to close off.

Then STOP. Do not write any other file in this same turn. Present the
drafted ADR-0010 to the user and wait for explicit approval before doing
anything else, per 09_CLAUDE_CODE_RULES.md §6's rule for blocking
architectural decisions. Approval is not implied by anything in this
prompt — it must come from the user, in response to seeing the actual
drafted ADR. Only once it is explicitly approved does ADR-0010's Status
flip to "Accepted" and does Step 2 begin.

Step 2 — Once ADR-0010 is Accepted:

a. Write forge-docs/15_VERIFICATION_FRAMEWORK.md (the next number after
   14_IMPLEMENTATION_PLAYBOOK.md), using this repo's standard frontmatter
   and numbered-section style, covering:
   - Purpose and its relationship to existing docs: it automates the
     Release Candidate audit step in 13_PHASE_LIFECYCLE.md and the manual
     audit in 14_IMPLEMENTATION_PLAYBOOK.md §6. It does not eliminate
     Owner Sign-off as a concept or automate the Released stage's tag/
     merge actions — those stay human-gated per 09_CLAUDE_CODE_RULES.md
     §7 and this session's own non-FDK-overridable global safety rules.
   - The high-level workflow: Implementation Agent -> Verification
     Orchestrator -> 8 verifiers -> aggregate -> PASS (auto-continue) /
     FAIL (remediation report -> repair -> re-verify), retry-capped at 3,
     then escalate.
   - Verification Orchestrator responsibilities: load the phase's
     Verification Contract, launch verifiers, aggregate results, produce
     the consolidated report, drive repair cycles, enforce the retry
     limit, trigger the next phase's implementation start on PASS. It
     never evaluates implementation quality itself.
   - Each of the 8 verifiers (Specification, Architecture, Build, Test,
     Regression, Code Quality, Documentation, UX-conditional): what it
     validates, that it never modifies production code, and — where a
     concrete repo mechanic already exists — how it maps onto it. For
     example: Build Verifier maps to the BLOCKER build-failure criterion
     in 12_BUG_CLASSIFICATION.md §2 (tsc/eslint/next build/backend
     tests); Regression Verifier maps to the "no regressions in existing
     features" check in 14_IMPLEMENTATION_PLAYBOOK.md §10; Code Quality
     Verifier follows the MAJOR/MINOR-not-BLOCKER framing in
     12_BUG_CLASSIFICATION.md §2 (may recommend, fails only on real
     standards violations).
   - The Verification Contract standard shape: Phase Metadata, Required
     Tasks, Acceptance Criteria, Expected File Scope, Required Validation
     Commands, Architecture Constraints, Documentation Requirements,
     Regression Targets, Required Verification Agents (+ optional UX).
     Point at VERIFICATION_CONTRACT_TEMPLATE.md (Step 2b) as where a
     phase actually fills this in.
   - The consolidated verification report format, in this repo's plain
     Markdown heading/checklist style (not ASCII-art boxes).
   - The repair loop and retry policy: aggregate failures -> consolidated
     remediation report -> implementation agent repairs -> re-verify ->
     repeat, capped at 3 automatic cycles. Explain the cap the way
     12_BUG_CLASSIFICATION.md §5 already frames RC1 -> RC2 -> ... cycles,
     as a generalization with a hard limit.
   - Escalation conditions (architecture/spec conflict, ambiguous
     requirements, destructive operations required, blocked external
     dependencies, retry limit exceeded, confidence below threshold),
     each mapped back to an existing "must ask first" trigger in
     09_CLAUDE_CODE_RULES.md §3 or this session's own global safety rules
     where one already exists, rather than inventing new vocabulary.
   - Design principles: deterministic, reproducible, architecture-aware,
     phase-aware, contract-driven, extensible, non-destructive,
     independent of the implementation agent.
   - A closing "What's built vs. what's next" section stating explicitly
     that this document is the agreed specification, and that the actual
     .claude/agents/* subagent definitions and the orchestrating skill/
     command that invokes them are follow-up implementation work, not
     delivered here — matching this repo's existing TODO-section
     convention for tracking forward work.
   - Cross-references.

b. Write forge-docs/implementation/VERIFICATION_CONTRACT_TEMPLATE.md,
   sibling to the existing RELEASE_NOTES_TEMPLATE.md pattern referenced
   in implementation/README.md §2.1, with the 9 Verification Contract
   sections above as fillable "- [ ] TODO: ..." placeholders, matching
   the placeholder style already used in
   implementation/Phase-05-Model-Playground/08_ACCEPTANCE.md.

c. Edit forge-docs/implementation/README.md §2 ("Shape of every phase
   folder") to add VERIFICATION_CONTRACT.md as a standard file **from
   Phase 05 onward only** — do not retrofit it onto the already-frozen
   Phase 01-04 folders (consistent with 13_PHASE_LIFECYCLE.md §4: a
   frozen phase's spec cannot be reopened). Reference
   VERIFICATION_CONTRACT_TEMPLATE.md and ../15_VERIFICATION_FRAMEWORK.md.

d. Edit forge-docs/13_PHASE_LIFECYCLE.md's Release Candidate stage row:
   describe the Verification Orchestrator as the default audit mechanism
   (manual audit becomes the escalation fallback, not the default). Add
   15_VERIFICATION_FRAMEWORK.md to Depends On and the Cross-references
   section. Leave the Owner Sign-off and Released stage language
   untouched — that boundary is intentional, per ADR-0010.

e. Edit forge-docs/14_IMPLEMENTATION_PLAYBOOK.md: reframe §6's
   "Run an independent audit before signing off" as running automatically
   via the Verification Orchestrator by default, with a manual pass
   remaining available for the escalation cases the new doc defines. Add
   one clarifying line to §11 that verification PASS is a precondition
   for, not a substitute for, the human-confirmed tag/merge steps. Add
   15_VERIFICATION_FRAMEWORK.md to Depends On and §13 Cross-references.

f. Edit forge-docs/09_CLAUDE_CODE_RULES.md: add
   15_VERIFICATION_FRAMEWORK.md to the §1 read order for sessions doing
   phase-completion work, and add "run the Verification Framework after
   implementation and continue to the next phase's implementation on a
   PASS result" to §3's "May do without asking" list. Do not touch
   "Must ask first" or §7 — global safety rules already correctly take
   precedence and need no restatement.

g. Add index rows: forge-docs/README.md §2 (row for doc 15) and
   forge-docs/decisions/README.md §3 (ADR-0010 row; update the header's
   decision counts, e.g. "9 decisions recorded (8 accepted, 1 proposed)"
   becomes "10 decisions recorded (9 accepted, 1 proposed)").

Do not, in this session: create .claude/agents/* subagent files; build an
orchestrating skill/command; retrofit VERIFICATION_CONTRACT.md into Phase
01-04; or pre-fill a VERIFICATION_CONTRACT.md for Phase 05-08 (their
01_SPEC.md and 08_ACCEPTANCE.md are still template placeholders — there
is nothing real yet to put in one).

Follow the checkpoint protocol in forge-docs/10_CHECKPOINT_PROTOCOL.md if
this session's work crosses one of its stop-condition thresholds.
```

## TODO

- [ ] TODO: Replace this with a worked-example prompt once a real session has run it and ADR-0010 exists.

## Cross-references

- [README.md](README.md)
- [SESSION_START_PROMPT.md](SESSION_START_PROMPT.md)
- [../../decisions/0004-interactive-workflows-not-automation.md](../../decisions/0004-interactive-workflows-not-automation.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
- `../../15_VERIFICATION_FRAMEWORK.md` — does not exist yet; created by running this prompt
