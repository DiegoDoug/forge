# Project Initialization Engine — Release Notes

> **Purpose:** User-facing summary of what shipped in this phase, for `../../../docs/Roadmap.md`-style consumption once released.
> **Scope:** This phase only.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Content-complete for the implemented feature set. Formally finalized at the Released stage (per `13_PHASE_LIFECYCLE.md`), after Release Candidate audit + Owner Sign-off.
> **Last Updated:** 2026-07-22

---

## Summary

Forge gains a **Project Init** feature (`/project-init`): a template-driven scaffolding engine that generates two kinds of file bundles as a zip download —

1. **FDK Phase Scaffold** — a new `Phase-XX-Name/` folder matching Forge's own 12-file FDK structure, for maintainers extending the FDK itself.
2. **AI Project Instructions** — `CLAUDE.md` / `AGENTS.md` / `instructions.md`, pre-filled with a project's name, description, tech stack, and conventions, for use in any project.

Both are pure server-side templating — no outbound network calls, no filesystem writes outside Forge's own database, fully usable on an offline LAN deployment.

## What's new

- New `/project-init` page, reachable from the sidebar and the command palette.
- A generation history (last 20) with re-download and delete, and matching Recent Activity entries.
- New API surface: `GET /api/project-init/catalog`, `POST /api/project-init/generate`, `GET /api/project-init/history`, `GET /api/project-init/{id}/download`, `DELETE /api/project-init/{id}`.
- New table `project_init_generations` (Alembic migration `0004_project_init`).

## What's not included (tracked, not dropped)

- Writing generated files directly to a filesystem path (download-only by design — see [01_SPEC.md §5](01_SPEC.md)).
- A user-facing template editor / bring-your-own-template system.
- Any LLM-assisted content generation.
- Workbench panel/pin registration for this feature (nav-registry reachability only).

## Upgrade notes

Additive migration only — no existing table, route, or model changes. No new environment variables or configuration required.

## Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
