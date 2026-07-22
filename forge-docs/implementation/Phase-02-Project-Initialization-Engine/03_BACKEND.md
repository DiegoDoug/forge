# Project Initialization Engine — Backend

> **Purpose:** Backend service design for this phase — modules, business logic boundaries, and integration with existing services.
> **Scope:** Backend only. Schema detail lives in 04_DATABASE.md; endpoint contracts live in 06_API.md.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Accepted.
> **Last Updated:** 2026-07-22

---

## 1. Service boundary

New subpackage: `backend/app/services/project_init/`, following the one-subpackage-per-feature convention (`services/notes/`, `services/crypto/`, etc.):

```
backend/app/services/project_init/
├── __init__.py
├── catalog.py       # the two TemplateKind definitions + their field schemas + output file lists
├── renderer.py       # string.Template substitution: (kind, validated input) -> {filename: content}
├── zipper.py         # {filename: content} -> zip bytes (stdlib zipfile, in-memory)
├── service.py        # orchestration: validate -> render -> persist history -> log activity
└── templates/
    ├── fdk_phase/     # the 13 file templates (README.md.tmpl, 01_SPEC.md.tmpl, ... 10_RELEASE_NOTES.md.tmpl, IMPLEMENT.md.tmpl)
    └── ai_instructions/  # CLAUDE.md.tmpl, AGENTS.md.tmpl, instructions.md.tmpl
```

The `forge-docs/templates/project-initialization/` directory (FDK docs) is updated to point here as the actual template content location, per its own note that engine logic and content belong in `backend/app/services/`, not in `forge-docs/`.

## 2. Business logic

Core operations, all synchronous (no background job queue — rendering plain text from small templates is sub-millisecond work, unlike Ingest's document conversion pipeline):

1. **`get_catalog() -> TemplateCatalog`** — static, in-memory description of both kinds: their field schema (for the frontend to render the right form) and their output filenames. No database read.
2. **`generate(session, request: GenerateRequest) -> ProjectInitGeneration`** —
   - Validates `request` against the matching kind's field schema (Pydantic; see [06_API.md](06_API.md)).
   - Calls `renderer.render(kind, request.config) -> dict[str, str]` (filename → rendered text content).
   - Persists one `ProjectInitGeneration` row (kind, name, config JSON, created_at) — the row stores *inputs*, not the rendered output, matching the Documents export-on-demand pattern (`services/documents/export.py`): output is deterministically reproducible from stored config plus the fixed template catalog.
   - Calls `activity.record(session, ActivityAction.created, "project_init_generation", generation.id, f'Generated "{name}"')`.
   - Commits, returns the persisted row.
3. **`render_zip(kind, config) -> bytes`** — shared by the initial `generate` response and by `download`; calls `renderer.render` then `zipper.to_zip`.
4. **`list_history(session, limit=20) -> list[ProjectInitGeneration]`** — most recent first.
5. **`get_or_404(session, generation_id) -> ProjectInitGeneration`** — mirrors the `_get_or_404` pattern used in `services/notes/service.py`.
6. **`delete(session, generation_id) -> None`** — deletes the history row only; no cascade, no file cleanup (nothing is stored on disk).

## 3. Integration with existing services

- **`app.services.activity`** — every successful `generate()` call records one `ActivityLog` row, so Recent Activity (Workbench panel and any future consumer) picks it up with zero changes to that code.
- No other existing service is called into or extended. This phase does not read from or write to Notes, Vault/Secrets, Documents, Ingest, or Settings.

## 4. Architectural compliance

- [x] Routers stay thin — `api/routes/project_init.py` only parses the request, calls `service.*`, and shapes the HTTP response; all logic above lives in `services/project_init/`.
- [x] No cross-feature imports introduced — `services/project_init/` imports only `app.services.activity`, `app.models.activity`, `app.core.errors`, and stdlib.
- [x] No new external dependency. Rendering uses stdlib `string.Template`; zipping uses stdlib `zipfile`. Both already implicitly available (Python stdlib ships with every backend base image already in [`06_TECH_STACK.md`](../../06_TECH_STACK.md)) — nothing to add to that table.
- [x] Schema change is a single additive migration (`0004_project_init.py`) — see [04_DATABASE.md](04_DATABASE.md).

## 5. TODO

None.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
