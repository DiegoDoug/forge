# ADR-0016 — Grouped navigation, and one job per search surface

> **Purpose:** Record Phase 09's two information-architecture decisions — grouping the flat sidebar, and resolving the three overlapping search surfaces — including a proposal that was rejected on evidence.
> **Scope:** Frontend information architecture and navigation only. No backend change, no route removed, no search scope changed.
> **Ownership:** Project owner (direction confirmed 2026-08-06; mechanism revised after verification, then approved)
> **Status:** **Accepted** — 2026-08-06, alongside the Phase 09 specification.
> **Version:** 0.1.0
> **Last Updated:** 2026-08-06
> **Depends On:** [../implementation/Phase-09-Frontend-Reimagine/01_SPEC.md](../implementation/Phase-09-Frontend-Reimagine/01_SPEC.md), [0007-search-dedicated-page.md](0007-search-dedicated-page.md), [0015-knowledge-hub-reuses-fts5.md](0015-knowledge-hub-reuses-fts5.md)
> **Supersedes:** —

---

## 1. Context

Phase 09's audit ([`../implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md`](../implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md) §4) found two structural problems in the shipped navigation.

**The sidebar is a flat, unranked list of twelve destinations.** Settings (app configuration) occupies the same visual register as Workbench (the landing surface). Nothing distinguishes persistent stores (Secrets, Notes, Documents, Knowledge) from stateless transforms (Converter, Developer Toolkit) from authoring surfaces (Prompt Studio, Model Playground, Project Init).

**Three surfaces search, with no stated boundary between them.** The ⌘K palette, the `/search` page, and Knowledge Hub. Worse, `/search` is an orphan: it appears in neither `NAV_ITEMS` nor the command palette, and its only entry point anywhere in the application is a Workbench pinned-tool tile. That directly contradicts [`../04_UI_GUIDELINES.md`](../04_UI_GUIDELINES.md) §2 — *"Every feature page is reachable from the sidebar **and** the command palette."*

## 2. Decision

**2.1 — Group the sidebar into four labelled sections, plus a pinned utility item.**

| Group | Items |
|---|---|
| Workspace | Workbench, Projects |
| Library | Secrets, Notes, Documents, Knowledge |
| Build | Prompt Studio, Model Playground, Project Init |
| Tools | Converter, Developer Toolkit |
| *(utility, below a divider)* | Settings |

The axis is **stored / authored / applied** — explainable in one sentence and true for every current item. Groups are static labels, not collapsible accordions: with twelve destinations, hiding any of them costs more than it saves.

`NAV_ITEMS` gains a `group` field **additively**. No `href`, `title`, `icon`, `shortcut`, or `description` value changes.

**2.2 — Give each search surface exactly one job, changing no surface's scope.**

| Surface | Job | Scope |
|---|---|---|
| **⌘K palette** | Find or go to anything, from anywhere. The universal entry point. | Navigate + secrets + notes + documents + session actions |
| **`/search?q=`** | See the full, untruncated result set for a query. The palette's overflow view. | Identical to the palette |
| **`/knowledge`** | Browse, filter, tag, link, and project-scope notes and documents. | Notes + documents |

`/search` gains a command-palette entry and a "View all results" path from the palette, ending its orphan status. Knowledge Hub's copy is adjusted so its `?q=` reads as *a filter within the Hub* rather than global search. Both search surfaces continue to call the same `GET /api/search`, so they cannot disagree.

`/search` stays out of the sidebar deliberately — a persistent nav item for a surface reachable by a global keystroke is redundant. That was ADR-0007's own conclusion and this decision upholds it.

**2.3 — Implement the eight advertised keyboard shortcuts.** `NAV_ITEMS[].shortcut` declares letters that the palette renders but nothing binds. They become palette-scoped accelerators.

## 3. Alternatives considered

### 3.1 Retire `/search` by redirecting it into Knowledge Hub — **rejected on evidence**

This was the option originally proposed to, and selected by, the project owner on 2026-08-06, on the stated premise that *"Knowledge Hub already supersedes it."* **Verification showed the premise is false**, and the proposal was withdrawn before it reached the IA:

- `backend/app/services/search/service.py` queries `secrets_service.list_secrets` **+** `notes_service.search_notes` **+** `documents_service.search_documents`.
- `backend/app/services/knowledge/service.py` queries `notes_service.search_notes` **+** `documents_service.search_documents` only. Per [ADR-0015](0015-knowledge-hub-reuses-fts5.md), Knowledge Hub composes the notes and documents FTS indexes and has **no secrets path at all**.

Knowledge Hub covers strictly less than `/search`. Redirecting would have silently removed the ability to search secrets — a user-visible functionality regression, which Phase 09's charter forbids without exception. The decision in §2.2 achieves the owner's actual goal (one obvious answer to "where do I search?") without changing any surface's scope.

This is recorded rather than quietly corrected, because the failure mode — a plausible consolidation that silently narrows capability — is exactly what a future IA decision is most likely to repeat.

### 3.2 Add `/search` to the sidebar as a thirteenth item — rejected

It would fix the orphan problem, but it grows the nav to satisfy a discoverability issue whose real cause is that `/search` has no relationship to the palette. ADR-0007 already reasoned that a dedicated results page earns its place by *"seeing all matches at once"*, not by being a nav destination. §2.2 makes that relationship explicit instead.

### 3.3 Collapsible nav groups — rejected

Adds persisted state, a collapse animation, and a way for a user to hide a destination and forget it exists. Twelve items do not need hiding.

### 3.4 Restyle the flat list without regrouping — rejected

The lowest-risk option, and it leaves the audit's central IA finding unaddressed. The sidebar's problem is rank, not appearance.

### 3.5 Extend Knowledge Hub to cover secrets — rejected, out of scope

Would make §3.1 viable, but requires a backend change, reopens [ADR-0015](0015-knowledge-hub-reuses-fts5.md), and raises a real question about whether encrypted-credential metadata belongs in a browsable knowledge surface at all. Phase 09 changes no backend.

## 4. Consequences

**Makes easier**
- A user can tell at a glance which destinations store their content, which author artifacts, and which are stateless tools.
- "Where do I search?" has one answer — ⌘K — with a documented path to full results.
- `/search` becomes discoverable without growing the navigation.
- Advertised shortcuts stop being a promise the interface breaks.
- `04_UI_GUIDELINES.md` §2's reachability rule becomes true, having been false since `/search` shipped.

**Makes harder / forecloses**
- Group assignment becomes a decision every future feature must make. The stored/authored/applied axis holds today; a feature that fits none of them will force a fifth group or a rethink.
- Touching `NAV_ITEMS` touches a manually-synced seam: `lib/nav-registry.ts` → `features/workbench/tool-metadata.ts` → backend `WORKBENCH_TOOL_KEYS`. This seam produced Phase 08's `BUG-0001`. Mitigated by making the change additive and by an explicit re-verification criterion (AC16).
- Keeping `/search` means keeping a route whose job overlaps the palette's. That overlap is now *stated* rather than eliminated — the honest outcome, given the scope asymmetry.

**Principles and invariants touched**
- Upholds [`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.7 ("one search") — both surfaces keep sharing one backend contract.
- Upholds, and does not supersede, [ADR-0007](0007-search-dedicated-page.md). Its accepted scope — a `/search` results page reusing `GET /api/search` — is unchanged.
- Does not touch [ADR-0015](0015-knowledge-hub-reuses-fts5.md). Knowledge Hub's index composition is unchanged.
- Does **not** build against [ADR-0008](0008-capability-registry-direction.md). The three registries stay separate; `03_ARCHITECTURE.md` §4's "do not build against it yet" is respected.

## 5. Cross-references

- [../implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md](../implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md) §4
- [../implementation/Phase-09-Frontend-Reimagine/01_SPEC.md](../implementation/Phase-09-Frontend-Reimagine/01_SPEC.md) §6.1
- [../../.design/frontend-reimagine/INFORMATION_ARCHITECTURE.md](../../.design/frontend-reimagine/INFORMATION_ARCHITECTURE.md)
- [0007-search-dedicated-page.md](0007-search-dedicated-page.md) · [0015-knowledge-hub-reuses-fts5.md](0015-knowledge-hub-reuses-fts5.md) · [0008-capability-registry-direction.md](0008-capability-registry-direction.md)
- [../04_UI_GUIDELINES.md](../04_UI_GUIDELINES.md) · [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
