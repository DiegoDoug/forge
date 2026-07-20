# Implementation Phases

> **Purpose:** Index of every FDK implementation phase — the buildable work that realizes the roadmap in [`../02_ROADMAP.md`](../02_ROADMAP.md).
> **Scope:** Index only. Each phase owns its own full spec in its own folder.
> **Ownership:** TODO — assign an owner.
> **Status:** Draft — all 8 phases are template scaffolds, none yet authorized for implementation
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../02_ROADMAP.md](../02_ROADMAP.md)
> **Supersedes:** —

---

## 1. Phases

| # | Phase | Status |
|---|-------|--------|
| 01 | [Workbench](Phase-01-Workbench/README.md) | Not started — spec placeholder |
| 02 | [Project Initialization Engine](Phase-02-Project-Initialization-Engine/README.md) | Not started — spec placeholder |
| 03 | [Prompt Studio](Phase-03-Prompt-Studio/README.md) | Not started — spec placeholder |
| 04 | [Universal Converter](Phase-04-Universal-Converter/README.md) | Not started — spec placeholder |
| 05 | [Model Playground](Phase-05-Model-Playground/README.md) | Not started — spec placeholder |
| 06 | [Projects](Phase-06-Projects/README.md) | Not started — spec placeholder |
| 07 | [Knowledge Hub](Phase-07-Knowledge-Hub/README.md) | Not started — spec placeholder |
| 08 | [Developer Toolkit](Phase-08-Developer-Toolkit/README.md) | Not started — spec placeholder |

## 2. Shape of every phase folder

Each `Phase-XX-Name/` contains the same 12 files:

`README.md`, `CURRENT_STATE.md`, `01_SPEC.md`, `02_UI.md`, `03_BACKEND.md`, `04_DATABASE.md`, `05_COMPONENTS.md`, `06_API.md`, `07_TESTING.md`, `08_ACCEPTANCE.md`, `09_IMPLEMENTATION_TASKS.md`, `IMPLEMENT.md`.

A phase may add extra numbered docs beyond this base 12 when its design introduces a contract that doesn't fit an existing file — e.g. Phase 01 (Workbench) adds `12_PANEL_INTERFACE.md` to specify the `WorkbenchPanel` contract (per [ADR-0002](../decisions/0002-workbench-panel-architecture.md)). This is the exception, not the norm — don't add a numbered doc speculatively; only when a phase's own spec work surfaces a real need for one.

See [`../11_PROJECT_STRUCTURE.md`](../11_PROJECT_STRUCTURE.md) §5 for how this maps onto the repository as a whole.

## 3. Before starting a phase

A phase is not authorized for implementation until its `01_SPEC.md` and `08_ACCEPTANCE.md` are filled in (not template placeholders) — see [`../09_CLAUDE_CODE_RULES.md`](../09_CLAUDE_CODE_RULES.md) §1.

## 4. TODO

- [ ] TODO: Update the Status column as each phase moves from spec placeholder → authorized → in progress → complete.

## 5. Cross-references

- [../02_ROADMAP.md](../02_ROADMAP.md)
- [../09_CLAUDE_CODE_RULES.md](../09_CLAUDE_CODE_RULES.md)
- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
