# Developer Toolkit — Components

> **Purpose:** Frontend component inventory for this phase — what gets built, and what's reused from the existing design system.
> **Scope:** Component-level detail. Screen-level UX lives in 02_UI.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved in principle by the project owner 2026-08-05.
> **Last Updated:** 2026-08-05

---

## 1. New components

Deliberately minimal, per [`01_SPEC.md`](01_SPEC.md) §1 (presentation/navigation consolidation, not a rebuild):

- **`app/(app)/developer-toolkit/page.tsx`** — the new page component. Renders `PageHeader` + top-level `Tabs`, and imports the existing Generators/Crypto/Utilities feature components directly (see §2). Reads the `?tab=` search param (via `useSearchParams`) to preselect the active tab, matching the pattern already used elsewhere in the app for query-param-driven state (e.g. Documents' `?open=` deep link).

That is the only new component this phase introduces. No new `features/developer-toolkit/` directory, no new `api.ts` — see §3.

## 2. Reused components

- **`components/ui/tabs.tsx`** (shadcn/ui `Tabs`/`TabsList`/`TabsTrigger`/`TabsContent`) — already in use on the current Crypto page; reused for the new top-level tab bar.
- **`components/page-header.tsx`** — the same `PageHeader` every other feature page uses.
- Every component already listed in [`01_SPEC.md`](01_SPEC.md) §3 requirement 1, imported unmodified:
  - From `frontend/features/generators/`: `PasswordGenerator`, `UuidGenerator`, `NanoIdGenerator`, `RandomBytesGenerator`, `ApiKeyGenerator`, `JwtSecretGenerator`, `EntropyEstimator`.
  - From `frontend/features/crypto/`: `Base64Tool`, `HashTool`, `AesTool`, `JwtDecodeTool`, `JwtVerifyTool`, `JwtBuildTool`, `RsaTool`, `EccTool`.
  - From `frontend/features/utilities/`: `QrTool`, `ColorTool`, `TimezoneTool`, `ChecksumTool`.

## 3. `features/` structure

No changes to `frontend/features/generators/`, `frontend/features/crypto/`, or `frontend/features/utilities/` — each keeps its own `api.ts` (Generators' and Crypto's typed fetch/React Query hooks; Utilities has none, being pure client-side) exactly as-is, per [`07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §1's "`api.ts` is the only endpoint-shape-aware file" rule — unaffected since no endpoint shape changes. The new page component (`app/(app)/developer-toolkit/page.tsx`) is a page, not a feature, and composes existing feature components — the same role every other multi-feature page (e.g. Workbench) already plays.

No new `frontend/features/developer-toolkit/` directory is created — there is no new business logic, state, or API surface to house there.

## 4. State management

No new TanStack Query hooks. Each tab's content keeps using its existing feature's own hooks (Generators' and Crypto's `api.ts` hooks, Utilities' local `useState`) unmodified. The only new local state is the new page component's active-tab selection (`Tabs`' own controlled/uncontrolled state, initialized from the `?tab=` search param) — not a data-fetching concern, no cache-key/invalidation strategy needed.

## 5. TODO

- [x] `?tab=` value set (`generators` / `crypto` / `utilities`) confirmed 2026-08-05 alongside the route/label/icon/shortcut decisions — these three values follow directly from the approved tab names, and `?tab=` deep links are on the project owner's explicit keep-list.

## 6. Cross-references

- [02_UI.md](02_UI.md)
- [06_API.md](06_API.md)
- [../../05_DESIGN_SYSTEM.md](../../05_DESIGN_SYSTEM.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
