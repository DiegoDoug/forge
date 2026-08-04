# Knowledge Hub — Components

> **Purpose:** Frontend component inventory for this phase — what gets built, and what's reused from the existing design system.
> **Scope:** Component-level detail. Screen-level UX lives in 02_UI.md.
> **Ownership:** Project owner (scope decisions confirmed 2026-08-04)
> **Status:** Confirmed — `01_SPEC.md` §7's four open questions resolved 2026-08-04; ready for implementation pending final review
> **Last Updated:** 2026-08-04

---

## 1. New components

All under `frontend/features/knowledge/`:

| Component | Responsibility |
|---|---|
| `knowledge-filter-bar.tsx` | Query input, type selector, tag multi-select, project selector; owns URL-param sync. |
| `knowledge-result-list.tsx` | Renders the result rows, the four states from `02_UI.md` §3, and the truncation notice. |
| `knowledge-result-row.tsx` | One row: type badge, title, excerpt, tag chips, project chip, updated-at. Single keyboard target. |
| `knowledge-tag-picker.tsx` | Assign/remove tags on an item, with inline create. Used by the Documents sidebar and the Notes card, **not** by the Hub page. |
| `knowledge-link-panel.tsx` | Linked-items list plus an add-link picker and per-row remove. Used by the same two hosts. |
| `knowledge-link-picker.tsx` | Searches knowledge items to pick a link target; excludes the current item so self-linking is impossible in the UI as well as the API. |

## 2. Reused components

Reused as-is from `frontend/components/` and the existing design system — nothing here is reinvented:

- `components/ui/select.tsx` (type/project pickers) — **apply the children-as-function workaround**, per `02_UI.md` §5's caveat.
- `components/ui/badge.tsx` / chip primitive for type badges and tag chips.
- `components/ui/input.tsx` for the query field.
- `components/ui/button.tsx`, `dialog.tsx` / popover for the link picker surface.
- `components/ui/skeleton.tsx` for the loading state.
- Existing empty-state / error-state patterns from the Projects and Secrets list pages — matched, not re-derived.
- `sonner` toasts for transient success only; validation errors render inline (`02_UI.md` §3).
- `date-fns` for relative timestamps, as elsewhere.

No new npm dependency. Nothing to add to `06_TECH_STACK.md`.

## 3. `features/` structure

```
frontend/features/knowledge/
  api.ts                      # the ONLY file aware of backend endpoint shapes
  knowledge-filter-bar.tsx
  knowledge-result-list.tsx
  knowledge-result-row.tsx
  knowledge-tag-picker.tsx
  knowledge-link-panel.tsx
  knowledge-link-picker.tsx
```

Page: `frontend/app/(app)/knowledge/page.tsx`.

Per `07_CODING_STANDARDS.md` §1, `api.ts` is the only file that knows endpoint shapes. Components take typed props and never call `fetch` directly.

**Host integration (existing files, additive edits only):**

- `frontend/features/documents/document-sidebar.tsx` — mounts `knowledge-tag-picker` and `knowledge-link-panel`.
- `frontend/features/notes/note-card.tsx` (or its expanded state, per `02_UI.md` §1.2's open design note) — same two controls.
- `frontend/lib/nav-registry.ts` — one new `NavItem`.

> **Cross-feature import check:** Documents and Notes importing from `features/knowledge/` is a feature importing a *composition layer*, the same shape as the backend question in `03_BACKEND.md` §2.2. `07_CODING_STANDARDS.md` forbids features importing each other's internals; `knowledge` is not "another feature's internals" but a shared surface, so this is judged acceptable — but it is the reason these components live in `features/knowledge/` rather than being duplicated into each host. If review disagrees at T9, the fallback is to promote the two shared controls into `frontend/components/` instead.

## 4. State management

TanStack Query, matching existing conventions.

| Hook | Key | Invalidated by |
|---|---|---|
| `useKnowledgeList(filters)` | `["knowledge", filters]` | tag assign/unassign, link create/delete, and any note/document mutation |
| `useKnowledgeTags()` | `["knowledge", "tags"]` | tag assign/unassign (counts change) |
| `useKnowledgeLinks(type, id)` | `["knowledge", "links", type, id]` | link create/delete on either endpoint of the link |

Invalidation notes:

- Creating or deleting a link must invalidate **both** endpoints' link queries, not just the initiating one — the link is visible from both sides (`01_SPEC.md` FR15).
- Tag mutations invalidate the tag list as well as the item list, because `GET /api/knowledge/tags` returns counts.
- Filters are part of the query key, so switching filters is a normal cache miss rather than manual refetch plumbing.

## 5. Cross-references

- [02_UI.md](02_UI.md)
- [06_API.md](06_API.md)
- [../../05_DESIGN_SYSTEM.md](../../05_DESIGN_SYSTEM.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
