# Frontend Reimagine — Codebase Audit

> **Purpose:** The evidence base for Phase 09. Every claim here is grounded in a specific file, line, or runtime measurement taken from the repository on 2026-08-06 — nothing is inferred from screenshots or assumed from convention.
> **Scope:** The shipped Forge frontend as of commit `2b9e40d` (post-Phase-08 freeze), plus the backend contracts the frontend consumes.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Complete — discovery pass, session 1.
> **Version:** 1.0.0
> **Last Updated:** 2026-08-06
> **Depends On:** —

---

## 1. Method

This audit was produced by direct inspection, not delegation:

- Full enumeration of `frontend/app/`, `frontend/components/`, `frontend/features/`, `frontend/lib/`, `frontend/hooks/`.
- Every one of the 17 route files read in full.
- `next.config.ts`, `components.json`, `package.json`, `app/globals.css`, `app/layout.tsx` read in full.
- Backend route modules enumerated and endpoint counts taken per module; `services/search/service.py` and `services/knowledge/service.py` read to settle a scope question.
- **Runtime verification**: the frontend dev server was started and computed styles and network responses were measured in a real browser. Two of the findings below (§3.1, §3.2) are runtime-verified, not static inferences.
- **Re-verified at T0.5a (2026-08-06)**, while fixing §3.1. Probing the running app narrowed the typography defect: `--font-mono` was **not** broken, contrary to this document's first draft. See the correction inside §3.1. The `/system/status` finding (§3.2) was *widened* — `docker/nginx.conf` does not route it either, so production has the same failure. See §3.2's addendum.
- `npx tsc --noEmit` run to establish a clean type baseline before any change.

## 2. What Forge's frontend actually is

### 2.1 Stack

| | |
|---|---|
| Framework | Next.js 15.5.20 (App Router, Turbopack), React 19.1.0, TypeScript 5 |
| Styling | Tailwind CSS v4 (`@tailwindcss/postcss`), no `tailwind.config` — CSS-first config in `globals.css` |
| Components | shadcn/ui on Base UI (`@base-ui/react` 1.6.0), style `base-nova`, base color `neutral` |
| Icons | `lucide-react` |
| Data | TanStack Query v5, one typed fetch wrapper (`lib/api-client.ts`) |
| Forms | `react-hook-form` + `zod` v4 |
| Theming | `next-themes`, `attribute="class"`, `defaultTheme="dark"`, `enableSystem` |
| Notable deps | `cmdk`, `@dnd-kit`, `@monaco-editor/react`, `react-markdown`, `sonner`, `framer-motion`, `papaparse`, `diff`, `yaml`, `fast-xml-parser`, `qrcode.react` |

**Type baseline: clean.** `npx tsc --noEmit` exits 0 with no output.

### 2.2 Shape

```
frontend/
  app/(auth)/      2 routes — setup, unlock. No shell, no auth.
  app/(app)/       15 routes — every real surface, behind AuthGate + shell.
  components/      8 shared app components + 40 shadcn primitives + app-shell + command-palette
  features/        18 feature folders — each owns api.ts + its own components
  lib/             api-client, nav-registry, format, query-provider, utils
  hooks/           use-clipboard
```

Roughly 11,500 lines of frontend source. The architecture is **sound**: `lib/api-client.ts` is the single fetch boundary, each `features/*/api.ts` owns its endpoint shapes, features do not import each other's internals, and page components compose feature components. Phase 09 preserves this structure entirely.

### 2.3 Route inventory (17 routes)

| Route | Purpose | Key params | Feature deps | Notes |
|---|---|---|---|---|
| `/setup` | First-run master password | — | auth | No shell |
| `/unlock` | Session unlock | — | auth | No shell |
| `/` | Workbench — panels, pinned tools | — | workbench, notes, projects | Landing route |
| `/secrets` | Encrypted secret store | `open`, `project_id`, `new` | secrets, projects | 13 endpoints |
| `/notes` | Sticky-note board | `open`, `project_id`, `new` | notes, projects | dnd-kit board |
| `/documents` | Rich-text editor + history | `open`, `project_id` | documents, knowledge, projects | **No PageHeader** |
| `/knowledge` | Notes+documents browser | `q`, `type`, `tag_id`, `project_id` | knowledge | All state in URL |
| `/projects` | Project list | `new` | projects | |
| `/projects/[id]` | Project detail | — | projects, secrets, notes, documents | Only dynamic segment |
| `/prompt-studio` | Prompt authoring + versions | `open` | prompt-studio | **Best responsive impl** |
| `/model-playground` | LLM provider comparison | — | model-playground | 9 endpoints |
| `/project-init` | FDK scaffold generation | — | project-init | |
| `/converters` | Text/data/document conversion | — | converters, ingest | `/ingest` redirects here |
| `/developer-toolkit` | Generators + crypto + utilities | `tab` | generators, crypto, utilities | 3 routes redirect here |
| `/search` | Cross-entity search | `q` | search | **Orphaned — see §4.1** |
| `/settings` | Theme, password, backup, about | — | settings, auth | |

Five compatibility redirects in `next.config.ts`, all `permanent: false`: `/vault`, `/ingest`, `/generators`, `/crypto`, `/utilities`.

**Feature folders without a route of their own** (composed into other pages): `crypto`, `generators`, `utilities` → `/developer-toolkit`; `ingest` → `/converters`; `workbench` → `/`; `auth` → the gate; `search` → `/search` + the palette.

### 2.4 Backend contract surface

112 endpoints across 18 route modules. Largest: crypto (15), secrets (13), prompt_studio (10), model_playground (9), generators (8). **None of these is modified by Phase 09.**

### 2.5 Existing design system

There is a real, coherent **color** system and a real **radius** system. There is no type system, no spacing system, no motion system, and no status system.

- `globals.css` defines a complete shadcn semantic palette in OKLCH for `:root` and `.dark` — background, foreground, card, popover, primary, secondary, muted, accent, destructive, border, input, ring, five chart colors, and a full `--sidebar-*` set. This is good work and is the contract 40 primitives depend on.
- `--radius: 0.625rem` with sm/md/lg/xl/2xl/3xl/4xl derived as multipliers in `@theme inline`. A real system, underused — components mostly hardcode `rounded-xl`.
- **No type ramp.** Font sizes are picked per-component from Tailwind defaults, including one-off arbitrary values (`text-[11px]`, `text-[10px]`).
- **No spacing scale.** `p-4 md:p-6` is re-declared in eleven files.
- **No status roles.** Only `--destructive` exists; success/warning/info are hardcoded per component where needed.
- **No motion tokens**, and `framer-motion` — a declared dependency — has **zero import sites** anywhere in the codebase.

---

## 3. 🔴 Defects — runtime-verified

These are not stylistic observations. Both were measured in a running browser on 2026-08-06.

### 3.1 The entire application renders in Times New Roman

**Severity: 🔴 BLOCKER** (per `12_BUG_CLASSIFICATION.md` §2 — a defect that "should never have shipped this way").

`app/globals.css` lines 11–13 declare, inside `@theme inline`:

```css
--font-sans: var(--font-sans);          /* self-referential */
--font-mono: var(--font-geist-mono);
--font-heading: var(--font-sans);
```

Because the block is `inline`, Tailwind does not emit `--font-sans` as a custom property, and the declaration overrides Tailwind's own default value for it. `globals.css` line 129 then applies `html { @apply font-sans }`, which compiles to `font-family: var(--font-sans)` — an empty reference, therefore an invalid declaration, therefore the browser default.

**Correction (T0.5a, 2026-08-06): `--font-mono` was never broken.** The audit originally claimed it failed for a second, independent reason. Probing the running app disproved that: `@theme inline`'s `--font-mono: var(--font-geist-mono)` resolves correctly for any descendant of `<body>`, where `next/font` sets that variable, so every monospace surface has rendered in Geist Mono all along. What was empty is the `--font-mono` *custom property read at `:root`* — which is not what the `font-mono` utility uses. The original claim over-read a `:root` measurement. **Only `--font-sans` was broken**, and only because `html { @apply font-sans }` is applied to the one element that is not a descendant of `<body>`.

**Measured, on `/unlock`, dev server:**

```
htmlFontFamily              "Times New Roman"
bodyFontFamily              "Times New Roman"
--font-sans                 (EMPTY)
--font-mono                 (EMPTY)
--font-geist-sans (on body) "Geist", "Geist Fallback"
```

Geist and Geist Mono are downloaded on every page load and never applied. The most-seen visual property in the product is an accident. **Fixed by Phase 09 T1.**

### 3.2 `/system/status` 404s — Settings' storage readout is dead

**Severity: 🟡 MAJOR.**

`app/(app)/settings/page.tsx:23` calls `fetch("/system/status")` — a raw fetch that bypasses `lib/api-client.ts`, the only such bypass in the codebase for a JSON GET.

The backend does serve it (`backend/app/api/routes/health.py:23`, mounted at root with no `/api` prefix). But `next.config.ts` rewrites only `/api/:path*` and `/health`. `/system/status` is not proxied, so the browser request hits Next.js, which has no such route.

**Measured:** `fetch('/system/status')` → `404`, `content-type: text/html`. `.json()` then rejects, the query errors, `statusQuery.data` stays undefined, and the Storage line in the About card silently never renders.

Two viable fixes, both frontend-only: add a `/system/status` rewrite to `next.config.ts`, or repoint Settings at `/api/workbench`, which already returns the identical `storage` object. **No backend change is required.**

#### Addendum (T0.5b, 2026-08-06) — the defect is wider than first recorded

`docker/nginx.conf` was inspected while executing the fix. It proxies `/api/` and `/health` to the backend and sends everything else to the frontend. **`/system/status` is not routed there either**, so it falls through to Next.js and 404s in production for the same reason it did in development.

The `next.config.ts` rewrite shipped at T0.5b therefore fixes **development only**. Per this phase's own contract (`03_BACKEND.md` §2.2, `VERIFICATION_CONTRACT.md` §4), `docker/**` is inspect-only and a needed change there is a finding, not an autonomous edit. **Raised for owner decision** — two options, both one-line:

- **(a)** Add a `location /system/status` proxy block to `docker/nginx.conf`, mirroring `/health`. Keeps Settings reading the endpoint that semantically owns the data; requires a deploy-config change.
- **(b)** Repoint Settings at `GET /api/workbench`, which returns an identical `storage` object and is already proxied in both environments. Zero config change anywhere; couples Settings to the Workbench feature's endpoint — the reason this option was originally rejected, though that rejection was made before production was known to be broken too.

---

## 4. Information architecture problems

### 4.1 `/search` is an orphaned route

`/search` is a fully implemented, working page. It is **not** in `NAV_ITEMS` and **not** in the command palette. Its only entry point in the entire application is a Workbench pinned-tool tile (`features/workbench/tool-metadata.ts:48`).

This directly contradicts `forge-docs/04_UI_GUIDELINES.md §2`: *"Every feature page is reachable from the sidebar **and** the command palette."*

### 4.2 Three search surfaces, no stated boundary

| Surface | Backend | Scope |
|---|---|---|
| ⌘K palette | `GET /api/search` | secrets + notes + documents |
| `/search` | `GET /api/search` | secrets + notes + documents |
| `/knowledge` | `GET /api/knowledge` | **notes + documents only** |

Nothing in the UI explains which to use. **Important correction to the initial Phase 09 proposal:** it was proposed that Knowledge Hub "already supersedes" `/search` and the latter could be retired by redirect. Verification of `backend/app/services/knowledge/service.py` against `backend/app/services/search/service.py` shows this is **false** — Knowledge Hub composes the notes and documents FTS indexes only, per [ADR-0015](../../decisions/0015-knowledge-hub-reuses-fts5.md), and has no secrets path. Redirecting would have silently removed secret search. The proposal was rejected; see [ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md) for the adopted resolution.

### 4.3 The sidebar is a flat, unranked list

Twelve destinations of very different weight in one undifferentiated column. "Settings" (app configuration) sits in the same visual register as "Workbench" (the landing surface). Nothing signals that Secrets/Notes/Documents/Knowledge are persistent stores while Converter/Developer Toolkit are stateless transforms.

### 4.4 Declared keyboard shortcuts are not implemented

`NAV_ITEMS` declares `shortcut` for eight destinations (`D`, `V`, `N`, `K`, `P`, `O`, `U`, `,`). `CommandPaletteProvider` **renders** them via `<CommandShortcut>` — so the UI promises them — but no handler anywhere binds them. The only real keyboard shortcut in the app is ⌘K itself.

### 4.5 One destination, two icons

Prompt Studio renders `MessageSquareText` in the sidebar (`lib/nav-registry.ts:46`) and `Sparkles` on its Workbench tile (`features/workbench/tool-metadata.ts:52`). The divergence is commented as deliberate but reads as an inconsistency.

---

## 5. UX problems

### 5.1 Destructive actions are inconsistent — three delete silently

| Surface | Confirms? |
|---|---|
| Secrets | ✅ AlertDialog |
| Prompts (+ versions) | ✅ AlertDialog |
| Provider credentials | ✅ AlertDialog |
| Model Playground runs | ✅ AlertDialog |
| Projects | ✅ dedicated dialog |
| Workbench layout reset | ✅ AlertDialog |
| **Documents** | ❌ `handleDelete` → `remove.mutateAsync` directly (`app/(app)/documents/page.tsx:91`), from both the toolbar and every sidebar row |
| **Notes** | ❌ `remove.mutate(note.id)` directly (`features/notes/note-card.tsx:187`) |
| **Project Init generations** | ❌ `remove.mutate(id)` directly (`features/project-init/generation-history.tsx:47`) |

`04_UI_GUIDELINES.md §2` requires: *"Destructive actions… require a confirmation step — no silent deletes."* Three surfaces violate it, and — worse than any single violation — the user cannot form a reliable model of when Forge will ask.

### 5.2 Data-dense screens are unusable at mobile widths — and at tablet

| Rail | Width | Responsive handling |
|---|---|---|
| `features/secrets/secrets-filters.tsx:51` | `w-56` (224px), `shrink-0` | **None** |
| `features/documents/document-sidebar.tsx:40` | `w-72` (288px), `shrink-0` | **None** |
| `features/prompt-studio/prompt-sidebar.tsx:50` | `w-full lg:w-72` | ✅ Correct |

At a 375px viewport the Secrets list gets 151px and the Documents editor gets 87px. `04_UI_GUIDELINES.md §3` requires every feature to be usable at mobile widths and requires data-dense views to have *"an explicit mobile layout, not just a squeezed desktop table."* Prompt Studio (Phase 03) is the one surface that got this right and is the reference implementation for the rest.

**Addendum (T0.6, 2026-08-06) — a second, distinct failure at 768px.** Live inspection of populated Secrets at exactly the `md` breakpoint (768px, tablet) found a **horizontal scrollbar**: the fixed-width rail plus fixed-width row content overflow the viewport rather than reflowing. This was not visible from source inspection alone — the 375px failure mode (rail eating the content) and the 768px failure mode (rail plus content both overflowing) are different bugs with the same root cause (`w-56 shrink-0`, no responsive variant), and both are closed by the same fix (T10's `FilterRail`).

### 5.3 Wide-desktop layout is essentially undesigned

Breakpoint usage across the whole frontend: `md:` ×39, `sm:` ×32, `lg:` ×13, `xl:` ×4, `2xl:` ×1. Above 1280px, almost nothing adapts — content is left at desktop density in a much wider frame.

### 5.4 Inconsistent page framing

12 of 15 `(app)` routes use `PageHeader`. **Documents** and **Prompt Studio** bypass it entirely, opening straight into a split layout. Two of them then hardcode the topbar height to reclaim the space: `h-[calc(100dvh-3.5rem)]` in both, plus `calc(100dvh - 7.5rem)` in the Notes board. Three magic numbers encoding one shell constant.

### 5.5 Error and empty states are hand-rolled per surface

`EmptyState` exists and is used in six places. But "couldn't load X + Retry" is re-implemented inline with different markup in at least four: `app/(app)/projects/page.tsx:63`, `features/workbench/components/workbench-grid.tsx:86`, `app/(app)/project-init/page.tsx:30` (a bare `<p className="text-sm text-destructive">` with no retry at all), and `app/(app)/search/page.tsx:65` (which uses `EmptyState` for an error, semantically wrong).

---

## 6. Component architecture problems

### 6.1 Duplicated patterns

| Pattern | Copies | Where |
|---|---|---|
| Bordered list container (`rounded-xl border border-border`) | 7 | secrets, project detail, project-init, ingest job-list, search results, workbench panel card, tool-card |
| Search input with absolutely-positioned icon | 6 | secrets, notes, search, documents rail, prompt-studio rail, auth layout |
| Inline "couldn't load + retry" block | 4 | see §5.5 |
| Hardcoded shell-height calc | 3 | documents, prompt-studio, notes-board |
| Page padding `p-4 md:p-6` | 11 | most routes |

### 6.2 Installed but unused primitives

`components/ui/table.tsx`, `avatar.tsx`, `context-menu.tsx`, `alert.tsx` have **zero** import sites. `table` is the notable one: Forge has seven data-list surfaces, every one of them hand-rolled from `<div>`s and `<button>`s, while a table primitive sits unused.

### 6.3 Dead dependency

`framer-motion` (^12.42.2) is declared in `package.json` and imported nowhere.

### 6.4 The nav registry has two consumers that drift

`lib/nav-registry.ts` is the single source for sidebar and palette, which is correct. But `features/workbench/tool-metadata.ts` maintains a **manually synced** `NAV_KEY_BY_HREF` map plus an `EXTRA_TOOL_METADATA` override, and the backend keeps its own `WORKBENCH_TOOL_KEYS` list. The file's own comments acknowledge this as a "documented, tracked gap." It is the mechanism behind §4.5's two-icon divergence, and Phase 08 shipped a BLOCKER (`BUG-0001`) caused by exactly this seam.

---

## 6.5 Findings added by the screen dependency graph

Added 2026-08-06, after [`11_SCREEN_GRAPH.md`](11_SCREEN_GRAPH.md) was built at the project owner's request. Three things a flat route inventory structurally could not show:

1. **The cross-feature boundary is not clean** — ten edges against a zero-tolerance standard. Corrects §8 above; detail in `11_SCREEN_GRAPH.md` §5.1.
2. **Two module cycles** — `workbench ↔ notes` and `workbench ↔ projects`. Both are the intended ADR-0002 registry inversion, not accidental coupling, but they mean those three features cannot be migrated in isolation.
3. 🟢 **Knowledge Hub cannot deep-link to a note.** `knowledge-result-row.tsx:19` routes note results to a bare `/notes` while document results get `?open=<id>` — dropping the user on an infinite board with no indication which note they clicked. Both the command palette and `/search` deep-link notes correctly via the same working `?open=` contract. Folded into T11.

## 7. Accessibility problems

### 7.1 Note on §6.5's cross-feature finding

It is deliberately **not** in Phase 09's scope. Fixing it means either relaxing [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md)'s rule to accommodate registry patterns and public-component reuse, or introducing a shared layer for the two data-layer reach-throughs. Both are architecture decisions for the project owner, and neither is a presentation concern. Recorded so it is tracked rather than absorbed.


| Check | Finding |
|---|---|
| Accessible names on icon-only buttons | **38 icon-only buttons; 3 have `aria-label`; 11 rely on `title`.** The remainder have no accessible name. |
| `prefers-reduced-motion` | **Zero occurrences** in the entire codebase. |
| Contrast standard | Not defined. `04_UI_GUIDELINES.md §4` lists "define a minimum contrast standard" as an open TODO. No audit has ever been run — also an open TODO in the same file. |
| Semantic lists | Several data lists are `<div>` stacks of `<button>`s rather than `<ul>`/`<li>`. |
| Focus management | Good in places (Workbench customize mode does it deliberately and correctly); not systematic. |
| Keyboard drag | ✅ `@dnd-kit` `KeyboardSensor` correctly wired in both the Notes board and Workbench grid. |
| Landmarks | Partial — `<aside>`/`<nav>`/`<main>` present in the shell; not consistent inside features. |

## 8. What is already good, and must be preserved

Stated explicitly so the redesign does not "fix" things that are not broken:

- **The API boundary.** `lib/api-client.ts` as the single fetch wrapper with a typed `ApiError`; each `features/*/api.ts` owning its own endpoint shapes; no endpoint knowledge leaking into components. Only one violation exists (§3.2) and Phase 09 removes it.
- ~~**Feature isolation.** No cross-feature imports of internals.~~ — **Corrected 2026-08-06.** This claim was wrong, and the correction is left visible rather than edited away. Building the screen dependency graph ([`11_SCREEN_GRAPH.md`](11_SCREEN_GRAPH.md) §5.1) found **ten** cross-feature import edges across six features, against a coding standard that permits zero. Four are the intended Workbench registry inversion (ADR-0002); six are public-component reuse (`ProjectPicker` ×4, `KnowledgeLinkPanel`, `KnowledgeTagPicker`); and **two features reach into another feature's data layer** — `notes/note-card.tsx` imports `useKnowledgeList` from `knowledge/api`, and `projects` imports `model-playground`'s hooks *and types* across three files including `api.ts`. This is architectural debt, not presentation debt; Phase 09's obligation is to not worsen it, not to fix it. See §7.1.
- **URL as state.** Knowledge Hub's four filters, Developer Toolkit's `?tab=`, and the `?open=` selection convention are all deliberate and correct. Preserve exactly.
- **Optimistic updates.** The Workbench layout mutation does proper `onMutate`/rollback/`onSettled`, *and* correctly preserves unregistered panel types across unrelated user actions.
- **The panel registry.** `features/workbench/panel-registry.ts` + `register-all.ts` with the side-effect-import ordering comment is careful, correct work.
- **The color and radius systems.** Complete, OKLCH, both themes, derived radius scale. Extended by Phase 09, never replaced.
- **Prompt Studio's responsive master–detail.** The correct pattern, already shipped.
- **Theme persistence.** `next-themes` locally plus server-side persistence via `settingsApi.updateTheme`.

## 9. Risk register for the redesign

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | T1's global CSS change breaks all 40 primitives at once | Medium | High | Preserve every shadcn token name verbatim; T1 is its own task, verified before any screen work begins |
| R2 | Deep-link contracts (`?open=`, `?tab=`, `?q=`, `?project_id=`, `?new=`) silently break during a page rewrite | Medium | High | Enumerated in `08_ACCEPTANCE.md`; T28 re-tests every one against the pre-phase baseline |
| R3 | The five compatibility redirects break | Low | High | Untouched by design; explicitly re-verified in T28 |
| R4 | A frozen phase's behavior changes while restyling its surface | Medium | High | `IMPLEMENT.md` execution rule: presentation-only inside frozen surfaces; behavior changes require a finding, not an edit |
| R5 | Nav grouping changes `NAV_ITEMS` shape and breaks `tool-metadata.ts` or the backend tool catalog | Medium | Medium | §6.4's seam is known and caused Phase 08's BLOCKER; T3 adds group metadata **additively** and re-verifies the Workbench catalog |
| R6 | No frontend test framework exists — regressions are caught only by manual verification and typecheck | High | Medium | Pre-existing condition, out of scope to fix here; compensated by an explicit per-task preserve-contract and the T28 sweep |
| R7 | Scope creep from "while we're in here" fixes | High | Medium | Out-of-scope list in `01_SPEC.md`; anything found becomes a documented finding, not an in-flight edit |
| R8 | Phase runs long and context is lost mid-migration | High | Medium | Five milestones, `CURRENT_STATE.md` updated continuously, checkpoints per `10_CHECKPOINT_PROTOCOL.md` |

## 10. Cross-references

- [README.md](README.md) · [01_SPEC.md](01_SPEC.md) · [02_UI.md](02_UI.md) · [05_COMPONENTS.md](05_COMPONENTS.md) · [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [`.design/frontend-reimagine/DESIGN_BRIEF.md`](../../../.design/frontend-reimagine/DESIGN_BRIEF.md)
- [`.design/frontend-reimagine/INFORMATION_ARCHITECTURE.md`](../../../.design/frontend-reimagine/INFORMATION_ARCHITECTURE.md)
- [`.design/frontend-reimagine/DESIGN_TOKENS.css`](../../../.design/frontend-reimagine/DESIGN_TOKENS.css)
- [../../04_UI_GUIDELINES.md](../../04_UI_GUIDELINES.md) — the guidelines §4.1, §5.1, §5.2 are measured against
- [../../05_DESIGN_SYSTEM.md](../../05_DESIGN_SYSTEM.md) — the stub this phase fills in
- [../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md)
- [../../decisions/0017-layered-design-token-architecture.md](../../decisions/0017-layered-design-token-architecture.md)
