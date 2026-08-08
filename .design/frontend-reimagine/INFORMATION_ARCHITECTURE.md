# Information Architecture: Forge

> Produced by the `information-architecture` skill (julianoczkowski/designer-skills), Phase 09 discovery session, 2026-08-06.
> Reads from [DESIGN_BRIEF.md](DESIGN_BRIEF.md). Extends the shipped structure — it does not replace it.
> Every route below exists today. No route is created and none is deleted.

---

## 0. What changes, and what does not

| | Change |
|---|---|
| **Routes** | None added, none removed. `/search` keeps its URL and its full secrets+notes+documents scope. |
| **Route params** | Unchanged. `?open=`, `?tab=`, `?q=`, `?type=`, `?tag_id=`, `?project_id=`, `?new=` all keep their current meaning. |
| **Navigation structure** | Flat 12-item sidebar → 4 labelled groups + a pinned utility item. |
| **Search model** | Three ambiguous surfaces → one global search (palette, with `/search` as its full-results view) + one domain browser (Knowledge Hub). |
| **Entry points** | `/search` gains sidebar-adjacent and palette entry points; it is currently reachable only from a Workbench tile. |

### 0.1 Correction to the original consolidation proposal

The Phase 09 discovery question proposed *"retire the standalone `/search` page by redirecting it into Knowledge Hub, which already supersedes it."* **Verification against the backend showed that premise is false and the proposal is rejected.**

- `backend/app/services/search/service.py` queries `secrets_service.list_secrets` **+** `notes_service.search_notes` **+** `documents_service.search_documents`.
- `backend/app/services/knowledge/service.py` queries `notes_service.search_notes` **+** `documents_service.search_documents` only — per [ADR-0015](../../forge-docs/decisions/0015-knowledge-hub-reuses-fts5.md), Knowledge Hub composes the notes/documents FTS indexes and has no secrets path at all.

Knowledge Hub therefore does **not** supersede `/search`; it covers strictly less. Redirecting would silently remove the ability to search secrets — a user-visible functionality regression, which `Phase 09 §2` forbids without exception.

**Resolution adopted instead:** give each surface exactly one job, which achieves the same goal (one obvious answer to "where do I search?") without losing scope. See §2.4. Recorded as [ADR-0016](../../forge-docs/decisions/0016-grouped-navigation-and-search-surface-consolidation.md).

## 1. Site Map

```
Forge
│
├── (auth) — no shell, unauthenticated
│   ├── Setup                    /setup
│   └── Unlock                   /unlock
│
└── (app) — full shell, behind AuthGate
    │
    ├── WORKSPACE
    │   ├── Workbench            /                      ← default landing
    │   ├── Projects             /projects
    │   └── Project detail       /projects/[id]
    │
    ├── LIBRARY  (things Forge stores for you)
    │   ├── Secrets              /secrets               ?open= ?project_id= ?new=
    │   ├── Notes                /notes                 ?open= ?project_id= ?new=
    │   ├── Documents            /documents             ?open= ?project_id=
    │   └── Knowledge Hub        /knowledge             ?q= ?type= ?tag_id= ?project_id=
    │
    ├── BUILD  (things you author with)
    │   ├── Prompt Studio        /prompt-studio         ?open=
    │   ├── Model Playground     /model-playground
    │   └── Project Init         /project-init
    │
    ├── TOOLS  (things Forge does for you — stateless)
    │   ├── Converter            /converters            ← /ingest redirects here
    │   └── Developer Toolkit    /developer-toolkit     ?tab=generators|crypto|utilities
    │                                                     ← /generators, /crypto, /utilities redirect here
    │
    ├── Settings                 /settings              ← utility nav, pinned below the rule
    │
    └── Search results           /search                ?q=   ← not a sidebar item; see §2.4
```

Existing compatibility redirects (`next.config.ts`) are preserved unchanged: `/vault → /secrets`, `/ingest → /converters`, `/generators|/crypto|/utilities → /developer-toolkit?tab=…`.

## 2. Navigation Model

### 2.1 Primary navigation — grouped sidebar

Four labelled groups, eleven destinations. Groups are **static section labels, not collapsible accordions**: with twelve total destinations, hiding any of them costs more than it saves, and collapse state is one more thing to persist and get wrong.

| Group | Items | The axis it expresses |
|---|---|---|
| **Workspace** | Workbench, Projects | Where you start and how work is scoped |
| **Library** | Secrets, Notes, Documents, Knowledge | Persistent records Forge stores for you |
| **Build** | Prompt Studio, Model Playground, Project Init | Surfaces where you author artifacts |
| **Tools** | Converter, Developer Toolkit | Stateless transforms — input in, output out, nothing retained |

The grouping axis is **stored / authored / applied**, which is explainable in one sentence and holds for every current item. This is the ordering fix for the audit's finding that "Settings" and "Workbench" currently sit in the same visual register.

Group labels are Swiss-register: uppercase, letterspaced, `--font-size-2xs`, `--color-text-tertiary`. They are `<div role="presentation">` labels on `<nav>` sections with `aria-label`, not headings — they title a landmark, not document content.

### 2.2 Utility navigation

**Settings** is pinned to the bottom of the rail, below a divider, outside the four groups. It is app configuration, not a destination in the work hierarchy.

The **Lock** action stays in the topbar (a session action, not a destination) and remains mirrored in the command palette.

### 2.3 Secondary navigation — within a section

Three existing patterns, kept and made consistent rather than replaced:

- **Tabs** for peer views of one surface — Developer Toolkit's `?tab=` (URL-backed, part of the external contract) and its nested crypto tabs.
- **Filter rail** for scoping a list — Secrets (folders + tags), Documents (list + search), Prompt Studio (list + tags), Knowledge Hub (filter bar). Below `lg`, every rail becomes a drawer.
- **Master–detail** for author-and-select surfaces — Documents, Prompt Studio. Below `lg`, one pane at a time with a back affordance. Prompt Studio already implements this correctly and is the reference.

### 2.4 The search model — one job per surface

This is the audit's central IA fix. Today three surfaces overlap with no stated boundary; after Phase 09 each has exactly one job:

| Surface | Job | Scope | Entry |
|---|---|---|---|
| **⌘K command palette** | *Find or go to anything, from anywhere.* The universal entry point. | Navigate (all 12 destinations) + secrets + notes + documents + session actions | ⌘K/Ctrl-K from any route; topbar search trigger |
| **`/search?q=`** | *See the full result set for a query.* The palette's overflow view — same backend query, no truncation, room for context. | Identical to the palette: secrets + notes + documents | "View all results" from the palette; Enter on a topbar query; Workbench tile (existing); command palette entry (**new**) |
| **`/knowledge`** | *Browse, filter, tag, link, and project-scope your notes and documents.* An organizing surface, not the app's search. | Notes + documents (ADR-0015) | Sidebar → Library |

Both search surfaces call the same `GET /api/search`, so they can never disagree. Knowledge Hub's `?q=` stays what it already is — a **filter within** the Hub, not global search — and its copy is adjusted to say so.

`/search` stops being an orphan: it gains a command-palette entry and a real relationship to the palette, which is what actually made it undiscoverable. It stays out of the sidebar deliberately — a persistent nav item for a surface reachable by a global keystroke is redundant, which is what [ADR-0007](../../forge-docs/decisions/0007-search-dedicated-page.md) concluded and this phase upholds.

**Keyboard shortcuts become real.** `NAV_ITEMS[].shortcut` already declares letters (`D`, `V`, `N`, `K`, `P`, `O`, `U`, `,`) that are rendered in the palette but wired to nothing. Phase 09 implements them as palette-scoped accelerators.

### 2.5 Mobile navigation

The existing left drawer (`Sheet`) is kept — it is the right pattern for 12 destinations — and re-rendered from the *same grouped structure* as the desktop rail rather than duplicating the loop with different active-state classes, as it does today.

Topbar at mobile: menu trigger, search trigger (icon-only, opens the palette), Lock. Page-header actions collapse into an overflow menu past two.

## 3. Content Hierarchy

Priority order per surface. This is what the redesign ranks typographically and spatially.

### Workbench `/`
1. **Pinned tools** — the reason the page exists; fastest path back to work.
2. **Quick actions** — create-new for the three highest-frequency object types.
3. **Recent activity** — orientation: what happened since last session.
4. **Recent notes** — a peek at the most volatile content.
5. **System status** — reassurance, not a task. Lowest weight.
6. *Customize mode* — off the critical path entirely; entered deliberately.

### Secrets `/secrets`
1. **The list** — the whole point; every row scannable by name.
2. **Search + project scope** — the primary narrowing tools, above the list.
3. **Folder/tag rail** — secondary narrowing; a drawer below `lg`.
4. **New secret** — a page-header action, always reachable.
5. **Detail sheet** — full record on demand, over the list, never replacing it.

### Knowledge Hub `/knowledge`
1. **Results** — with type, tags, and project visible per row without hovering.
2. **Filter bar** — four URL-backed filters; current state always legible.
3. **Result count / truncation notice** — sets expectations before scrolling.
4. **Tag + link affordances** — per row, on demand.

### Documents `/documents` · Prompt Studio `/prompt-studio`
1. **The editor** — the work surface; gets the most space at every width.
2. **Document/prompt title** — identity, always visible while editing.
3. **List rail** — switching context; a drawer below `lg`.
4. **Object actions** (pin, tags, links, export, version history, delete) — a toolbar, grouped by consequence, destructive last and visually separated.

### Projects `/projects` · `/projects/[id]`
1. **Project identity** — name, description, archived state.
2. **Scoped content** — the secrets/notes/documents this project holds.
3. **AI config + quick run** — a sidebar concern, not the headline.
4. **Lifecycle actions** — edit, archive, delete; delete visually separated.

### Converter · Developer Toolkit
1. **Section structure** — which family of tools you're in.
2. **The tool cards** — each self-contained, input-above-output.
3. **Persistent output** — results stay put; nothing scrolls away on re-run.

### Settings
1. **Appearance** — the most-changed setting.
2. **Master password** — highest-consequence; visually separated.
3. **Backup** — import/export, with the destructive-import warning adjacent to the control, not below the card.
4. **About** — reference only, lowest weight. *(Its Storage line is currently dead — `/system/status` 404s. Fixed in Phase 09 via a `next.config.ts` rewrite.)*

## 4. User Flows

### 4.1 Enter Forge
1. Any URL → `AuthGate` checks setup status, then session.
2. Not set up → `/setup`. Set up but locked → `/unlock`. Authenticated → the requested route renders.
3. Unlock success → `/`.
4. **Preserved exactly.** Restyled only; the redirect logic is untouched.

### 4.2 Find something (the reworked flow)
1. User presses ⌘K from anywhere.
2. Palette opens, focus in the input, nav destinations listed by default.
3. User types.
   - <2 characters → destinations only, filtered.
   - ≥2 characters → `GET /api/search` fires; Secrets / Notes / Documents groups render inline.
4. User chooses:
   - A destination → route push.
   - A result → deep link (`/secrets?open=<id>`, `/notes?open=<id>`, `/documents?open=<id>`) — **the existing contract, unchanged.**
   - **"View all results"** → `/search?q=<query>` with the full, untruncated set. *(New affordance.)*

### 4.3 Delete anything (the unified flow)
1. User triggers a destructive action.
2. `ConfirmDialog` names the specific object and states what is lost.
3. Confirm → mutation → optimistic removal → toast reporting the outcome.
4. **Applies uniformly**, closing the audit's finding that Documents, Notes, and Project-Init generations currently delete with no confirmation while Secrets, Prompts, Providers, and Runs ask.

### 4.4 Scope work to a project
1. `/projects` → create or open a project.
2. `/projects/[id]` shows scoped secrets, notes, documents.
3. "View all" → `/secrets?project_id=<id>` etc.
4. `ProjectPicker` on Secrets/Notes/Documents sets the same scope inline.
5. **Preserved exactly.** Consistency of the picker's placement and label is the only change.

### 4.5 Convert / generate (stateless tools)
1. Sidebar → Tools → Converter or Developer Toolkit.
2. Deep link honored: `?tab=` lands on the named section.
3. Input → transform → output, with copy affordance.
4. **Preserved exactly**, including the `?tab=` contract the retired routes redirect into.

## 5. Naming Conventions

One word per concept, used everywhere. The audit found several of these used inconsistently between sidebar, page header, palette, and Workbench tile.

| Concept | Label in UI | Notes |
|---|---|---|
| Encrypted credential store | **Secrets** | Never "Vault" — [ADR-0006](../../forge-docs/decisions/0006-vault-renamed-to-secrets.md). `/vault` redirect stays. |
| Home / landing surface | **Workbench** | Never "Dashboard" — [ADR-0001](../../forge-docs/decisions/0001-workbench-replaces-dashboard.md). |
| Notes + documents browser | **Knowledge Hub** in the page header; **Knowledge** in the sidebar | Sidebar uses the short form for rail width; both refer to `/knowledge`. |
| Format conversion surface | **Converter** | Singular. The route is `/converters` (plural, unchanged); the *label* is singular everywhere. |
| Generators + crypto + utilities | **Developer Toolkit** | Never the three old names as top-level labels. |
| Global find | **Search** | The palette is "Search Forge…"; the page is "Search results". |
| Stored LLM prompt | **Prompt** | Not "template" — templates are a Project Init concept. |
| Project Init output | **Generation** | Not "scaffold" or "download". |
| Model Playground execution | **Run** | Consistent with `run-history-list`. |
| Grouping unit | **Project** | Never "workspace" in UI copy — [ADR-0005](../../forge-docs/decisions/0005-projects-primary-organizational-unit.md). "Workspace" appears only in this document as an IA group label. |

**Fix required:** Prompt Studio currently renders a `Sparkles` icon on its Workbench tile and `MessageSquareText` in the sidebar for the same destination (`features/workbench/tool-metadata.ts`). One destination, one icon.

## 6. Component Reuse Map

| Component | Used on | Behavior differences |
|---|---|---|
| `AppShell` | Every `(app)` route | None. Owns the topbar height token so no page recomputes it. |
| `Sidebar` / `MobileNav` | Every `(app)` route | Same grouped source; rail at `md+`, drawer below. |
| `Topbar` | Every `(app)` route | Breadcrumb slot populated on `/projects/[id]` only. |
| `CommandPalette` | Every `(app)` route | None. |
| `PageHeader` | 14 of 15 `(app)` routes | Documents and Prompt Studio adopt it (they bypass it today). Notes/Secrets/Projects carry action clusters; Converter/Dev Toolkit carry none. |
| `DataList` / `DataListRow` | Secrets, Search, Knowledge, Ingest jobs, Project scoped lists, Generation history, Run history | Column composition differs per surface; row rhythm, rule weight, and hover/focus treatment do not. |
| `FilterRail` | Secrets, Documents, Prompt Studio | Content differs; the rail-vs-drawer responsive contract does not. |
| `SearchField` | Secrets, Notes, Search, Documents rail, Prompt Studio rail, Knowledge filter bar | Placeholder and debounce differ; markup and focus treatment do not. |
| `ToolCard` | Converter (9 tools), Developer Toolkit (16 tools), Settings (4 cards) | None. |
| `EmptyState` / `ErrorState` | Every list-bearing surface | Copy differs; structure does not. |
| `ConfirmDialog` | Every destructive action | Copy differs; structure and button order do not. |
| `panel-error-boundary` | Workbench panels today | Generalized so a failed region never blanks the page. |

## 7. Content Growth Plan

| Surface | Grows | Current handling | Phase 09 posture |
|---|---|---|---|
| Secrets | Unbounded | Server-side `q`/folder/tag/project filtering; no pagination | Design rows for long lists (sticky column labels, stable row height). Pagination stays a backend gap. |
| Knowledge Hub | Unbounded | Server caps and reports `truncated` + `total` | Make the truncation notice a first-class, legible element rather than header microcopy. |
| Notes | Unbounded | Infinite board, no pagination | Board keeps horizontal pan at mobile rather than reflowing. |
| Documents / Prompts | Unbounded | Rail lists, search-filtered | Rail is virtual-scroll-ready in structure; virtualization itself is out of scope. |
| Run history / Generation history | Unbounded | Capped lists with delete | Ruled `DataList` treatment; explicit "showing N" where the server caps. |
| Activity feed | Unbounded | Server-capped | Unchanged. |

**No pagination UI is introduced in Phase 09** — the endpoints don't support it (a tracked gap in `docs/Roadmap.md`), and inventing client-side pagination over an uncapped fetch would be worse than the current honest truncation notice.

## 8. URL Strategy

Documenting the existing conventions so the redesign preserves them exactly.

- **Pattern**: `/<feature>` for a surface, `/<feature>/[id]` for a detail page. Only Projects uses a path segment for identity.
- **Dynamic segments**: `/projects/[id]` only.
- **Selection via query, not path**: `?open=<id>` opens a sheet/editor over a list without leaving the list route — used by Secrets, Notes, Documents, Prompt Studio. This is a deliberate existing convention (it keeps list state and scroll position) and is **preserved**.
- **Filter/scope params**: `?q=`, `?type=`, `?tag_id=` (repeatable), `?project_id=`.
- **View params**: `?tab=` (Developer Toolkit) — part of the external redirect contract.
- **Intent params**: `?new=1` — consumed once on mount and stripped via `router.replace`. Used by Workbench Quick Actions into Secrets, Notes, Projects.
- **History discipline**: `push` for navigation the user should be able to back out of; `replace` for filter and tab changes. Existing behavior, kept.
- **Compatibility redirects**: five in `next.config.ts`, all `permanent: false`. Preserved; none added, none removed by this phase.
