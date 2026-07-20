# Forge Development Kit (FDK)

> **Purpose:** Entry point and navigation index for the entire documentation-first engineering system that drives Forge's future development.
> **Scope:** Index only — points to every root document and subsystem. Content lives in the linked files, not here.
> **Ownership:** TODO — assign an FDK owner.
> **Status:** Draft
> **Last Updated:** 2026-07-20

---

## 1. Start here

If you are a Claude Code session about to do implementation work in this repository, read [`09_CLAUDE_CODE_RULES.md`](09_CLAUDE_CODE_RULES.md) before anything else.

## 2. Root documents

| # | Document | Covers |
|---|----------|--------|
| 00 | [VISION.md](00_VISION.md) | Why Forge exists, its north star |
| 01 | [PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md) | Recurring product/design judgment calls |
| 02 | [ROADMAP.md](02_ROADMAP.md) | Phase sequencing |
| 03 | [ARCHITECTURE.md](03_ARCHITECTURE.md) | System shape, integration points |
| 04 | [UI_GUIDELINES.md](04_UI_GUIDELINES.md) | Interaction and UX conventions |
| 05 | [DESIGN_SYSTEM.md](05_DESIGN_SYSTEM.md) | Visual tokens |
| 06 | [TECH_STACK.md](06_TECH_STACK.md) | Every dependency, current and anticipated |
| 07 | [CODING_STANDARDS.md](07_CODING_STANDARDS.md) | Code-level conventions |
| 08 | [DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md) | The task/feature completion checklist |
| 09 | [CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md) | The Claude Code execution contract |
| 10 | [CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md) | When and how to checkpoint |
| 11 | [PROJECT_STRUCTURE.md](11_PROJECT_STRUCTURE.md) | Physical repository map |

## 3. Subsystems

| Folder | Purpose |
|---|---|
| [implementation/](implementation/README.md) | The 8 phase specs — the actual buildable work |
| [templates/](templates/README.md) | Reusable templates (scaffolding, chunks, workflows, prompts, assets) |
| [decisions/](decisions/README.md) | Architecture decision records (ADRs) |
| [history/](history/README.md) | Durable checkpoint log |

## 4. Related documentation outside this folder

- [`../docs/README.md`](../docs/README.md) — user-facing documentation for the shipped application (what Forge *is*, as opposed to what it's *becoming*)
- [`../.claude/`](../.claude/SESSION_TEMPLATE.md) — session/checkpoint/implementation templates copied at the start of each Claude Code session

## 5. TODO

- [ ] TODO: Assign ownership across all documents in this index — currently every document lists "TODO — assign an owner."
- [ ] TODO: Ratify [00_VISION.md](00_VISION.md) and [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md) with the project owner before Phase 01 implementation begins.

## 6. Cross-references

See section 2 and 3 above — this document exists to link everything else, not to duplicate it.
