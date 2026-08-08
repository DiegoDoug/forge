# Design Brief: Forge Frontend Reimagine (Phase 09)

> Produced by the `design-brief` skill (julianoczkowski/designer-skills) during the Phase 09 discovery session, 2026-08-06.
> Codebase-derived. No product capability in this brief is invented — every flow named here exists in `frontend/` today.
> Companion documents: [INFORMATION_ARCHITECTURE.md](INFORMATION_ARCHITECTURE.md), [DESIGN_TOKENS.css](DESIGN_TOKENS.css), [TASKS.md](TASKS.md).

---

## Problem

Forge is a genuinely capable self-hosted developer toolbox — 15 routes, 112 backend endpoints, eight shipped phases of real functionality. But it does not *look* or *feel* like one product. It feels like eight products that happen to share a sidebar.

Described from the user's side:

- **"Why does this look broken?"** Every screen in Forge renders in **Times New Roman**. The Geist typeface is downloaded on every page load and then never applied, because `--font-sans` is defined as a self-reference and resolves empty. The single most-seen visual property in the entire application is an accident. (Verified at runtime, not inferred — see [00_AUDIT.md §3.1](../../forge-docs/implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md).)
- **"Where do I search?"** There are three search surfaces — the ⌘K palette, a `/search` page, and Knowledge Hub — with overlapping scopes and no explanation of which one to use. `/search` isn't in the sidebar or the palette at all; its only entry point is a Workbench tile.
- **"Which of these twelve things do I want?"** The sidebar is a flat, unlabelled list of twelve destinations of wildly different weight. "Settings" sits in the same visual register as "Workbench". Nothing signals that Secrets/Notes/Documents are *content* while Converter/Developer Toolkit are *stateless tools*.
- **"I can't use this on my phone."** Secrets pins a 224px filter rail and Documents a 288px list rail, neither with any responsive treatment. At 375px that leaves 151px and 87px of usable content respectively. The app has a mobile nav drawer, which implies a promise it does not keep.
- **"Did I just delete that?"** Deleting a document, a note, or a generated scaffold happens instantly with no confirmation, while deleting a secret, a prompt, or a provider credential asks first. The user cannot form a reliable model of when Forge will ask.

None of this is a capability problem. Forge does what it claims. It just doesn't yet *read* as one deliberate thing.

## Solution

Rebuild the presentation layer of Forge in place — same routes, same API contracts, same capabilities — around a single coherent visual and structural system, so that the product's actual quality becomes legible.

The experience we're aiming for: a developer opens Forge, and within two seconds understands what kind of tool it is (technical, precise, self-hosted, not a SaaS dashboard), where their content lives versus where their tools live, and how to get to any of it. Density is high because the work is dense. Nothing is decorated. Every line, every border, every color carries information.

## Experience Principles

Three principles, each resolving a real tension found in the audit.

1. **System over screen** — *No page gets a value the system doesn't define.* The audit found seven independent re-implementations of the same bordered-container pattern, six hand-rolled search inputs, and two hardcoded `calc(100dvh-3.5rem)` layout hacks. Every one of those is a place where a future change has to be made seven times. Resolves: *local convenience vs. global coherence* — global wins, always.

2. **Density with hierarchy, not density instead of it** — *Show more, but rank it.* Forge's users are managing dozens of secrets and hundreds of knowledge items; airy card grids waste their screen. But the current lists are flat — every row is the same weight, so scanning is linear. The answer is tighter rows *plus* a real typographic hierarchy, not more whitespace. Resolves: *information density vs. scannability* — get both, via type and rule weight rather than padding.

3. **Reversibility is visible** — *The user always knows whether an action can be undone before they take it.* Destructive actions get one consistent treatment across all 15 routes. Non-destructive ones never borrow that treatment and never ask for confirmation they don't need. Resolves: *friction vs. safety* — spend the friction only where loss is real, and spend it uniformly.

## Aesthetic Direction

- **Philosophy**: **Dieter Rams (functionalist) as the base system, with Swiss / International Typographic discipline applied to data-dense surfaces.** Chosen and confirmed by the project owner, 2026-08-06.

  Rams governs the shell, forms, dialogs, and tool cards: restrained monochrome, one functional accent, strict spatial system, borders and dividers instead of shadows, motion only on state change. This is the right base because Forge is *literally* a rack of tools — "less but better" is not an aesthetic pose here, it's a description of the product.

  Swiss governs Secrets, Knowledge results, run history, generation history, and version history: rules as structural elements, dramatic scale contrast between row title and metadata, all-caps letterspaced column labels, zero shadows, alignment as a hard constraint. These surfaces are tables of record, and Swiss typography is what tables of record have always looked like.

  The two are compatible because they share a substrate — flat, gridded, monochrome-plus-one-accent, no ornament. Swiss is applied here as *typographic treatment within Rams containers*, not as a second design system. The seam is explicitly bounded in [05_COMPONENTS.md](../../forge-docs/implementation/Phase-09-Frontend-Reimagine/05_COMPONENTS.md) so it cannot drift.

- **Tone**: Precise, quiet, unhurried, confident. Reads as instrumentation rather than persuasion. Forge never tries to delight; it tries to be exactly right.

- **Reference points**: Linear's information density and keyboard-first posture; Stripe Dashboard's typographic hierarchy in data tables; Vercel's restraint in dark mode; the Braun ET66 calculator as the literal Rams touchstone for "one accent on a monochrome field."

- **Anti-references**: Generic AI-SaaS dashboards. Specifically forbidden: purple-to-blue hero gradients, glassmorphism, floating cards on gradient meshes, decorative blurred orbs, oversized rounded corners, emoji as UI iconography, "✨"-prefixed section headings, illustration-driven empty states, and shadow-based depth used where a 1px border would do. If a visual element cannot be justified by hierarchy, comprehension, navigation, feedback, or task completion, it does not ship.

### Deviation from the `frontend-design` skill, recorded deliberately

The skill instructs: *"Choose distinctive fonts loaded via Google Fonts or CDN. Avoid generic defaults... Pair a display font with a body font."*

Forge deviates. **We wire up the already-bundled Geist / Geist Mono pairing instead of adding a display face.** Rationale:

- Forge is a **self-hosted, LAN-first, frequently-offline** product. A CDN font dependency is a runtime failure mode, not a design choice.
- Geist and Geist Mono are already installed, already downloaded on every page load via `next/font`, and already self-hosted by Next.js. The bug is that they were never *connected* — fixing the connection is a strictly smaller and safer change than introducing a new face.
- Geist is not a generic default. It's a technical grotesque designed for developer tooling, and the Sans/Mono pairing *is* the display/body pairing the skill asks for — on these screens, mono is a semantic register (keys, hashes, IDs, code), not a decorative one.

This deviation was presented to and confirmed by the project owner on 2026-08-06.

## Existing Patterns

What the codebase already establishes, which this redesign must respect or extend rather than discard.

- **Typography**: Geist Sans + Geist Mono, loaded via `next/font/google` in `app/layout.tsx` as `--font-geist-sans` / `--font-geist-mono`. **Currently unreachable** — `app/globals.css` declares `--font-sans: var(--font-sans)` (self-referential) and `--font-mono: var(--font-geist-mono)` inside `@theme inline`, so `--font-sans` resolves empty and `--font-mono` never receives the class-scoped value. Both computed to empty at runtime; the document renders in Times New Roman. There is no type ramp of any kind — sizes are chosen per-component from Tailwind defaults.
- **Colors**: A complete shadcn/ui semantic palette in `app/globals.css` (`--background`, `--foreground`, `--card`, `--primary`, `--muted`, `--accent`, `--destructive`, `--border`, `--input`, `--ring`, `--chart-1..5`, plus a full `--sidebar-*` set), defined in OKLCH for both `:root` and `.dark`. This layer is **good** and is the contract 40 `components/ui/*` primitives depend on — it must be preserved by name. What's missing: success/warning/info status roles (only `--destructive` exists), so status is currently expressed with per-component hardcoded colors.
- **Spacing**: Tailwind v4 defaults, unconfigured. No project scale. Page padding is re-declared as `p-4 md:p-6` in eleven separate files.
- **Radius**: A real system — `--radius: 0.625rem` with `--radius-sm/md/lg/xl/2xl/3xl/4xl` computed as multipliers in `@theme inline`. Underused in practice; components mostly hardcode `rounded-xl` / `rounded-lg`.
- **Components**: 40 shadcn/ui primitives on Base UI in `components/ui/`, style `base-nova`, base color `neutral`, icons `lucide-react`. Eight shared app components (`page-header`, `empty-state`, `tool-card`, `copy-button`, `output-field`, `theme-provider`, plus `app-shell/` and `command-palette/`). Four primitives are installed but entirely unused: `table`, `avatar`, `context-menu`, `alert`.
- **Motion**: `framer-motion` is a declared dependency with **zero import sites**. `tw-animate-css` is imported. No motion tokens, no `prefers-reduced-motion` handling anywhere in the codebase.
- **Theming**: `next-themes` with `attribute="class"`, `defaultTheme="dark"`, `enableSystem`. Theme choice is also persisted server-side via `settingsApi.updateTheme`. Works correctly — preserve as-is.
- **Data layer**: TanStack Query throughout; one typed `lib/api-client.ts`; per-feature `features/*/api.ts` owning endpoint shapes. This boundary is sound and is **not** in scope to change.

## Component Inventory

| Component | Status | Notes |
|---|---|---|
| `components/ui/*` (40 shadcn primitives) | **Exists** — retune only | Keep every export name and prop signature. Retune internal spacing/type to the new ramp. `table`, `avatar`, `context-menu`, `alert` currently unused — decide per [05_COMPONENTS.md](../../forge-docs/implementation/Phase-09-Frontend-Reimagine/05_COMPONENTS.md) whether `table` gets adopted for data surfaces or removed. |
| `AppShell` (sidebar + topbar + main) | **Modify** | Currently three loose components composed inline in `app/(app)/layout.tsx`. Becomes a real shell owning the grid, the `--shell-topbar-h` token, and scroll containment — killing both `calc(100dvh-3.5rem)` hacks. |
| `Sidebar` | **Modify** | Flat 12-item list → grouped sections with labels. Must keep `NAV_ITEMS` as the single registry. |
| `MobileNav` | **Modify** | Currently duplicates Sidebar's render loop with different active-state classes. Becomes a presentation of the same grouped nav. |
| `Topbar` | **Modify** | Gains breadcrumb/context slot; search trigger and Lock action retuned. |
| `CommandPalette` | **Modify** | Absorbs `/search`'s full-result behavior; gains the per-item keyboard shortcuts that `NAV_ITEMS.shortcut` already declares but nothing implements. |
| `PageHeader` | **Modify** | Add breadcrumb slot, size variants, and sticky behavior. Used by 12 of 15 routes; Documents and Prompt Studio bypass it — bring them in. |
| `EmptyState` | **Modify** | Keep API. Retune to Rams (drop the dashed border and the tinted icon chip). |
| `ErrorState` | **New** | Four routes hand-roll a "Couldn't load X + Retry" block inline with different markup. One component, one treatment. |
| `DataList` / `DataListRow` | **New** | The Swiss-typographic surface. Replaces the seven independent `rounded-xl border border-border` + hand-rolled-row implementations (Secrets, Search, Knowledge, Ingest jobs, Project scoped lists, generation history, run history). |
| `SearchField` | **New** | Six hand-rolled copies of the same absolutely-positioned-icon input exist today. |
| `FilterRail` | **New** | Owns the responsive contract that Secrets' `w-56` and Documents' `w-72` rails currently lack: rail at `lg+`, drawer below. |
| `ConfirmDialog` | **New** | Wraps `alert-dialog` into one destructive-action treatment, so Documents/Notes/Project-Init stop deleting silently. |
| `Toolbar`, `Field`, `SectionHeading`, `StatusBadge`, `KeyValueRow` | **New** | Extracted from repeated inline patterns found across features. |
| `ToolCard` | **Modify** | Currently a bare bordered div. Becomes the Rams tool container used consistently across Converter + Developer Toolkit. |
| `CopyButton`, `OutputField` | **Exists** — retune only | Sound API; restyle to tokens. |
| `features/*/` components | **Modify in place** | Each feature keeps ownership of its own UI. No feature-specific component moves into the global layer. |

## Key Interactions

- **Navigation.** Sidebar sections are static labels, not collapsible accordions — Forge has 12 destinations, which is small enough that hiding any of them costs more than it saves. Active state is a left rule plus weight change, not a filled pill.
- **Command palette (⌘K).** Opens over any route. Typing ≥2 characters queries `/api/search` and renders Secrets/Notes/Documents results inline, selecting a result deep-links to it (`?open=<id>` — the existing contract). The twelve `NAV_ITEMS.shortcut` letters become real: with the palette open, the shortcut letter jumps to that destination.
- **Destructive actions.** One path: trigger → `ConfirmDialog` naming the specific object and stating what is lost → confirm → optimistic removal → toast with the outcome. Applied uniformly to every delete in the app.
- **Loading.** Skeletons that match the shape of the content they replace (row-height skeletons for lists, not generic blocks). Never a layout shift between skeleton and content.
- **Errors.** Inline and retryable at the component that failed. A failed panel never blanks the page around it — `panel-error-boundary` already establishes this for Workbench; generalize it.
- **Copy-to-clipboard.** Already correct (`CopyButton` gives explicit confirmation). Preserve behavior exactly; restyle only.
- **Filter/search state.** Continues to live in the URL where it already does (Knowledge Hub's four params, Developer Toolkit's `?tab=`, Secrets' `?project_id=`). No filter state moves out of the URL.

## Responsive Behavior

Mobile-first, four validated widths: **375 / 768 / 1024 / 1440+**.

| Element | 375 | 768 | 1024 | 1440+ |
|---|---|---|---|---|
| Primary nav | Drawer (existing `MobileNav`) | Drawer | Persistent rail | Persistent rail |
| Filter rails (Secrets, Documents, Prompt Studio) | Drawer, triggered from a toolbar button | Drawer | Inline rail | Inline rail |
| Master–detail (Documents, Prompt Studio) | One pane at a time + back affordance | One pane | Split | Split |
| Data lists | Stacked rows; metadata wraps under title | Stacked rows | Ruled rows, aligned columns | Ruled rows |
| Tool grids (Converter, Dev Toolkit) | 1 col | 2 col | 2 col | 3 col |
| Workbench panels | 1 col | 2 col | 2 col | 3 col |
| Page header actions | Overflow menu past 2 actions | Inline | Inline | Inline |

Prompt Studio (Phase 03) already implements the master–detail pattern correctly and is the reference implementation the older surfaces get brought up to.

Behavior changes, not just size changes: filter rails *become* drawers; page-header action rows *become* overflow menus; the Secrets row's tag cluster and timestamp *drop out* below `sm` rather than truncating; the Notes board keeps horizontal pan rather than reflowing.

## Accessibility Requirements

Treated as implementation, not polish. Baseline for every migrated surface:

- **Contrast**: WCAG 2.1 **AA** minimum — 4.5:1 body text, 3:1 large text and UI boundaries — in *both* themes. This is a new explicit standard; `forge-docs/04_UI_GUIDELINES.md §4` currently has it as an open TODO. Token pairs are validated at definition time, not per component.
- **Focus**: Visible focus on every interactive element in both themes, via one `--ring` treatment. Focus is trapped in dialogs/drawers and restored to the trigger on close. The Workbench customize-mode focus handling is the existing good precedent.
- **Keyboard**: Every action reachable without a pointer, including the Notes drag board (`@dnd-kit` keyboard sensor is already wired) and the Workbench panel reorder.
- **Accessible names**: The audit found 38 icon-only buttons, of which only 3 carry `aria-label` and 11 rely on `title`. Every icon-only control gets an explicit accessible name.
- **Semantics**: Real landmarks (`nav`/`main`/`aside`), headings in order, lists as lists. Several data "lists" are currently `<div>` stacks of `<button>`s.
- **Forms**: `react-hook-form` + `zod` with inline, programmatically-associated errors (`aria-describedby`), never alert dialogs. Already the convention — enforce it uniformly.
- **Motion**: A `prefers-reduced-motion` block that disables transitions. Currently absent entirely.
- **Touch targets**: ≥44×44px at mobile widths.
- **Color is never the only signal**: status always pairs color with text or icon.

## Out of Scope

Explicitly not covered by this brief, to prevent scope creep:

- **Any backend change.** No endpoint, request shape, response shape, status code, or database schema is modified. The one server-adjacent fix in scope is a `next.config.ts` **rewrite** so the existing `/system/status` endpoint is reachable from the browser — a frontend config change, not a backend change.
- **Any new product capability.** No new screens, no new features, no new panels, no new tools. If it isn't in the codebase today, it isn't in this phase.
- **Auth/session model.** `AuthGate`, the unlock/setup flow, and cookie behavior are restyled but functionally untouched.
- **The data layer.** TanStack Query usage, the `lib/api-client.ts` boundary, and per-feature `api.ts` ownership are preserved as-is. Query keys are not renamed.
- **Route removal.** No route is deleted. `/search` is *redirected*, exactly as `/vault`, `/ingest`, `/generators`, `/crypto`, and `/utilities` already are — the URL keeps working.
- **Pagination.** The known list-endpoint pagination gap (`docs/Roadmap.md`) stays a backend concern and is not solved here.
- **Frozen phase specifications.** Phases 01–08 specs are locked. Where this phase changes a surface a frozen phase owns, it changes *presentation only*, and the change is recorded in this phase's docs — not by reopening theirs.
- **New runtime dependencies.** None. `framer-motion` is either adopted for the (minimal) motion this philosophy permits or removed as dead weight — that decision belongs to the token/motion task, and either way nothing new is installed.
