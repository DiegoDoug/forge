# Document Header Block

> **Purpose:** Canonical shape of the frontmatter block used at the top of every `forge-docs` file, defined once instead of duplicated by hand across every root and phase doc.
> **Scope:** The header block and its versioning convention only — not a full document template.
> **Ownership:** TODO — assign an owner.
> **Status:** Active
> **Version:** 1.0.0
> **Last Updated:** 2026-07-20
> **Depends On:** —
> **Supersedes:** The pre-versioning header shape (Purpose/Scope/Ownership/Status/Last Updated only) used before 2026-07-20.

---

## 1. The block

Every `forge-docs` Markdown file opens with:

```markdown
# NN — Title

> **Purpose:** One sentence — why this document exists.
> **Scope:** One or two sentences — what it covers and, more importantly, what it explicitly defers to another document.
> **Ownership:** Who owns keeping this current (or `TODO — assign an owner`).
> **Status:** Draft | Active | Deprecated | Superseded by <doc>
> **Version:** Semantic version of this document's content (MAJOR.MINOR.PATCH — see §2).
> **Last Updated:** YYYY-MM-DD
> **Depends On:** Other docs whose content this one assumes/builds on (or `—` if none).
> **Supersedes:** A prior document or convention this replaces (or `—` if none).

---
```

## 2. Versioning a document

- **PATCH** (`0.1.0` → `0.1.1`) — typo fixes, cross-reference updates, no meaning change.
- **MINOR** (`0.1.0` → `0.2.0`) — a new section added, or existing guidance clarified/extended without contradicting prior guidance.
- **MAJOR** (`0.x.0` → `1.0.0`) — a decision this document made is reversed or replaced. Pair this with an entry in [`../../decisions/README.md`](../../decisions/README.md) when the reversal is architectural.
- New documents start at `0.1.0` while `Status: Draft`. Move to `1.0.0` when the project owner ratifies it and `Status` becomes `Active`.

## 3. Depends On / Supersedes

- **Depends On** lists documents whose facts this one assumes are current — e.g. a phase's `03_BACKEND.md` depends on the root `03_ARCHITECTURE.md`. Not every cross-reference belongs here, only load-bearing ones: if the referenced doc changes in a way that contradicts this one, this one is now wrong and needs a re-read.
- **Supersedes** is set only when a document fully replaces the guidance of a prior one. Leave both fields as `—` when not applicable — never delete the line, so the shape stays scannable across files.

## 4. Usage

Use this block verbatim (fill in the bracketed/em-dash placeholders) at the top of every new `forge-docs` file — root doc, phase doc, ADR, or checkpoint log entry.

Retrofit status as of 2026-07-20: the 12 root docs, `README.md`, `decisions/`, `history/`, and `templates/` index docs use this shape. `implementation/Phase-01-Workbench/` uses it as of its spec pass. `implementation/Phase-02-*` through `Phase-08-*` still use the pre-versioning shape — retrofit each when that phase's spec work begins, not speculatively ahead of it.

## 5. Cross-references

- [../README.md](../README.md)
- [../../decisions/README.md](../../decisions/README.md) — where a MAJOR version bump on an architectural doc likely needs a paired ADR
