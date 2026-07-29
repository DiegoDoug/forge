# ADR-0010 — FDK verification automation exception

> **Purpose:** Record that FDK's own build/verification meta-process — not any Forge product feature — is exempt from ADR-0004's operator-driven default, so the Autonomous Multi-Agent Verification Framework can run phase-transition audits without a human confirming each step.
> **Scope:** The FDK development process only (how phases move from "implementation done" to "next phase's implementation starts"). Does not touch Forge product UX, and does not override the project's global safety-rule gates on destructive/external-facing actions.
> **Ownership:** Project owner (approved 2026-07-25)
> **Status:** Accepted
> **Version:** 0.1.0
> **Last Updated:** 2026-07-25
> **Depends On:** [../00_VISION.md](../00_VISION.md), [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md), [0004-interactive-workflows-not-automation.md](0004-interactive-workflows-not-automation.md)
> **Supersedes:** —

---

## 1. Context

FDK phases currently move from "implementation done" to "next phase begins" through manual, human-driven steps: an independent audit a person reviews ([14_IMPLEMENTATION_PLAYBOOK.md](../14_IMPLEMENTATION_PLAYBOOK.md) §6), a Release Candidate cycle, and Owner Sign-off ([13_PHASE_LIFECYCLE.md](../13_PHASE_LIFECYCLE.md)). The project adopts an Autonomous Multi-Agent Verification Framework: a Verification Orchestrator plus 8 specialized verifier subagents that run automatically after an implementation phase completes, aggregate a single PASS/FAIL decision, drive an automatic repair loop on FAIL (capped at 3 cycles), and on PASS continue straight into the next phase's implementation with no human confirmation step. Human review is required only for genuine escalation: retry limit exceeded, ambiguous requirements, destructive operations required, blocked external dependencies, or confidence below threshold.

This collides in *shape* with [ADR-0004](0004-interactive-workflows-not-automation.md), a ratified, Accepted decision that Forge's multi-step processes stay operator-driven at each step, explicitly rejecting "autonomous... automation that runs unattended and reports results after the fact" as a default posture, on the grounds that Forge is a self-hosted tool the operator actively drives, not a service that acts on their behalf unattended. ADR-0004 does not collide in *literal scope* — its own Scope line frames it as "a product-wide principle... ahead of the phases (Prompt Studio, Model Playground, Project Initialization Engine)," i.e. Forge features end users touch, not the FDK meta-process by which those features get built. But [09_CLAUDE_CODE_RULES.md](../09_CLAUDE_CODE_RULES.md) §6 requires exactly this kind of cross-cutting, precedent-setting call to be drafted as a candidate decision and confirmed before implementation proceeds — treating "it's process, not product" as self-evidently out of scope would be the same shortcut ADR-0004 itself exists to close off. This ADR settles the question explicitly rather than leaving it implicit.

## 2. Decision

FDK's own build/verification meta-process — defined in [`../15_VERIFICATION_FRAMEWORK.md`](../15_VERIFICATION_FRAMEWORK.md) — is exempt from ADR-0004's operator-driven default. The Autonomous Multi-Agent Verification Framework is authorized to execute automatically within the FDK development process, subject to the constraints defined by this ADR and the Verification Framework specification.

A PASS authorizes only progression within the FDK implementation workflow — specifically, starting the next phase's implementation. It does not authorize release, publication, tagging, merging, deployment, or any other externally visible or irreversible action.

Verification agents provide evidence and recommendations. They do not establish architectural policy; only accepted ADRs may do so.

Two further boundaries on this exception:

- **It does not touch Forge product UX.** ADR-0004 remains fully in force, unchanged, for every Forge product feature (Prompt Studio, Ingest, the future Model Playground, and anything else an end user of the shipped app interacts with). This ADR carves out FDK's own development process only — the tooling that builds Forge, not Forge itself.
- **It does not override the project's global safety rules governing destructive or externally visible actions.** Git push/tag/merge, publishing content, and sending messages remain explicit-permission-gated regardless of what a verifier reports as PASS. The Verification Framework automates the audit gate between "implementation done" and "next phase's implementation starts" (the Release Candidate audit in [13_PHASE_LIFECYCLE.md](../13_PHASE_LIFECYCLE.md)); it does not automate Owner Sign-off as a recorded decision, and it does not automate the Released stage's tag/merge ceremony ([14_IMPLEMENTATION_PLAYBOOK.md](../14_IMPLEMENTATION_PLAYBOOK.md) §11) — those stay human-confirmed, per [09_CLAUDE_CODE_RULES.md](../09_CLAUDE_CODE_RULES.md) §7, which already states global safety rules take precedence over anything an FDK document says.

## 3. Alternatives considered

- **Scale back to "auto-verify, but a human still confirms the phase transition."** Closer to ADR-0004's spirit — verifiers run automatically, but starting the next phase's implementation still waits for an explicit go-ahead. Rejected: the project owner explicitly chose full automation (PASS auto-continues; humans only engage on escalation) over this narrower alternative when the two were presented as options.
- **Treat the FDK meta-process as already outside ADR-0004's scope, with no new ADR needed.** ADR-0004's own Scope line arguably already excludes it. Rejected: skipping the ADR because the answer "seems obvious" is exactly the failure mode `09_CLAUDE_CODE_RULES.md` §6 exists to prevent — a persuasive read of scope today could just as easily be a wrong read next time, and there'd be no durable record of the reasoning either way.
- **Fold this into ADR-0004 itself as an amendment rather than a new ADR.** Rejected: ADR-0004 is Accepted and describes a settled product principle; amending it to carry a process-only carve-out would blur its own stated scope for future readers. A separate, cross-referenced ADR keeps ADR-0004 legible as "product UX stays operator-driven, full stop" while this ADR carries the one documented exception and its guardrails.

## 4. Consequences

- **Makes it easier:** reduces idle time between verified completion and subsequent implementation — the framework's core design goal.
- **Makes it harder:** catching a subtly-wrong "PASS" before the next phase's implementation has already begun building on top of it. Mitigated by the 3-cycle retry cap, the explicit escalation conditions in `15_VERIFICATION_FRAMEWORK.md`, and the fact that release/merge actions stay human-gated regardless — a wrong PASS can be caught and corrected before anything ships, even if a phase's implementation work has already started.
- **Touches an architectural invariant:** this ADR establishes the first explicit exception to ADR-0004's product-wide default. Any future request to automate a *product* feature (not FDK process) must still be justified on its own terms against ADR-0004 — this ADR does not set a precedent for weakening ADR-0004 generally, only for this one, explicitly bounded, process-only case.
- **Should be revisited** once a real phase has actually traversed the Verification Framework end-to-end (mirrors ADR-0004 §4's own TODO pattern of revisiting a principle once real usage exists) — confirm the 3-cycle retry cap and escalation thresholds are calibrated correctly against a worked example, not just a hypothetical one.

## 5. Cross-references

- [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
- [0004-interactive-workflows-not-automation.md](0004-interactive-workflows-not-automation.md) — the decision this ADR carves a narrow exception into
- [../09_CLAUDE_CODE_RULES.md](../09_CLAUDE_CODE_RULES.md) §6 (blocking architectural decisions) and §7 (global safety rules always take precedence)
- [../13_PHASE_LIFECYCLE.md](../13_PHASE_LIFECYCLE.md) — the Release Candidate stage this ADR's framework automates
- [../14_IMPLEMENTATION_PLAYBOOK.md](../14_IMPLEMENTATION_PLAYBOOK.md) §6, §11 — the manual audit and release ceremony this ADR's framework partially automates and partially leaves untouched
- `../15_VERIFICATION_FRAMEWORK.md` — the full framework specification this ADR authorizes
