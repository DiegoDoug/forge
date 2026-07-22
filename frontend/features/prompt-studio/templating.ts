/**
 * ${name} placeholder substitution - the TypeScript mirror of
 * backend/app/services/prompt_studio/templating.py. Rendering-determinism
 * constraint (01_SPEC.md §3.16, project-owner requirement): this module
 * performs substitution, escaping, and validation only - never a conditional,
 * loop, function call, filter, include, or import. Never replace this with a
 * templating library (Handlebars, Mustache, etc.); that would be a new
 * architectural decision, not an incremental change here.
 */

const PLACEHOLDER_PATTERN = /\$\$|\$([A-Za-z_][A-Za-z0-9_]*)|\$\{([A-Za-z_][A-Za-z0-9_]*)\}/g;

/** Every distinct ${name} referenced in body, using the same pattern substitute() below scans with. */
export function extractPlaceholders(body: string): Set<string> {
  const names = new Set<string>();
  for (const match of body.matchAll(PLACEHOLDER_PATTERN)) {
    const name = match[1] ?? match[2];
    if (name) names.add(name);
  }
  return names;
}

export interface SubstituteResult {
  rendered: string;
  missing: string[];
}

/**
 * Best-effort client-side preview substitution. Unlike the backend's strict
 * substitute() (which raises on a missing key), this always returns a
 * renderable string - a missing/blank required variable keeps its ${name}
 * token visible in the output and is also reported in `missing`, so the
 * caller can highlight it as unresolved rather than silently rendering an
 * empty string (01_SPEC.md §3.5).
 */
export function substitute(body: string, values: Record<string, string>): SubstituteResult {
  const missing = new Set<string>();
  const rendered = body.replace(PLACEHOLDER_PATTERN, (match, named?: string, braced?: string) => {
    if (match === "$$") return "$";
    const name = named ?? braced;
    if (!name) return match;
    const value = values[name];
    if (value === undefined || value === "") {
      missing.add(name);
      return `\${${name}}`;
    }
    return value;
  });
  return { rendered, missing: Array.from(missing) };
}
