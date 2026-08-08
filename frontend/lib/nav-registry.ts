import {
  FileText,
  FlaskConical,
  FolderKanban,
  KeyRound,
  LayoutDashboard,
  Library,
  MessageSquareText,
  Settings,
  Sparkles,
  StickyNote,
  Repeat,
  Wrench,
  type LucideIcon,
} from "lucide-react";

// Phase 09 grouping axis — stored / authored / applied. See
// forge-docs/implementation/Phase-09-Frontend-Reimagine/02_UI.md §1.1 and
// ADR-0016 §2.1. "utility" is not a group tab; it renders pinned below a
// divider, outside the four labelled sections (Settings only).
export type NavGroup = "workspace" | "library" | "build" | "tools" | "utility";

export const NAV_GROUP_LABELS: Record<Exclude<NavGroup, "utility">, string> = {
  workspace: "Workspace",
  library: "Library",
  build: "Build",
  tools: "Tools",
};

// Display order of the four labelled groups. "utility" is excluded — it
// renders separately, pinned below a divider (Settings only).
export const NAV_GROUP_ORDER: Exclude<NavGroup, "utility">[] = ["workspace", "library", "build", "tools"];

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  description: string;
  shortcut?: string;
  group: NavGroup;
}

// Additive-only change (Phase 09 T3, AC15): every href/title/icon/shortcut/
// description below, and the array's own order, is byte-identical to the
// pre-Phase-09 registry. Only the `group` field was added to each entry.
// Grouped rendering is done at render time via getGroupedNavItems() below,
// not by reordering this source array — this file stays the single, stable
// source both the Sidebar/MobileNav rail and the command palette render
// from, and it must never fork.
export const NAV_ITEMS: NavItem[] = [
  { title: "Workbench", href: "/", icon: LayoutDashboard, description: "Pinned tools & recent activity", shortcut: "D", group: "workspace" },
  { title: "Secrets", href: "/secrets", icon: KeyRound, description: "Encrypted secrets", shortcut: "V", group: "library" },
  { title: "Notes", href: "/notes", icon: StickyNote, description: "Sticky note board", shortcut: "N", group: "library" },
  { title: "Documents", href: "/documents", icon: FileText, description: "Rich text editor, history & export", group: "library" },
  { title: "Knowledge", href: "/knowledge", icon: Library, description: "Search, tag & link notes and documents", shortcut: "K", group: "library" },
  { title: "Projects", href: "/projects", icon: FolderKanban, description: "Group secrets, notes & documents by workspace", shortcut: "P", group: "workspace" },
  { title: "Converter", href: "/converters", icon: Repeat, description: "Text, data & document conversion", shortcut: "O", group: "tools" },
  // Generators, Crypto, and Utilities were consolidated into one entry by
  // Phase 08 (Developer Toolkit) — see its 01_SPEC.md §3 requirement 3. The
  // Wrench icon and "U" shortcut are inherited from the old Utilities entry;
  // Wand2/"G" and ShieldHalf/"C" are freed. The old routes redirect (see
  // next.config.ts), so nothing that linked to them breaks.
  {
    title: "Developer Toolkit",
    href: "/developer-toolkit",
    icon: Wrench,
    description: "Generators, crypto, and utilities",
    shortcut: "U",
    group: "tools",
  },
  { title: "Project Init", href: "/project-init", icon: Sparkles, description: "Generate FDK scaffolds & AI instructions", group: "build" },
  { title: "Prompt Studio", href: "/prompt-studio", icon: MessageSquareText, description: "Author, version & preview LLM prompts", group: "build" },
  { title: "Model Playground", href: "/model-playground", icon: FlaskConical, description: "Compare LLM provider outputs side by side", group: "build" },
  { title: "Settings", href: "/settings", icon: Settings, description: "Theme, backup, about", shortcut: ",", group: "utility" },
];

// Buckets NAV_ITEMS into NAV_GROUP_ORDER's four sections, preserving each
// item's relative order within its group. Excludes "utility" items (Settings)
// — consumers render those separately, pinned below a divider.
export function getGroupedNavItems(): { group: Exclude<NavGroup, "utility">; label: string; items: NavItem[] }[] {
  return NAV_GROUP_ORDER.map((group) => ({
    group,
    label: NAV_GROUP_LABELS[group],
    items: NAV_ITEMS.filter((item) => item.group === group),
  }));
}

export function getUtilityNavItems(): NavItem[] {
  return NAV_ITEMS.filter((item) => item.group === "utility");
}
