# Workbench — Database

> **Purpose:** Data model changes required for this phase.
> **Scope:** Schema and migration planning only. Service logic lives in 03_BACKEND.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — third full pass (compatibility-migration alias approach), pending confirmation
> **Version:** 0.3.0
> **Last Updated:** 2026-07-20
> **Depends On:** [01_SPEC.md](01_SPEC.md), [../../../docs/Database.md](../../../docs/Database.md), [../../decisions/0003-workbench-single-row-layout.md](../../decisions/0003-workbench-single-row-layout.md), [../../decisions/0006-vault-renamed-to-secrets.md](../../decisions/0006-vault-renamed-to-secrets.md)
> **Supersedes:** v0.2.0 of this document (Secrets rename assumed a flat table rename)

---

## 1. New or modified tables

One new table, following the single-row config pattern established by `app_config` and ratified for this use by [ADR-0003](../../decisions/0003-workbench-single-row-layout.md):

```python
class WorkbenchLayout(SQLModel, table=True):
    """Single-row table (id is always 1) holding the instance-wide Workbench layout."""

    __tablename__ = "workbench_layout"

    id: int = Field(default=1, primary_key=True)
    panels: str = Field(default="[]")         # JSON-encoded list[{"type": str, "visible": bool}], in display order
    pinned_tools: str = Field(default="[]")   # JSON-encoded list[str] of tool keys, in pin order
    updated_at: datetime = Field(default_factory=utcnow)
```

Renamed from `widgets` to `panels` (previously the column was framed around a fixed `WidgetType` enum; per [ADR-0002](../../decisions/0002-workbench-panel-architecture.md) the column now stores opaque `type` strings the database itself has no fixed vocabulary for — validation of *structure* still happens in the service layer per [`03_BACKEND.md`](03_BACKEND.md) §2, but there is no database-level or Python-enum-level constraint on which `type` values are legal, since that's a frontend-registry fact).

`panels` and `pinned_tools` remain JSON-encoded `TEXT` (SQLite has no native JSON column type in this stack).

**No new table for the forward-looking tool catalog** (`WORKBENCH_TOOL_KEYS` in [`03_BACKEND.md`](03_BACKEND.md) §3) — it is a Python constant, not persisted data, for the same reason `nav-registry.ts` is a frontend constant: it describes what the *code* knows how to render, not instance state.

No existing tables (`ActivityLog`, `Note`) are modified. Per [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)'s compatibility-migration approach, the Vault → Secrets rename touches the database layer **only if safe**: if `vault`'s table/columns can be renamed without a risky data migration, do so as part of the rename task; otherwise the `Secrets` model keeps `__tablename__ = "vault"` and the rename stays at the application layer only. Either way, this is scoped to the rename task, not designed further in this document.

## 2. Relationships

None. `WorkbenchLayout` has no foreign keys — it references only opaque tool-key and panel-type strings, not rows in other tables. This mirrors `AppConfig`.

## 3. Migration plan

One explicit Alembic migration adding the `workbench_layout` table (`id`, `panels`, `pinned_tools`, `updated_at`). No data migration needed — the row is created lazily on first access via the get-or-create pattern in `get_layout()` (per [`03_BACKEND.md`](03_BACKEND.md) §2).

No direct schema edits — per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2.

## 4. Data lifecycle

Persists indefinitely, like `AppConfig`. Overwritten in place on every layout change and on reset; no history/versioning of past layouts is kept.

## 5. TODO

- [ ] TODO: Confirm the JSON-in-TEXT approach is acceptable rather than normalizing into child tables — unchanged judgment call from v0.1.0 of this document, still open. Implemented as specified (JSON-in-TEXT) pending that confirmation, not a design change.
- [x] TODO: Write and review the actual Alembic migration once this document is confirmed. — Done: `backend/alembic/versions/0003_workbench_layout.py` (T3), following the same idempotent-guard pattern as `0002_documents.py`.
- [x] TODO: Coordinate with the Vault → Secrets rename task ([ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)) on migration ordering if both land in the same implementation session. — Resolved: T1 (the rename) landed first; it made no database changes (the `secrets`/`folders`/`tags`/`secret_versions` tables were already correctly named), so no ordering conflict existed by the time this migration was written.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md)
- [../../../docs/Database.md](../../../docs/Database.md)
- [../../decisions/README.md](../../decisions/README.md)
