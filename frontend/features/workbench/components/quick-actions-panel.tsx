"use client";

import type { ComponentType } from "react";
import Link from "next/link";
import { KeyRound, StickyNote, Wand2, Zap } from "lucide-react";

import { registerWorkbenchPanel } from "../panel-registry";
import type { WorkbenchPanelProps } from "../panel-types";

const ACTIONS = [
  { title: "New note", href: "/notes?new=1", icon: StickyNote },
  { title: "New secret", href: "/secrets?new=1", icon: KeyRound },
  // Points straight at the unified page's Generators tab rather than the
  // retired /generators route - that route still redirects here (Phase 08,
  // next.config.ts), but a frequently-used action shouldn't pay for the hop.
  { title: "Generate password", href: "/developer-toolkit?tab=generators", icon: Wand2 },
];

// Narrow rail rendering: a single compact row rather than the full-width
// tile grid this used when it shared equal footing with Pinned Tools
// (Phase 10 UX elevation — Quick Actions duplicates Pinned Tools' "jump"
// function, so it moved to the rail as a lower-emphasis shortcut strip).
const QuickActionsPanel: ComponentType<WorkbenchPanelProps> = () => {
  return (
    <div className="flex flex-col gap-1.5">
      {ACTIONS.map((action) => (
        <Link
          key={action.href}
          href={action.href}
          className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm font-medium transition-colors hover:border-primary/40 hover:bg-accent/40"
        >
          <action.icon className="h-4 w-4 shrink-0 text-primary" />
          {action.title}
        </Link>
      ))}
    </div>
  );
};

registerWorkbenchPanel({
  type: "quick_actions",
  metadata: {
    title: "Quick Actions",
    description: "One-click shortcuts into a new note, secret, or password.",
    icon: Zap,
    defaultVisible: true,
    column: "rail",
  },
  component: QuickActionsPanel,
});
