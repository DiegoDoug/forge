# Contributing

## Adding a new tool/feature

Using a hypothetical "Base64 image inspector" utility as an example:

**Backend** (skip if the feature is purely client-side, like most of
Converters/Utilities):

1. If it needs persistence, add a model in `app/models/`, then write an
   Alembic migration (`alembic revision --autogenerate -m "..."`, review the
   output).
2. Add Pydantic request/response schemas in `app/schemas/<feature>.py`.
3. Add business logic in `app/services/<feature>/service.py` — this is what
   gets unit-tested, not the route.
4. Add a router in `app/api/routes/<feature>.py`. Gate it with
   `dependencies=[AuthDep]` unless it's genuinely public (health/setup/auth
   only, currently).
5. Register the router in `app/api/router.py`.

**Frontend**:

1. Add `features/<feature>/api.ts` — typed fetch functions and React Query
   hooks. This is the *only* file that knows the endpoint shapes.
2. Add feature components in `features/<feature>/*.tsx`. Reuse
   `components/tool-card.tsx` and `components/output-field.tsx` for
   single-purpose tool panels (see any file in `features/generators/` or
   `features/crypto/` for the pattern) — most Converters/Utilities tools are
   this shape: a `ToolCard` with an input, an action, and an `OutputField`.
3. Add a page in `app/(app)/<feature>/page.tsx` (or a tab within an existing
   page — see `app/(app)/crypto/page.tsx` for the tabbed-panel pattern).
4. Add it to `lib/nav-registry.ts` if it's a top-level section — this
   single list drives both the sidebar and the ⌘K command palette.

## Before submitting

- `npm run build` in `frontend/` must pass (it runs `tsc` as part of the
  Next.js build) — **don't** run this at the same time as `npm run dev`,
  they corrupt each other's `.next/` cache.
- Exercise new endpoints directly (curl, or the interactive docs at
  `/docs`) — don't rely on the UI alone to prove a backend change works.
- No placeholder/mocked implementations. If something's genuinely
  out of scope for a change, leave it out rather than stub it — see
  [DecisionLog.md](DecisionLog.md) for examples of intentionally-deferred
  scope (PGP) and how that was communicated instead of faked.

## Code style

- Backend: type-annotated Python, `from __future__ import annotations`
  **except** in files with SQLModel `Relationship()` fields (see
  `app/models/vault.py` — future annotations breaks forward-reference
  resolution for generic relationship types like `list["Secret"]` in
  combination with the SQLAlchemy version this project pins).
- Frontend: TypeScript, no `any`. Prefer composing shadcn primitives over
  raw HTML for anything interactive (dialogs, selects, etc.) — see
  [Development.md](Development.md) for Base UI's `render` prop composition
  pattern.
- No commented-out code, no `TODO` placeholders left in shipped code — open
  an issue instead.
