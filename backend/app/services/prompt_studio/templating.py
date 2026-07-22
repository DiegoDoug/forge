"""Deterministic ${name} placeholder substitution for prompt bodies.

Rendering-determinism constraint (project-owner requirement, spec review
2026-07-22 - see forge-docs/implementation/Phase-03-Prompt-Studio/01_SPEC.md
§3.16): this module performs substitution, escaping, and validation only.
It must never grow a conditional, loop, function call, filter, include, or
import - string.Template is used specifically because it has no expression
language at all, so that guarantee is a property of the tool, not just a
policy on top of it. Do not replace this with Jinja2 or any other templating
engine; that would be a new architectural decision, not an incremental change
here.
"""

from __future__ import annotations

from string import Template


def extract_placeholders(body: str) -> set[str]:
    """Every distinct ${name} referenced in body, using string.Template's own
    pattern so extraction can never disagree with substitution."""
    names: set[str] = set()
    for match in Template.pattern.finditer(body):
        name = match.group("named") or match.group("braced")
        if name:
            names.add(name)
    return names


def substitute(body: str, values: dict[str, object]) -> str:
    """Strict substitution - raises KeyError via string.Template if a
    referenced name is missing from values. Callers that need a
    best-effort/partial render should catch that and surface the missing
    names, not silently render empty strings."""
    return Template(body).substitute(values)
