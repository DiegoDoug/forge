# Prompt Studio — Backend

> **Purpose:** Backend service design for this phase — modules, business logic boundaries, and integration with existing services.
> **Scope:** Backend only. Schema detail lives in 04_DATABASE.md; endpoint contracts live in 06_API.md.
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** Accepted — approved alongside [`01_SPEC.md`](01_SPEC.md) 2026-07-22, including the project-owner's rendering-determinism addition (§2.1).
> **Last Updated:** 2026-07-22

---

## 1. Service boundary

New `backend/app/services/prompt_studio/` subpackage — no existing service is extended. Layout, mirroring `services/project_init/`'s structure (the most recent, most representative full-feature example in the codebase):

```
backend/app/services/prompt_studio/
  __init__.py
  templating.py   # extract_placeholders(body) -> set[str]; substitute(body, values) -> str
  service.py      # create, get, list, update_metadata, update_content, delete,
                  # duplicate, list_versions, get_version, restore_version
backend/app/models/prompt_studio.py     # Prompt, PromptVersion (see 04_DATABASE.md)
backend/app/schemas/prompt_studio.py    # Pydantic request/response DTOs (see 06_API.md §2)
backend/app/api/routes/prompt_studio.py # thin router — see 06_API.md §1
```

## 2. Business logic

**2.1 The shared substitution algorithm** (`templating.py`) — this is the one place the algorithm is implemented; the frontend's client-side preview (per [`02_UI.md`](02_UI.md) §1.1) reimplements the same rule in TypeScript since there is no shared code between frontend and backend (per [`07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) — features/modules don't share runtime code across the Python/TypeScript boundary), so this section is the single source of truth both sides must match:

- Placeholder syntax: `${name}` (Python `string.Template`'s default `$`-based syntax, identifier rule `[A-Za-z_][A-Za-z0-9_]*`). A literal `$` is written as `$$` (escaped), matching `string.Template`'s own rule exactly — no custom escaping logic is invented.
- `extract_placeholders(body: str) -> set[str]`: returns every distinct identifier referenced as `${name}`, using `string.Template.pattern` (the same regex `string.Template` itself uses internally) rather than a hand-rolled regex, so extraction and substitution can never disagree with each other.
- Server-side substitution (used only if/when a future phase needs it — this phase's preview is client-side per §1.1) would use `Template(body).substitute(mapping)`, i.e. **strict** substitution that raises on a missing key, not `safe_substitute`, so a missing required variable is a hard error rather than a silently-empty string.
- **Determinism constraint (project-owner requirement, added at specification review 2026-07-22 — see [`01_SPEC.md`](01_SPEC.md) §3.16):** `templating.py` and its TypeScript mirror perform substitution, escaping, and validation only — nothing else. Neither implementation may ever call `eval`, a Jinja/Mustache-style template engine, or any mechanism that would let a prompt body express a conditional, loop, function call, filter, include, or import. `string.Template` is used specifically because it is structurally incapable of any of that (it has no expression language at all) — this is a property of the tool chosen, not just a policy on top of it. Any future request for conditional/loop logic in a prompt body is an explicit new architectural decision (a new ADR under [`../../decisions/`](../../decisions/README.md)), not an incremental change to this module.

**2.2 Core operations** (`service.py`):

- `create(session, data: PromptCreate) -> Prompt` — validates (via the Pydantic schema, see §4 and `06_API.md` §2) that every `${name}` in `body` is a declared variable name; creates the `Prompt` row and its first `PromptVersion` (version 1, note `"Initial version"`) in the same transaction; calls `activity.record(..., ActivityAction.created, "prompt", prompt.id, f'Created "{name}"')`.
- `get(session, prompt_id) -> Prompt` — raises `NotFoundError` (from `app.core.errors`) if missing.
- `list_prompts(session, search: str | None, tag: str | None) -> list[Prompt]` — filters in Python/SQL over name/description (search) and the `tags_json` column (tag) — no full-text index is introduced for this phase's expected scale (a personal prompt library), consistent with §5/`01_SPEC.md` §5 not adding new search infrastructure.
- `update_metadata(session, prompt_id, data: PromptUpdateMeta) -> Prompt` — updates `name`/`description`/`tags_json` only; does **not** touch `version_number` or create a `PromptVersion` row; calls `activity.record(..., ActivityAction.updated, "prompt", prompt.id, f'Updated "{name}"')`.
- `update_content(session, prompt_id, data: PromptUpdateContent) -> Prompt` — the versioning operation: (1) validates the new `body`'s placeholders against the new `variables` (same rule as create), (2) writes **one new** `PromptVersion` row for the incoming content at `version_number + 1` (note `"Edited"`), (3) overwrites the `Prompt` row's `body`/`variables_json`/`version_number` to match, updates `updated_at`, (4) calls `activity.record(..., ActivityAction.updated, "prompt", prompt.id, f'Saved v{new_version} of "{name}"')`. **Implementation note (corrected during Milestone 2, 2026-07-22):** unlike a naive reading of "snapshot-then-overwrite," this does *not* also re-snapshot the outgoing content — the outgoing content already has its own immutable `PromptVersion` row, written the moment it became current (either by `create()`, or by whichever prior `update_content()`/`restore_version()` call last made it current). Writing a second row for it here would create a duplicate entry with identical content under a reused version number. Exactly one `PromptVersion` row exists per version number at all times. (Secrets' own `update_secret` does re-snapshot the outgoing value on every edit, because `SecretVersion` has no version-number concept to reuse — that's a reasonable design for an un-numbered audit trail, but would produce a redundant duplicate row here now that Prompt Studio tracks explicit version numbers.)
- `delete(session, prompt_id) -> None` — deletes the `Prompt` row; `PromptVersion` rows cascade via the model's `cascade="all, delete-orphan"` relationship (same relationship kwargs Secrets already uses for `SecretVersion`); calls `activity.record(..., ActivityAction.deleted, "prompt", prompt_id, f'Deleted "{name}"')` **before** the row is gone (the name is captured up front, since `ActivityLog.summary` is a plain string snapshot, not a live reference).
- `duplicate(session, prompt_id) -> Prompt` — reads the source prompt's current `body`/`variables_json`/`tags_json`, creates a brand-new `Prompt` (`name = f"{source.name} (copy)"`) with its own fresh `PromptVersion` at version 1 (note `"Duplicated from ..."`, referencing the source's id/name in the note text only — no `source_prompt_id` foreign key is introduced, since the duplicate is explicitly a fully independent entity per [`01_SPEC.md`](01_SPEC.md) §3.10); calls `activity.record(..., ActivityAction.created, "prompt", new_prompt.id, f'Duplicated "{source_name}" as "{new_name}"')`.
- `list_versions(session, prompt_id) -> list[PromptVersion]` — newest-first (matches the `order_by` used by Secrets' `versions` relationship), lightweight shape (no `body`/`variables_json` in the list response — see `04_DATABASE.md` §... / `06_API.md` §2 for the list-vs-detail shape split, mirroring why the prompt list endpoint itself is lightweight).
- `get_version(session, prompt_id, version_id) -> PromptVersion` — full detail (body + variables) for one version; raises `NotFoundError` if the version doesn't belong to `prompt_id` (not just if the id doesn't exist at all — prevents one prompt's version id from being readable via another prompt's URL).
- `restore_version(session, prompt_id, version_id) -> Prompt` — writes **one new** `PromptVersion` row at `version_number + 1` containing `target`'s `body`/`variables_json` (note `f"Restored from v{target.version_number}"`), then applies that content as the prompt's new current `body`/`variables_json`/`version_number` (so restoring never decrements or reuses a version number — history is strictly append-only, matching `01_SPEC.md` §3.9, and nothing is lost since every version already has its own permanent row); calls `activity.record(..., ActivityAction.updated, "prompt", prompt.id, f'Restored v{target.version_number} of "{name}"')`. Same non-redundancy note as `update_content` above — the prompt's pre-restore current content already has its own row and does not need re-snapshotting.

## 3. Integration with existing services

- **`app.services.activity`** — every mutating operation above calls the existing `record(session, action, entity_type, entity_id, summary)` function exactly as-is (no changes to `activity.py`, `ActivityLog` model, or `ActivityAction` enum — `"prompt"` is simply a new `entity_type` string value, not a new enum member). The caller-commits contract is preserved: `service.py` calls `activity.record(...)` then the same function's own `await session.commit()`, matching every existing caller (`project_init`, `documents`, `secrets`).
- **No other existing service is called into.** In particular, this phase does not call `app.core.security.get_vault_crypto()` or reference `Secret`/`SecretVersion` — prompt bodies and variable values are not treated as secret data (see `01_SPEC.md` §5 and `06_API.md` §3 Security Considerations for the explicit reasoning) and are stored as plain columns, matching Documents/Notes, not encrypted like Vault/Secrets.

## 4. Architectural compliance

- [x] Routers stay thin — `prompt_studio.py`'s router functions only parse path/query params, call one `service.py` function, and shape the response through a `schemas/prompt_studio.py` model; every branch of business logic described in §2 lives in `service.py` (per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §1.1/§2).
- [x] No cross-feature imports introduced — `services/prompt_studio/` imports only `app.core`, `app.database`, `app.models`, `app.schemas`, and `app.services.activity` (the one pre-approved cross-cutting service every feature is allowed to call, same as every existing feature).
- [x] No new external dependency — `string.Template` (stdlib), `@monaco-editor/react` and the `diff` npm package (both already in [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) §1) cover every requirement in [`01_SPEC.md`](01_SPEC.md). Nothing needs to be added to that table.
- [x] Models are the schema source of truth — `Prompt`/`PromptVersion` are defined once in `app/models/prompt_studio.py`; the corresponding Alembic migration (`04_DATABASE.md` §3) is additive-only.
- [x] ORM objects are never returned directly — every route response is shaped through a `schemas/prompt_studio.py` Pydantic model (per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §1.1's "never expose ORM objects directly" hard rule).

## 5. TODO

- [ ] None — this document is filled in for the specification review pass.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
