# Prompt Template — FDK Verification Framework Implementation Kickoff

> **Purpose:** Copy this prompt to start a Claude Code session that operationalizes the Autonomous Multi-Agent Verification Framework specified in [15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md) — the `.claude/agents/*` verifiers, the orchestrator, the repair loop, and FDK phase-lifecycle integration. Distinct from [VERIFICATION_FRAMEWORK_KICKOFF_PROMPT.md](VERIFICATION_FRAMEWORK_KICKOFF_PROMPT.md), which produced the specification this prompt implements against.
> **Scope:** Code/config implementation across five independently-reviewable milestones (1, 2, 3, 4A, 4B — Milestone 4 was split so integration plumbing and autonomous-progression activation are separately reviewable and separately gated; 4A and 4B ship as separate pull requests, not just separate commits). Not for phase implementation work — for that, use [SESSION_START_PROMPT.md](SESSION_START_PROMPT.md).
> **Ownership:** TODO — assign an owner.
> **Status:** Draft
> **Last Updated:** 2026-07-29

---

## Template

```
This prompt initiates implementation of the FDK Verification Framework's
operational components — the verifier subagents, the orchestrator, the
repair loop, and FDK phase-lifecycle integration. Treat this prompt as
the authoritative task description. Do not assume prior conversation
context beyond the repository contents and the instructions below.

You are working in the Forge repository as a Claude Code session. The
documentation phase of this work is already complete:
forge-docs/decisions/0010-fdk-verification-automation-exception.md is an
Accepted ADR authorizing the framework to run autonomously within the FDK
development process, and forge-docs/15_VERIFICATION_FRAMEWORK.md is the
stable specification this implementation builds against (its own Status
field stays "Draft" by this repo's convention — living docs like this one
and forge-docs/13_PHASE_LIFECYCLE.md and forge-docs/14_IMPLEMENTATION_PLAYBOOK.md
are never marked "Accepted"; only ADRs carry that status — but "Draft" here
does not mean "unstable" or "open to reinterpretation": treat its content
as fixed unless the project owner amends it). This session implements
against both documents, it does not redesign them. If something in this
prompt appears to conflict with either document, stop and flag the
conflict rather than resolving it by picking one side.

Read, in order, before writing anything:
1. forge-docs/09_CLAUDE_CODE_RULES.md
2. forge-docs/15_VERIFICATION_FRAMEWORK.md
3. forge-docs/decisions/0010-fdk-verification-automation-exception.md
4. forge-docs/implementation/VERIFICATION_CONTRACT_TEMPLATE.md
5. forge-docs/14_IMPLEMENTATION_PLAYBOOK.md
6. forge-docs/10_CHECKPOINT_PROTOCOL.md

This work is structured as five milestones, in order: 1, 2, 3, 4A, 4B.
Each milestone is independently reviewable. Do not begin the next
milestone in the same turn the current one completes — produce a
checkpoint per
forge-docs/10_CHECKPOINT_PROTOCOL.md (Completed Tasks / Modified Files /
Current State / Remaining Work / Recommended Next Prompt / Known Risks)
and wait for explicit confirmation before continuing. This mirrors how
the specification phase itself was gated, and is deliberate: no milestone
here is small enough or obvious enough to justify skipping the check.

Milestone 1 — Verification infrastructure (no autonomous behavior yet):
- Verification Contract schema/parser, reading the shape defined in
  forge-docs/15_VERIFICATION_FRAMEWORK.md §5 and
  forge-docs/implementation/VERIFICATION_CONTRACT_TEMPLATE.md.
- Orchestrator skeleton — the coordination structure from §3, with no
  verifiers wired in yet and no ability to auto-continue anything. Per §9's
  "Orchestrator-replaceable" principle: the skeleton must contain no
  verifier-specific logic — it should only know how to load a contract,
  invoke whatever verifiers the contract declares (by a standard
  interface, not by name-specific branches), and aggregate whatever
  reports come back. If you find yourself writing a conditional for a
  specific verifier's behavior inside the orchestrator, that's a signal
  the interface between them is wrong, not a reason to special-case it.
- Report model — the structure from §6, producible from a
  hand-constructed set of fake verifier results, to prove the format
  before anything real produces it.
- Contract validation — a contract that's missing a required section or
  references a verifier that doesn't exist should fail loudly, not
  silently.
- At the end of this milestone, nothing runs automatically and nothing
  can auto-continue a phase. That capability doesn't exist until
  Milestone 4B.

Milestone 2 — Verifier agents:
- Implement the 8 verifiers from forge-docs/15_VERIFICATION_FRAMEWORK.md
  §4 as .claude/agents/*.md subagent definitions: Specification,
  Architecture, Build, Test, Regression, Code Quality, Documentation, UX
  (UX conditional per contract declaration, per §4.8).
- Each verifier should expose a common interface (consistent input: a
  contract + a codebase state; consistent output: pass/fail + findings)
  while delegating to existing tools where one already exists — e.g. the
  Build Verifier should shell out to the actual tsc/eslint/next
  build/pytest commands rather than reimplementing what they check, per
  the existing-mechanic mapping already documented in §4 for each
  verifier.
- Each verifier must only evaluate — confirm none of them is given write
  access to production code, per forge-docs/15_VERIFICATION_FRAMEWORK.md
  §4's shared rule.
- Per §9's "Orchestrator-replaceable" principle: each verifier must
  communicate only through the Verification Contract as input and the
  standardized report format as output — nothing verifier-to-orchestrator
  that bypasses that boundary (no shared mutable state, no orchestrator
  internals a verifier reaches into). Each verifier must also be directly
  invokable on its own, outside the orchestrator entirely, for debugging
  and manual use — if a verifier can only run when the orchestrator calls
  it, it doesn't meet this milestone's exit bar.
- Verifiers can be tested individually against a real or fixture codebase
  state in this milestone, independent of the orchestrator — this is the
  concrete proof of the independent-execution requirement above, not just
  a convenience.

Milestone 3 — Orchestration:
- Wire the Milestone 2 verifiers into the Milestone 1 orchestrator skeleton:
  execute the verifier pipeline per a loaded contract, aggregate results
  into a single PASS/FAIL decision (§3, §6), and generate the
  consolidated report.
- Implement the repair loop: on FAIL, aggregate failures into a
  remediation report, hand it to the Implementation Agent, re-verify,
  repeat — capped at the 3-cycle retry limit from §7. The verifier suite
  itself never edits production code; only the Implementation Agent does.
- Implement the escalation conditions from §8 (architecture/spec
  conflict, ambiguous requirements, destructive operation required,
  blocked external dependency, retry limit exceeded, confidence below
  threshold) as explicit stop-and-report conditions, not silent
  fallthroughs.
- At the end of this milestone, the orchestrator can run a full
  verify → report → repair → re-verify cycle end-to-end against a real
  contract, but still does not autonomously start a next phase's
  implementation — that wiring is Milestone 4B (Milestone 4A adds the
  FDK integration plumbing first, still with no auto-continue).
- Replaceability validation (the concrete test for the Architectural
  acceptance criterion below, not a separate optional task): build a
  second, minimal reference orchestrator — it can be as simple as a
  short script — that consumes the same Verification Contract shape and
  produces the same report format as the real Orchestrator. Substitute
  it in and run it against the Milestone 2 verifiers unchanged. If any
  verifier needs a code change, a special case, or a different call
  convention to work under the reference orchestrator, the "Orchestrator-
  replaceable" principle (§9) is not actually satisfied yet — go back and
  fix the verifier/contract boundary, don't just note it as a known gap.
  This test is what makes replaceability a pass/fail check instead of a
  code-review opinion.

Milestones 4A and 4B are each their own pull request, not just their own
commit within one PR. 4A must be safe to merge on its own — it contains
no code path that can advance a phase, so there is nothing in it that
needs 4B's dry run to be trustworthy. 4B is deliberately small and
reviewable on its own, containing only the activation capability and the
dry run that justified it, so a reviewer isn't re-reviewing 4A's
plumbing to approve 4B's one new behavior.

Build both milestones as a vertical slice, not horizontally. Horizontal
means building each component to completion across the whole system
before connecting anything (e.g. "wire contract discovery everywhere,
then report persistence everywhere, then hook up the lifecycle") — it
produces a system that's only checkable once every piece is done, which
is exactly the failure mode this staged-milestone approach exists to
avoid. Vertical means each numbered step below chains onto the previous
one into a single, narrow, already-executable path — discover contract
-> verify -> repair -> escalate -> persist -> hook into the lifecycle —
so the slice is reviewable and testable after every step, not just at
the end.

Milestone 4A — Lifecycle integration, autonomous progression disabled.
Goal: integrate the Milestone 1-3 framework into the Release Candidate
workflow while making it impossible for it to advance a phase. Build in
this order, each step landing on top of a working previous step:

1. Phase discovery — discover the active implementation phase and locate
   its VERIFICATION_CONTRACT.md per forge-docs/implementation/README.md
   §2.1, without a human pointing to it explicitly. Fail cleanly (a clear
   error, not a silent no-op) if the contract is absent.
2. Verification entry point — the single function/entry point the FDK
   lifecycle will call: load the discovered contract, build the verifier
   registry (verifiers.default_registry()), and run Orchestrator.run()
   to produce a VerificationReport. Nothing else yet.
3. Repair integration — wrap step 2's verification call with RepairLoop,
   respecting the 3-cycle limit from §7. Still no lifecycle decision of
   any kind made from the result.
4. Escalation integration — evaluate the escalation policy (evaluate())
   against the RepairLoop's result and produce the structured escalation
   output (render_escalation_report()) when applicable. Still stop here
   — nothing yet acts on the outcome beyond producing this output.
5. Report persistence — persist the verification report and, if
   applicable, the escalation report, following this repo's existing
   history/ conventions (see history/CHECKPOINT_LOG_TEMPLATE.md for the
   pattern this repo already uses for durable records).
6. Lifecycle hook — invoke the step 1-5 pipeline from
   forge-docs/13_PHASE_LIFECYCLE.md's Release Candidate stage, replacing
   the manual audit *only* as the audit mechanism. This step must not
   change phase state in any way — it runs the pipeline and persists its
   output, nothing more.
7. Regression guard — add tests proving: no advance-to-next-phase
   API/symbol exists anywhere in this package's public API; no automatic
   phase transition occurs under any input, including a clean PASS;
   Owner Sign-off remains untouched as a recorded human decision; every
   release action (git tag/merge/push) remains explicit-permission-gated,
   per forge-docs/15_VERIFICATION_FRAMEWORK.md §1 and
   forge-docs/09_CLAUDE_CODE_RULES.md §7. This is a durable trip-wire, not
   a one-time confirmation — it must still pass after 4B lands.

4A acceptance: contract is automatically discovered; verification runs
automatically at the RC stage; reports are generated and persisted; the
repair loop is functional; escalation is functional; no autonomous
progression capability exists anywhere in the codebase.

Milestone 4B — Activation. Precondition, not optional: a real phase
(Phase 05, or whichever phase FDK has reached) has a complete,
authorized 01_SPEC.md, 08_ACCEPTANCE.md, and VERIFICATION_CONTRACT.md.
This milestone cannot be satisfied against a fabricated or fixture phase
— do not begin it until that precondition is genuinely true. Build in
this order:

1. Dry run — execute an actual Release Candidate verification against
   the real phase via 4A's pipeline. Exercise PASS, FAIL, retry, and
   escalation — the full Validation requirement below is the concrete
   checklist for this step, not a separate, later task.
2. Review — confirm every verifier behaved correctly, the repair loop
   behaved correctly, escalation behaved correctly, and the persisted
   reports are correct. If anything failed, fix the underlying issue and
   rerun step 1 in full — do not patch around one failure and call the
   rest close enough.
3. Governance artifact — once every review item passes, write the
   dry-run result as a permanent, checked-in record (a history/ entry per
   history/CHECKPOINT_LOG_TEMPLATE.md, not a chat-only claim) documenting
   the framework version, the phase validated, the outcome, and
   observations. This record is evidence that validation occurred. It is
   not consulted by runtime code, and must never become one — coupling
   governance (why activation was introduced) to runtime (what the
   activation function does when called) means routine documentation
   maintenance (archiving old reports, rebasing history, renumbering
   framework versions) could silently change runtime behavior, which is
   worse than keeping the two concerns independent.
4. Introduce activation — only now, implement advance_to_next_phase(...)
   (or equivalent). This function did not exist before this step. Its
   behavior is governed purely by implementation state, never by checking
   for the governance record's presence, a version number in it, or any
   other artifact from step 3.
5. Lifecycle wiring — wire Release Candidate -> Verification -> PASS ->
   advance to the next implementation phase. FAIL continues to route to
   Repair Loop -> Escalation exactly as 4A already built it — 4B adds
   exactly one new edge (PASS -> advance), nothing else changes.
6. Regression verification — prove PASS advances correctly to the actual
   next phase per forge-docs/02_ROADMAP.md, not a hardcoded or assumed
   one; FAIL never advances; escalation never advances; retry-limit-
   exceeded never advances; Owner Sign-off still requires human
   confirmation; every release action stays human-only. Reconfirm 4A's
   step-7 regression guard still passes unmodified.
7. Dedicated activation commit — the introduction of autonomous
   progression lands in one commit whose sole purpose is enabling that
   capability after successful validation. No unrelated refactors, no
   other feature work bundled in. Its diff and commit message should make
   "this is what turns on autonomous phase progression, and this is the
   dry run that justified it" legible to a reviewer without archaeology.

4B acceptance: a successful real dry run occurred; a permanent validation
record was written; autonomous progression is enabled; human governance
(Owner Sign-off, release actions) is unchanged; all regression tests,
including 4A's, pass.

Architectural acceptance criterion (gates Milestone 2 completion; the
Milestone 3 replaceability validation above is the concrete test that
proves it, not a separate requirement): the Orchestrator must be
replaceable without changing any verifier's contract. At Milestone 2,
verify and be able to demonstrate all three of the following:
1. Verifiers communicate with the Orchestrator only through the
   Verification Contract and the standardized report format from
   forge-docs/15_VERIFICATION_FRAMEWORK.md §5–§6 — nothing else crosses
   that boundary.
2. The Orchestrator contains no verifier-specific logic — it coordinates
   generically against whatever the contract declares, per §9.
3. Each verifier is independently executable outside the Orchestrator,
   for debugging and manual use.
Treat these three as a Milestone 2 code-review check — necessary but not
sufficient. The criterion isn't actually satisfied until Milestone 3's
replaceability validation (swapping in the minimal reference orchestrator)
passes; that's the objective, falsifiable version of the same check. This
is what keeps parallel execution, distributed execution, or replacing the
Orchestrator entirely from requiring changes to every verifier later.
Treat a violation of either check as a blocker for its own milestone, not
a Milestone 6 cleanup item.

Validation requirement (this is 4B step 1's "Dry run" made concrete —
must be run and its result recorded per 4B's steps 1-3 BEFORE step 4
writes any activation code, not after): run at least one real end-to-end
dry run against an actual phase (Phase 05, once its 01_SPEC.md and
08_ACCEPTANCE.md are filled in and authorized — do not fabricate a fake
phase to satisfy this check) and confirm all of the following actually
happened, not just that code exists to do them. At this point in the
sequence advance_to_next_phase does not exist yet (it isn't introduced
until step 4) — nothing below should involve an actual phase transition
attempt; that verification happens later, in step 6, against the
now-introduced activation function:
- Contract generation/discovery worked without manual pointing.
- Every declared verifier actually executed.
- The consolidated report was generated in the format from §6.
- The PASS path was exercised: a genuinely passing implementation
  produced PASS, and — since no advance-to-next-phase capability exists
  at this point in the sequence — the run correctly did nothing beyond
  persisting the PASS report. (Confirming PASS actually triggers an
  advance, to the correct next phase per forge-docs/02_ROADMAP.md, is
  step 6's job, once step 4 has introduced that capability.)
- The FAIL path was exercised: a genuinely failing check (introduce one
  deliberately if the real phase doesn't happen to have one) produced
  FAIL and a remediation report with specific, actionable items.
- The retry/repair loop actually ran at least one real cycle.
- At least one escalation condition was deliberately triggered and
  produced a stop-and-report, not a silent continue.
- Owner Sign-off and every release action (tag/merge/push) were
  confirmed to still require explicit human action throughout — this is
  the single most important thing to verify, since it's the boundary
  ADR-0010 exists to protect.

Do not mark this implementation complete, and do not update
forge-docs/15_VERIFICATION_FRAMEWORK.md §10's "what's built vs. what's
next" section to remove any item, until Milestone 4B's validation
requirement has actually run against a real phase, its result is recorded
per 4B's governance-record step, and every bullet is confirmed, not
assumed.

Follow forge-docs/10_CHECKPOINT_PROTOCOL.md for checkpoints within a
milestone too, not just between milestones, if a milestone's own task
count or context usage crosses its stop-condition thresholds.
```

## TODO

- [ ] TODO: Replace this with a worked-example prompt once a real session has run Milestone 1.
- [ ] TODO: Confirm the physical location for `.claude/agents/*` verifier definitions and the orchestrator (skill vs. command vs. something else) doesn't already exist elsewhere in this repo's `.claude/` conventions before Milestone 2 begins — this prompt assumes the standard `.claude/agents/*.md` convention but doesn't mandate a specific orchestrator mechanism.

## Cross-references

- [README.md](README.md)
- [VERIFICATION_FRAMEWORK_KICKOFF_PROMPT.md](VERIFICATION_FRAMEWORK_KICKOFF_PROMPT.md) — produced the specification this prompt implements against
- [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md)
- [../../decisions/0010-fdk-verification-automation-exception.md](../../decisions/0010-fdk-verification-automation-exception.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
