# Project Initialization Templates

> **Purpose:** Document the scaffolding templates Phase 02 (Project Initialization Engine) generates — the actual template *content* lives as code under `backend/app/services/project_init/templates/`, per §2 below.
> **Scope:** Documentation of template scope only — no engine logic or template content lives in `forge-docs/`.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Spec confirmed — see [`../../implementation/Phase-02-Project-Initialization-Engine/01_SPEC.md`](../../implementation/Phase-02-Project-Initialization-Engine/01_SPEC.md).
> **Version:** 0.2.0
> **Last Updated:** 2026-07-22
> **Depends On:** [`../../implementation/Phase-02-Project-Initialization-Engine/01_SPEC.md`](../../implementation/Phase-02-Project-Initialization-Engine/01_SPEC.md)
> **Supersedes:** v0.1.0 of this document (pre-spec placeholder).

---

## 1. Confirmed contents

Two template kinds, both fixed/built-in (no user-facing template editor — see [01_SPEC.md §5](../../implementation/Phase-02-Project-Initialization-Engine/01_SPEC.md)):

- **FDK Phase Scaffold** — the `implementation/Phase-XX-Name/` 12-file structure documented in [../../02_ROADMAP.md](../../02_ROADMAP.md) / [../../11_PROJECT_STRUCTURE.md §5](../../11_PROJECT_STRUCTURE.md).
- **AI Project Instructions** — `CLAUDE.md`, `AGENTS.md`, `instructions.md` for an arbitrary target project.

## 2. Where the actual template content lives

`backend/app/services/project_init/templates/fdk_phase/*` and `backend/app/services/project_init/templates/ai_instructions/*` — code, not FDK documentation, per this document's own original scope note ("no engine logic"). This `forge-docs/templates/project-initialization/` directory documents *what* the engine generates; it does not itself contain the template files.

## 3. TODO

None — scope confirmed by [`01_SPEC.md`](../../implementation/Phase-02-Project-Initialization-Engine/01_SPEC.md).

## 3. Cross-references

- [../README.md](../README.md)
- [../../implementation/Phase-02-Project-Initialization-Engine/README.md](../../implementation/Phase-02-Project-Initialization-Engine/README.md)
