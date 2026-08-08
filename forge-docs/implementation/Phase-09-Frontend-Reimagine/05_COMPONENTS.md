# Frontend Reimagine — Components

> **Purpose:** The component architecture Phase 09 delivers — what is primitive, what is shared, what stays feature-owned, and the boundaries between them.
> **Scope:** This phase only.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved 2026-08-06; fully implemented and RC-verified 2026-08-07 — every component in this inventory built and adopted per `09_IMPLEMENTATION_TASKS.md`'s as-built notes.
> **Version:** 0.1.0
> **Last Updated:** 2026-08-06
> **Depends On:** [02_UI.md](02_UI.md), [00_AUDIT.md](00_AUDIT.md)

---

## 1. Layering rule

```
components/ui/          Primitives. Own no product knowledge. shadcn/Base UI.
components/             Shared app components. Own layout and state vocabulary,
                        never feature data shapes.
components/app-shell/   The shell. Owns navigation and page framing.
features/<f>/           Feature components. Own their own data and semantics.
```

Two hard rules, both inherited from [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) and re-stated because this phase moves a lot of code:

1. **Nothing feature-specific moves into `components/`.** A component earns promotion only when at least three features need it *and* it carries no feature semantics. `ProjectPicker` is the deliberate counter-example: it is used by Secrets, Notes, and Documents but stays in `features/projects/` because it knows what a project is. That is the correct seam and it does not change.
2. **No cross-feature imports of internals.** Features compose each other only through a feature's public components — as Documents already does with `KnowledgeTagPicker`.

## 2. Primitives — `components/ui/` (40 files)

**Retuned, never re-API'd.** Every export name and prop signature is preserved. A retune that forces a consumer edit is out of contract.

Retuning means: consume the type ramp instead of ad-hoc sizes; consume `--space-*` instead of arbitrary padding; consume `--radius` instead of hardcoded `rounded-*`; use `--elevation-*` only for true overlays; use the single `:focus-visible` treatment; use `--duration-fast`/`--easing-default` for state transitions.

**In active use (36):** accordion, alert-dialog, badge, button, card, checkbox, command, dialog, dropdown-menu, input, input-group, label, popover, progress, scroll-area, select, separator, sheet, skeleton, slider, sonner, switch, tabs, textarea, tooltip, and the rest.

**Installed with zero import sites (4):** `table`, `avatar`, `context-menu`, `alert`.

> **Open decision (OQ2, `01_SPEC.md` §7).** `table` is the interesting one — Forge has seven data-list surfaces, all hand-rolled from `<div>`s and `<button>`s, while a table primitive sits unused. **Recommendation:** adopt `table` as the markup basis for the genuinely tabular surfaces (Secrets, run history, generation history) and remove the other three. Decided in T5; whichever way it goes, nothing is left installed-and-unused at phase end (FR15).

## 3. Shared app components — `components/`

### 3.1 Existing, retuned

| Component | Change |
|---|---|
| `PageHeader` | **v2.** Adds `breadcrumb` slot, `size` variant, sticky behavior, and overflow-menu collapse for action clusters past two. Adopted by Documents and Prompt Studio, which bypass it today. Existing `title`/`description`/`actions` props unchanged. |
| `EmptyState` | Retuned to Rams — drops the dashed border and the tinted icon chip. API unchanged (`icon`, `title`, `description`, `action`). |
| `ToolCard` | Becomes the canonical Rams tool container for Converter (9), Developer Toolkit (16), and Settings (4). API unchanged. |
| `CopyButton`, `OutputField` | Restyle only. Behavior is already correct — `CopyButton`'s explicit confirmation satisfies `04_UI_GUIDELINES.md` §2 and must not regress. |
| `ThemeProvider` | Unchanged. |

### 3.2 New

Each exists because the audit found the pattern re-implemented. The "replaces" column is the justification — no component is added speculatively.

| Component | Replaces | Notes |
|---|---|---|
| `DataList` / `DataListRow` | **7** hand-rolled `rounded-xl border border-border` list containers | The Swiss surface. Owns row rhythm, rule weight, hover/focus/selected, and the loading/empty/error row variants. Column composition is passed in; rhythm is not negotiable. |
| `FilterRail` | Secrets' unresponsive `w-56`, Documents' unresponsive `w-72` | Owns the rail-at-`lg` / drawer-below contract, the trigger, and focus restoration. Prompt Studio's existing correct behavior is the reference. |
| `SearchField` | **6** copies of the absolutely-positioned-icon input | Owns icon placement, clear affordance, debounce, and `role="searchbox"` labelling. |
| `ErrorState` | **4** inline "couldn't load + retry" blocks with divergent markup | One retryable failure treatment. Corrects Search's semantically wrong use of `EmptyState` for errors, and Project Init's bare red paragraph with no retry at all. |
| `ConfirmDialog` | **6** ad-hoc `AlertDialog` compositions — and the **3** deletes that ask nothing | Wraps `alert-dialog`. Names the object, states what is lost, fixes button order and destructive styling. The mechanism behind FR12. |
| `Toolbar` | The above-list control rows in Secrets, Notes, Knowledge, Documents | Owns spacing, wrap behavior, and mobile collapse. |
| `SectionHeading` | Inline `<h2 className="text-sm font-semibold tracking-wide uppercase">` in Converter and Project Init | Applies `.label-structural`. |
| `StatusBadge` | Per-component hardcoded status colours | Consumes the new `--success`/`--warning`/`--info`/`--destructive` roles. Always pairs colour with text or icon. |
| `Field` | Repeated `Label` + control + error markup | Wires `aria-describedby`/`aria-invalid` correctly so form a11y stops being per-form. |
| `KeyValueRow` | Metadata rows in secret detail, project detail, settings About | Tabular numerals, consistent label/value ratio. |
| `AppShell` | The three components composed inline in `app/(app)/layout.tsx` | Owns the grid, `--shell-topbar-h`, and scroll containment. Retires all three viewport-calc hacks. |

### 3.3 Shell components — `components/app-shell/`

| Component | Change |
|---|---|
| `AppShell` | **New.** See above. |
| `Sidebar` | Grouped rendering from `NAV_ITEMS` group metadata. Active state becomes a left rule + weight change. **Active-route matching logic is preserved verbatim.** |
| `MobileNav` | Renders the *same* grouped structure as `Sidebar` instead of duplicating the loop with divergent active-state classes. |
| `Topbar` | Gains a breadcrumb slot. Search trigger collapses to an icon below `md`. Lock mutation unchanged. |
| `CommandPaletteProvider` | Binds the eight advertised shortcuts; adds "View all results". **Deep-link targets and the `enabled: open && query.trim().length > 1` query gate are preserved.** |

## 4. Feature components — `features/*/`

All 60+ feature components stay where they are and keep their data ownership. They are restyled and recomposed onto the shared components above; none is promoted to `components/`.

Notable per-feature changes:

| Feature | Change |
|---|---|
| `secrets/` | `SecretsFilters` → `FilterRail`; list → `DataList`; detail sheet and form dialog retuned. |
| `documents/` | `DocumentSidebar` → `FilterRail`; toolbar → `Toolbar` grouped by consequence; delete → `ConfirmDialog`; new save-state indicator. |
| `notes/` | `NoteCard` delete → `ConfirmDialog`; board height from `--shell-*` tokens, not a magic calc. |
| `knowledge/` | Result list → `DataList`; truncation notice becomes a first-class element. |
| `projects/` | Scoped lists → `DataList`; `ProjectPicker` restyled but stays feature-owned. |
| `prompt-studio/` | Sidebar → `FilterRail`. **Its responsive behavior is the reference and must not regress.** |
| `model-playground/` | Run history → `DataList`. **Credential flows preserved exactly** (ADR-0011). |
| `converters/`, `crypto/`, `generators/`, `utilities/` | Consistent `ToolCard` composition. Tool *logic* untouched. |
| `ingest/` | Job list → `DataList`; explicit polling states. |
| `project-init/` | Generation history → `DataList` + `ConfirmDialog`; catalog error → retryable `ErrorState`. |
| `workbench/` | Panel cards retuned; `panel-error-boundary` generalized for reuse; **panel registry untouched**. |
| `auth/` | `AuthGate` restyled; **redirect logic untouched**. |
| `search/`, `settings/` | Restyled onto shared components. |

## 5. Registries

Three registries exist and stay separate. This phase does **not** attempt to unify them — [ADR-0008](../../decisions/0008-capability-registry-direction.md) (Capability Registry) is Proposed, not Accepted, and `03_ARCHITECTURE.md` §4 says explicitly: do not build against it yet.

| Registry | Owner | Phase 09 change |
|---|---|---|
| `lib/nav-registry.ts` | Sidebar, mobile nav, command palette | **Additive only** — gains a `group` field. No `href`, `title`, `icon`, or `shortcut` is changed. |
| `features/workbench/tool-metadata.ts` | Workbench pinned tiles | Resolve the Prompt Studio two-icon divergence (`00_AUDIT.md` §4.5). Otherwise untouched. |
| `backend/.../workbench.py` `WORKBENCH_TOOL_KEYS` | Backend tool catalog | **Untouched** — no backend change. |

> **⚠️ Known seam.** These three are manually synced, as `tool-metadata.ts`'s own comments acknowledge, and this seam produced Phase 08's BLOCKER (`BUG-0001`). T3's acceptance criterion re-verifies the Workbench tool catalog after the nav change, specifically because grouping touches `NAV_ITEMS`.

## 6. What must not happen

Restating [`01_SPEC.md`](01_SPEC.md) NFR3 at component granularity, because this is where a large redesign typically goes wrong:

- **No parallel component tree.** No `components/v2/`, no `components-new/`, no `*-redesigned.tsx`.
- **No parallel shell.** One `AppShell`.
- **No duplicate API client.** `lib/api-client.ts` stays the only fetch boundary — and the one existing bypass (`fetch("/system/status")` in Settings) is removed by FR14, reducing the count from one to zero.
- **No feature logic moved into shared components** to make a layout easier.
- **No component created without a named duplicate it replaces.** Every entry in §3.2 cites its count.
- **No primitive API change.** If a retune seems to need one, it is a finding for `CURRENT_STATE.md`, not an edit.

If a migration genuinely requires a temporary parallel implementation, `IMPLEMENT.md` requires the removal boundary to be documented **at the moment it is created**, not afterwards.

## 7. Cross-references

- [02_UI.md](02_UI.md) · [00_AUDIT.md](00_AUDIT.md) §6 · [01_SPEC.md](01_SPEC.md) · [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md) · [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md)
- [../../decisions/0008-capability-registry-direction.md](../../decisions/0008-capability-registry-direction.md)
