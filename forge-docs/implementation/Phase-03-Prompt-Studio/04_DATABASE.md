# Prompt Studio — Database

> **Purpose:** Data model changes required for this phase.
> **Scope:** Schema and migration planning only. Service logic lives in 03_BACKEND.md.
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** Accepted — approved alongside [`01_SPEC.md`](01_SPEC.md) 2026-07-22.
> **Last Updated:** 2026-07-22

---

## 1. New or modified tables

Two new tables, both new SQLModel classes in `backend/app/models/prompt_studio.py`. No existing table is modified.

**`prompts`** (`class Prompt`):

| Column | Type | Notes |
|---|---|---|
| `id` | `str` (UUID), PK | `default_factory=new_id`, matching every other model's id convention |
| `name` | `str`, max 200 | required |
| `description` | `str \| None`, max 1000 | optional |
| `body` | `str`, max 20,000 | required; current content |
| `variables_json` | `str` | JSON-encoded `list[PromptVariable]`, default `"[]"` — see §1.1 |
| `tags_json` | `str` | JSON-encoded `list[str]`, default `"[]"`, max 10 tags / 30 chars each |
| `version_number` | `int` | default `1`; current version's number |
| `created_at` | `datetime` | `default_factory=utcnow` |
| `updated_at` | `datetime` | `default_factory=utcnow`, updated on every metadata or content change |

**`prompt_versions`** (`class PromptVersion`):

| Column | Type | Notes |
|---|---|---|
| `id` | `str` (UUID), PK | |
| `prompt_id` | `str`, FK → `prompts.id`, indexed | |
| `version_number` | `int` | the version this row snapshots |
| `body` | `str` | snapshot at that version |
| `variables_json` | `str` | snapshot at that version |
| `note` | `str \| None`, max 200 | auto-generated (`"Initial version"`, `"Edited"`, `"Restored from v2"`, `"Duplicated from ..."`) — never user-authored free text in this phase |
| `created_at` | `datetime`, indexed | `default_factory=utcnow` |

**§1.1 `variables_json` shape** — a JSON array of objects matching this structure (validated at the Pydantic layer, not enforced by SQLite itself, same pattern as `ProjectInitGeneration.config`):

```json
[
  {
    "name": "audience",
    "type": "string",
    "required": true,
    "default": null,
    "description": "Who the summary is written for"
  }
]
```

`type` is one of `"string" | "number" | "boolean"`. `name` must be unique within the array and match `^[A-Za-z_][A-Za-z0-9_]{0,63}$` (enforced by the Pydantic schema in `06_API.md` §2, not a database constraint — SQLite has no native JSON-array uniqueness/regex constraint mechanism, and every other JSON-blob column in the app, e.g. `ProjectInitGeneration.config`, follows the same "validate at the Pydantic boundary, store as an opaque JSON string" pattern).

## 2. Relationships

- `Prompt.versions: list["PromptVersion"]` — a one-to-many `Relationship`, `sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "PromptVersion.created_at.desc()"}` — this is the exact same relationship shape `Secret.versions` already uses for `SecretVersion` (see `backend/app/models/secrets.py`), applied to a new, unrelated table pair. No foreign key exists from `Prompt`/`PromptVersion` to any other feature's table (Vault/Secrets, Notes, Documents, Project Init) — Prompt Studio is fully standalone data, per [`01_SPEC.md`](01_SPEC.md) §4's explicit note that it shares no table with Phase 05.
- `PromptVersion.prompt_id` is a plain indexed foreign key (`Field(foreign_key="prompts.id", index=True)`) with `ON DELETE CASCADE` semantics enforced at the ORM/service layer via the cascade relationship above — consistent with how `SecretVersion.secret_id` already works (SQLite's own FK-cascade enforcement is not relied on independently of the ORM-level cascade, matching existing precedent).
- No unique database constraint is added on `(prompt_id, version_number)` — the service layer is the sole writer of that pair and always increments monotonically in a single code path (`03_BACKEND.md` §2), the same trust boundary every other service-layer-owned invariant in this codebase already relies on (e.g. `ProjectInitGeneration`'s `created_at` ordering).

## 3. Migration plan

One new, additive-only Alembic migration: `backend/alembic/versions/0005_prompt_studio.py` (next in sequence after `0004_project_init.py`), following that migration's exact template shape:

- `revision = "0005"`, `down_revision = "0004"`.
- `upgrade()`: guarded fresh-install check via `sa.inspect(bind).get_table_names()` — `if "prompts" not in ...: op.create_table("prompts", ...)`, same for `"prompt_versions"`, plus `op.create_index()` for `prompt_versions.prompt_id` and `prompt_versions.created_at`. The guard exists because `SQLModel.metadata.create_all()` (run once, at `0001`, for any brand-new install) will already have created both tables once `Prompt`/`PromptVersion` are registered in `app/models/__init__.py` — only databases upgrading across this release boundary need the explicit `create_table` calls, exactly as documented for `0004_project_init.py`.
- `downgrade()`: `op.drop_index()` (both indexes) then `op.drop_table("prompt_versions")` then `op.drop_table("prompts")` (child before parent, matching `0004`'s ordering).
- No modification to any existing migration or existing table — this is a strictly additive migration, per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2 ("migrations are explicit after the initial one") and the "One migration per phase. Additive only" rule in [`../../14_IMPLEMENTATION_PLAYBOOK.md`](../../14_IMPLEMENTATION_PLAYBOOK.md) §3.
- Tested per the playbook's own requirement: the migration must run cleanly on `docker compose up` boot against both a fresh database and a database still at `0004` (Milestone 3 integration testing, see [`07_TESTING.md`](07_TESTING.md) §1).

## 4. Data lifecycle

Prompts and their versions persist indefinitely, exactly like Vault/Secrets, Notes, and Documents — this is durable user content, not scratch/TTL data like Ingest's conversion working files. There is no automatic pruning of old versions in this phase (an unbounded, append-only version history is the explicit design in [`01_SPEC.md`](01_SPEC.md) §3.7 and the accepted risk in [`README.md`](README.md) Risks) — a future phase could add version-pruning/squashing if real usage shows it's needed, but that is not speculatively built here.

## 5. TODO

- [ ] None — this document is filled in for the specification review pass. This phase does introduce schema changes (stated explicitly, per this file's own template instruction): two new tables, no modification to any existing one.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [../../../docs/Database.md](../../../docs/Database.md)
- [../../decisions/README.md](../../decisions/README.md)
