# ADR-0004 — Interactive workflows, not automation

> **Purpose:** Record that Forge's multi-step processes stay operator-driven at each step, rather than running as unattended background automation, as a repo-wide default posture.
> **Scope:** A product-wide principle, recorded now ahead of the phases (Prompt Studio, Model Playground, Project Initialization Engine) that will face this question directly. Not Workbench-specific mechanics.
> **Ownership:** Project owner (approved 2026-07-20)
> **Status:** Accepted
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../00_VISION.md](../00_VISION.md), [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
> **Supersedes:** —

---

## 1. Context

As Forge grows into an AI-assisted developer workbench (Prompt Studio, Model Playground, Project Initialization Engine), a recurring design question will come up repeatedly: should multi-step processes run autonomously in the background, or stay driven by the operator at each step? This is being settled once, now, before the phases that depend on the answer are designed — rather than re-litigated phase by phase.

## 2. Decision

Forge features involving multi-step processes are interactive and user-driven — the operator initiates and stays present through each meaningful step (reviewing, confirming, or adjusting) — rather than autonomous background automation that runs unattended and reports results after the fact. Precedent already exists: Ingest's document→Markdown conversion works this way today (operator uploads, reviews output). Future Prompt Studio prompt chains and Project Initialization Engine scaffolding follow the same posture.

## 3. Alternatives considered

- Autonomous/scheduled automation (background jobs, cron-triggered pipelines) as a default — rejected: Forge is a self-hosted tool the operator actively drives ([`../00_VISION.md`](../00_VISION.md) §1), not a service that acts on their behalf unattended. This also sidesteps a whole class of "what ran while I wasn't looking" trust questions on a tool that already handles secrets.
- Decide this per-phase, case by case, with no stated default — rejected: leaves every future phase's design session to re-derive the same answer.

## 4. Consequences

- Makes it easier: consistent UX expectations across phases — the operator is never surprised by something that happened without them.
- Makes it harder: features that would genuinely benefit from background automation (e.g. a scheduled backup, a watched-folder ingest) need an explicit, separately-justified exception, not a silent default.
- This principle belongs in [`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) as a numbered principle in a future documentation pass — recorded here first since it came up during Phase 01 planning, ahead of that update.

## 5. Cross-references

- [../00_VISION.md](../00_VISION.md)
- [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
- [../02_ROADMAP.md](../02_ROADMAP.md)
