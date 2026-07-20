# Research

> **Purpose:** Home for exploratory material — competitor scans, benchmarks, raw ideas, and reference links — that informs FDK decisions but isn't itself a spec, principle, or ADR.
> **Scope:** Brainstorming and evidence-gathering only. Once an idea here is ready to become real scope, it moves into a phase's `01_SPEC.md` (or a new phase in [`../02_ROADMAP.md`](../02_ROADMAP.md)); once a technical choice here is ready to become a commitment, it moves into an ADR under [`../decisions/`](../decisions/README.md).
> **Ownership:** TODO — assign an owner.
> **Status:** Active
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** —
> **Supersedes:** —

---

## 1. Why this folder exists

Implementation docs (`implementation/Phase-XX-*/`) are meant to stay authoritative and buildable — not cluttered with half-formed ideas, competitor screenshots, or "what if we also did X" tangents. Those belong here instead, so a spec never has to answer for content nobody has committed to yet.

## 2. Subfolders

| Folder | Contains |
|---|---|
| [benchmarks/](benchmarks/README.md) | Performance/UX benchmarks against comparable tools, and Forge's own measurements over time |
| [competitors/](competitors/README.md) | Notes on adjacent tools (Bitwarden, DevToys, Notion, etc.) — what they do, not to copy but to know the intersection Forge should cover (see [`../00_VISION.md`](../00_VISION.md) §4) |
| [ideas/](ideas/README.md) | Raw, unscoped feature ideas that haven't earned a roadmap slot yet |
| [future-features/](future-features/README.md) | Ideas that have graduated past "raw" — worth a real look next time [`../02_ROADMAP.md`](../02_ROADMAP.md) is revisited, but not yet a phase |
| [references/](references/README.md) | External links, articles, and prior art worth remembering |

## 3. Promotion path

1. An idea starts in `ideas/` as a short, informal note.
2. If it survives scrutiny and looks like real scope, it moves to `future-features/` with a bit more shape (why it matters, rough size).
3. When it's ready to be sequenced, it becomes a row in [`../02_ROADMAP.md`](../02_ROADMAP.md) §3 and, once started, a phase folder under [`../implementation/`](../implementation/README.md).
4. Any technical choice made along the way that would bind a future phase gets its own ADR in [`../decisions/`](../decisions/README.md) — research notes are not a substitute for that record.

## 4. TODO

- [ ] TODO: Populate each subfolder with real content as it accumulates — this structure is intentionally empty at creation time.

## 5. Cross-references

- [../README.md](../README.md)
- [../00_VISION.md](../00_VISION.md)
- [../02_ROADMAP.md](../02_ROADMAP.md)
- [../decisions/README.md](../decisions/README.md)
