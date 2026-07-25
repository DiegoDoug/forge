import { Search, Sparkles, type LucideIcon } from "lucide-react";

import { NAV_ITEMS } from "@/lib/nav-registry";

export interface ToolMetadata {
  key: string;
  title: string;
  description: string;
  icon: LucideIcon;
  href: string;
}

// Maps a WORKBENCH_TOOL_KEYS key (backend/app/services/workbench.py §3) to
// its nav-registry.ts href. Manually synced, like the backend catalog itself
// is manually synced with nav-registry.ts (03_BACKEND.md §3's documented,
// tracked gap) - not a bug, the same known seam on the frontend side.
//
// "/ingest" was removed here as part of Universal Converter (Phase 04)
// Milestone 5 - the page was consolidated into "/converters" (see
// Phase-04-Universal-Converter/01_SPEC.md §3), and the backend's matching
// "ingest" tool key was retired alongside it.
const NAV_KEY_BY_HREF: Record<string, string> = {
  "/secrets": "secrets",
  "/notes": "notes",
  "/documents": "documents",
  "/generators": "generators",
  "/crypto": "crypto",
  "/converters": "converters",
  "/utilities": "utilities",
};

// Tool-catalog keys with no frontend/lib/nav-registry.ts entry: Search isn't
// a permanent sidebar item (ADR-0007). Prompt Studio does have a nav-registry
// entry now (Phase 03 shipped), but keeps its own metadata here too since its
// icon differs from the sidebar's (MessageSquareText) - this entry is what
// the Workbench pinned-tools tile renders, matching Search's precedent of a
// tool having its own Workbench-facing metadata distinct from the sidebar's.
//
// The forward-looking "universal_converter" placeholder that used to live
// here (anticipating Phase 04) was removed rather than activated: Phase 04's
// actual design unified Converters and Ingest into the single existing
// "/converters" page rather than shipping a separate tile, so "converters"
// (mapped above from nav-registry.ts, unchanged) already covers it.
const EXTRA_TOOL_METADATA: Record<string, Omit<ToolMetadata, "key">> = {
  search: { title: "Search", description: "Search secrets, notes, and documents", icon: Search, href: "/search" },
  prompt_studio: {
    title: "Prompt Studio",
    description: "Author and version LLM prompts",
    icon: Sparkles,
    href: "/prompt-studio",
  },
};

export function getToolMetadataMap(): Record<string, ToolMetadata> {
  const map: Record<string, ToolMetadata> = {};

  for (const item of NAV_ITEMS) {
    const key = NAV_KEY_BY_HREF[item.href];
    if (key) map[key] = { key, title: item.title, description: item.description, icon: item.icon, href: item.href };
  }
  for (const [key, meta] of Object.entries(EXTRA_TOOL_METADATA)) {
    map[key] = { key, ...meta };
  }

  return map;
}
