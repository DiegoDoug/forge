# Phase 11 — Database Design

> **Purpose:** Schema changes required (and confirmation of what is NOT required) for Phase 11.
> **Status:** Draft — pending Authorization.
> **Last Updated:** 2026-08-18

---

## 1. Does Phase 11 need schema changes?

**Yes — one additive table, one additive column.** Determined by inspection, not assumed:

- Notes, Documents, Projects, Knowledge Hub (tags, links) need **zero** schema changes — every MCP tool in `06_API.md` reuses the existing `Note`, `Document`, `Project`, `Tag`, `NoteTagLink`, `DocumentTagLink`, `KnowledgeLink` models exactly as they exist today.
- Forge has no existing individually-revocable credential table (session tokens are stateless HMACs — `01_SPEC.md` §4.1) — one new table is required to back MCP token issuance/revocation.
- `ActivityLog` has no `source` column (everything today is implicitly UI-originated) — one new nullable column is required to distinguish MCP-originated audit entries (`01_SPEC.md` §4.5).

## 2. New model: `McpToken`

`backend/app/models/mcp_token.py`:

```python
class McpToken(SQLModel, table=True):
    __tablename__ = "mcp_tokens"

    id: str = Field(default_factory=new_id, primary_key=True)
    name: str = Field(max_length=100)
    token_hash: str = Field(index=True)          # salted hash, never the plaintext token
    scopes: str                                    # comma-separated: "read,write,delete"
    created_at: datetime = Field(default_factory=utcnow)
    last_used_at: datetime | None = Field(default=None)
    revoked_at: datetime | None = Field(default=None)
```

Conventions matched: UUID-hex string PK via `new_id()` (`models/base.py`), naive-UTC timestamps via `utcnow()` (`models/base.py`), no ORM-level cascade needed (this table has no children). `token_hash` is indexed for fast lookup on every `/mcp` request; the plaintext token is generated once at creation time, returned to the caller once, and never stored or logged — same principle as `AppConfig.master_password_hash` never storing the master password.

**Must be added to `backend/app/models/__init__.py`'s import list** — migration `0001`'s `SQLModel.metadata.create_all(bind)` bootstrap only picks up models that are imported there; this is a confirmed repository convention, not a guess (see backend research §4).

## 3. `ActivityLog` column addition

```python
# backend/app/models/activity.py — additive
source: str = Field(default="ui", max_length=20)   # "ui" | "mcp"
```

Nullable-with-default so existing rows and existing UI-originated writes need no backfill logic beyond the column default; every route/service call site that already calls `activity.record(...)` continues to work unchanged (implicit `source="ui"`), and only `app/mcp/tools/*.py` call sites pass `source="mcp"` explicitly. `activity.record()`'s signature grows one optional keyword argument, defaulting to `"ui"` — not a breaking change to any existing caller.

## 4. Migration

`backend/alembic/versions/00XX_mcp_tokens.py` (exact number determined at implementation time — current head is `0009_knowledge_hub.py`, so this is expected to be `0010`), following the established idempotent pattern (guarded by `inspector.get_table_names()`/`get_columns()` checks so it's a no-op on fresh installs where `create_all` already created it, per the same pattern as `0002`-`0009`):

```python
def upgrade():
    inspector = inspect(op.get_bind())
    if "mcp_tokens" not in inspector.get_table_names():
        op.create_table(
            "mcp_tokens",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("token_hash", sa.String(), nullable=False),
            sa.Column("scopes", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("last_used_at", sa.DateTime(), nullable=True),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_mcp_tokens_token_hash", "mcp_tokens", ["token_hash"])

    columns = {c["name"] for c in inspector.get_columns("activity_log")}
    if "source" not in columns:
        op.add_column(
            "activity_log",
            sa.Column("source", sa.String(length=20), nullable=False, server_default="ui"),
        )
```

No FTS5 involvement (tokens and activity source are not searchable content). No foreign keys from `mcp_tokens` to anything else — it is a standalone credential table, same independence as `AppConfig`.

## 5. Migration test

Following the existing convention (Phase 07's deliverables list an explicit "migration up/down/up test"), Phase 11 needs the same: `backend/tests/test_mcp_migration.py` (or an addition to an existing migration-test module) verifying `alembic upgrade head` → `downgrade -1` → `upgrade head` leaves the schema consistent, and that running the migration twice (simulating the fresh-install `create_all` case) is a true no-op.

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [07_TESTING.md](07_TESTING.md)
