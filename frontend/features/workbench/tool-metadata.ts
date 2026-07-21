import { Repeat, Search, Sparkles, type LucideIcon } from "lucide-react";

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
const NAV_KEY_BY_HREF: Record<string, string> = {
  "/secrets": "secrets",
  "/notes": "notes",
  "/documents": "documents",
  "/generators": "generators",
  "/crypto": "crypto",
  "/converters": "converters",
  "/utilities": "utilities",
  "/ingest": "ingest",
};

// Tool-catalog keys with no frontend/lib/nav-registry.ts entry: Search isn't
// a permanent sidebar item (ADR-0007), and Prompt Studio / Universal
// Converter don't exist yet (Phases 03/04).
const EXTRA_TOOL_METADATA: Record<string, Omit<ToolMetadata, "key">> = {
  search: { title: "Search", description: "Search secrets, notes, and documents", icon: Search, href: "/search" },
  prompt_studio: {
    title: "Prompt Studio",
    description: "Author and version LLM prompts",
    icon: Sparkles,
    href: "#",
  },
  universal_converter: {
    title: "Universal Converter",
    description: "Unified document and data format conversion",
    icon: Repeat,
    href: "#",
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
