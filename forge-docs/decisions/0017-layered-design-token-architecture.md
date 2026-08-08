# ADR-0017 — Layered design tokens, preserving the shadcn semantic contract

> **Purpose:** Record how Phase 09 introduces a real design-token system without breaking the 40 shadcn primitives that depend on the existing token names.
> **Scope:** Frontend token architecture and the aesthetic direction it encodes. No backend change, no component API change.
> **Ownership:** Project owner (aesthetic direction, typography decision, and architecture confirmed 2026-08-06)
> **Status:** **Accepted** — 2026-08-06, alongside the Phase 09 specification.
> **Version:** 0.1.0
> **Last Updated:** 2026-08-06
> **Depends On:** [../implementation/Phase-09-Frontend-Reimagine/01_SPEC.md](../implementation/Phase-09-Frontend-Reimagine/01_SPEC.md), [../05_DESIGN_SYSTEM.md](../05_DESIGN_SYSTEM.md)
> **Supersedes:** —

---

## 1. Context

`frontend/app/globals.css` contains a complete, well-formed shadcn semantic palette — OKLCH values for both themes covering `--background`, `--foreground`, `--card`, `--popover`, `--primary`, `--secondary`, `--muted`, `--accent`, `--destructive`, `--border`, `--input`, `--ring`, five chart colors, a full `--sidebar-*` set, and a derived `--radius` scale. **Forty primitives in `components/ui/` consume those names directly.**

It also contains, and does not contain, the following:

- **A defect.** `--font-sans` is declared as `var(--font-sans)` inside `@theme inline` — a self-reference. Because the block is `inline`, Tailwind emits nothing and the declaration overrides its own default. `html { @apply font-sans }` therefore computes to an invalid `font-family`, and **the entire application renders in the browser's default serif**. Measured in a running browser on 2026-08-06: computed `font-family` `"Times New Roman"` on both `<html>` and `<body>`, `--font-sans` and `--font-mono` both empty, `--font-geist-sans` correctly populated as `"Geist", "Geist Fallback"`. **Corrected at T0.5a:** `--font-mono` was *not* broken — the audit over-read a `:root` measurement. `@theme inline`'s `var(--font-geist-mono)` resolves correctly on descendants of `<body>`, so monospace surfaces always rendered in Geist Mono. Only `--font-sans` failed, because `html { @apply font-sans }` targets the one element outside `<body>`.
- **No type ramp.** Sizes are chosen per component from Tailwind defaults, including arbitrary values like `text-[11px]`.
- **No spacing scale.** `p-4 md:p-6` is re-declared in eleven files.
- **No status roles.** Only `--destructive` exists; success, warning, and info are hardcoded per component.
- **No motion tokens**, and no `prefers-reduced-motion` anywhere in the codebase.
- **No shell or density constants.** Three files hardcode viewport arithmetic against the topbar height.

[`../05_DESIGN_SYSTEM.md`](../05_DESIGN_SYSTEM.md) has carried "document the full palette", "define semantic color roles", "document the font family/scale", "document the spacing scale", and "document transition durations" as open TODOs since the project began.

## 2. Decision

**2.1 — A three-layer token architecture, in `globals.css`, added to rather than replacing what exists.**

| Layer | Contents | Who may reference it |
|---|---|---|
| **1 — Foundation** | Raw ramps: `--forge-neutral-*`, `--forge-accent-*`, status hues, `--space-*`, `--font-size-*`, weights, line-heights, letter-spacings, durations, easings, breakpoints | Layer 2 only. **Never a component.** |
| **2 — Semantic** | The role tokens. Every existing shadcn name, re-expressed in Layer 1 terms, **plus** the missing roles: `--success`/`--warning`/`--info` (each with `-subtle` and `-border` variants), `--border-subtle`/`--border-strong`, `--elevation-0..3`, `--overlay-scrim` | Components. This is the only layer they touch. |
| **3 — Structural** | `--shell-topbar-h`, `--shell-rail-w`, `--shell-filter-rail-w`, `--shell-detail-rail-w`, `--row-height`, `--control-height-*`, `--touch-target-min`, `--max-width-prose` | The shell and shared components |

**2.2 — Every existing shadcn token name is preserved verbatim.** Additions only. No rename, no removal.

**2.3 — The typography defect is fixed by binding `--font-sans` and `--font-mono` to the real `next/font` variables at `:root`, outside `@theme inline`,** with proper fallback stacks. No new font is introduced.

**2.4 — The system encodes one aesthetic direction: Dieter Rams functionalist, with Swiss typographic treatment on data-dense surfaces.** Confirmed by the project owner, 2026-08-06. The Swiss seam is exactly three CSS utilities — `.label-structural`, `.data-primary`, `.data-meta` — applied *inside* Rams containers. Swiss never makes container, spacing, or colour decisions. Anything not using those three utilities is Rams by default.

**2.5 — Dark mode stays on the `.dark` class selector.**

## 3. Alternatives considered

### 3.1 Replace the shadcn tokens with a purpose-built naming scheme — rejected

Names like `--color-bg-primary` / `--color-text-secondary` (as the `design-tokens` skill's template suggests) would be more self-describing. But 40 primitives consume the shadcn names, so this is a 40-file breaking change whose entire benefit is nomenclature. The skill itself instructs *"if tokens already exist, extend them rather than replacing"* — the existing layer is not the problem; the missing layers are.

### 3.2 Introduce a distinctive display/body font pairing — rejected, deliberately

The `frontend-design` skill instructs: *"Choose distinctive fonts loaded via Google Fonts or CDN. Avoid generic defaults... Pair a display font with a body font."* Forge deviates, with owner confirmation:

- Forge is **self-hosted, LAN-first, and frequently offline**. A CDN font dependency is a runtime failure mode, not a design choice.
- Geist and Geist Mono are already installed, already downloaded on every page load, and already self-hosted by `next/font`. The bug is that they were never *connected*. Wiring them up is strictly smaller and safer than adding a face.
- Geist is not a generic default — it is a technical grotesque designed for developer tooling. The Sans/Mono pairing *is* the display/body pairing the skill asks for; on these screens mono is a semantic register (keys, hashes, IDs, code), not a decorative one.

### 3.3 `[data-theme="dark"]` plus a `prefers-color-scheme` media query — rejected

The `design-tokens` skill recommends both. Forge cannot adopt either without breakage:

- `next-themes` runs with `attribute="class"`, and `globals.css` declares `@custom-variant dark (&:is(.dark *))`. Every `dark:` utility in the codebase depends on the class. Switching selectors would break theming app-wide to satisfy a naming preference.
- Adding a `prefers-color-scheme` media query would create a *second* authority for the theme. `next-themes` already resolves the system preference (`enableSystem`) into the class, and theme choice is additionally persisted server-side via `settingsApi.updateTheme`. A media query would conflict with both.

### 3.4 A 16px base body size — rejected in favour of a targeted fix

The skill sets a 16px mobile floor to prevent iOS input zoom. That hazard is specific to form controls, so it is solved precisely: input, select, and textarea are raised to 16px below the `md` breakpoint, while dense UI text stays at 14px — correct for a developer tool with this much surface per screen.

### 3.5 Re-pick the accent hue for a more Braun-like Rams palette — rejected

Warmer, more restrained accents were considered. Rejected because Phase 09's stated success criterion is that an existing user *"should recognize the same product"*, and hue is the strongest recognition cue Forge has. What changes is how much the accent is **used**: strictly functional (active state, focus, primary action), never decorative.

### 3.6 A separate `tokens.css` file — rejected

Portable, but it splits the source of truth. `components.json` names `app/globals.css` as the Tailwind CSS entry, and shadcn tooling writes there. One file, three clearly-commented layers.

## 4. Consequences

**Makes easier**
- Forge renders in its intended typeface for the first time.
- Retuning the visual system becomes a token edit, not a sweep across 60+ components.
- Status, motion, elevation, and density stop being per-component judgement calls.
- `--shell-topbar-h` retires three hardcoded viewport calculations.
- WCAG AA becomes checkable at the token layer instead of per component — a contrast budget is enumerated at the foot of the tokens file, and `04_UI_GUIDELINES.md` §4's standing "define a minimum contrast standard" TODO is finally answerable.
- `05_DESIGN_SYSTEM.md`'s five open TODOs become documentable facts.

**Makes harder / forecloses**
- Two vocabularies now coexist: shadcn semantic names (`--muted-foreground`) and Forge foundation names (`--forge-neutral-500`). Mitigated by the hard rule that components touch Layer 2 only — but it is a rule people can break.
- A single global CSS change affects all 40 primitives at once. This is the phase's highest-risk task and is why T1 is sequenced first and alone, verified before any screen work begins.
- The Rams/Swiss seam can spread. Bounded to three utilities and re-stated in `IMPLEMENT.md` as a named failure mode, but it needs watching at design review.
- Committing to Rams forecloses more expressive directions without a new decision.

**Principles and invariants touched**
- Fills [`../05_DESIGN_SYSTEM.md`](../05_DESIGN_SYSTEM.md), which has been a stub with real configuration facts and no token table since it was written.
- Answers [`../04_UI_GUIDELINES.md`](../04_UI_GUIDELINES.md) §4's contrast-standard TODO and §6's motion-policy TODO.
- Touches no architectural invariant in [`../03_ARCHITECTURE.md`](../03_ARCHITECTURE.md) §2 — this is presentation only.

## 5. Cross-references

- [../../.design/frontend-reimagine/DESIGN_TOKENS.css](../../.design/frontend-reimagine/DESIGN_TOKENS.css) — the proposed token file
- [../../.design/frontend-reimagine/DESIGN_BRIEF.md](../../.design/frontend-reimagine/DESIGN_BRIEF.md) — the philosophy this encodes
- [../implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md](../implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md) §3.1, §2.5
- [../implementation/Phase-09-Frontend-Reimagine/01_SPEC.md](../implementation/Phase-09-Frontend-Reimagine/01_SPEC.md) FR1, FR2
- [../04_UI_GUIDELINES.md](../04_UI_GUIDELINES.md) · [../05_DESIGN_SYSTEM.md](../05_DESIGN_SYSTEM.md) · [../06_TECH_STACK.md](../06_TECH_STACK.md)
