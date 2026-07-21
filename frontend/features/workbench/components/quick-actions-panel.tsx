"use client";

import type { ComponentType } from "react";
import Link from "next/link";
import { KeyRound, StickyNote, Wand2, Zap } from "lucide-react";

import { registerWorkbenchPanel } from "../panel-registry";
import type { WorkbenchPanelProps } from "../panel-types";

const ACTIONS = [
  { title: "New note", href: "/notes?new=1", icon: StickyNote },
  { title: "New secret", href: "/secrets?new=1", icon: KeyRound },
  { title: "Generate password", href: "/generators", icon: Wand2 },
];

const QuickActionsPanel: ComponentType<WorkbenchPanelProps> = () => {
  return (
    <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
      {ACTIONS.map((action) => (
        <Link
          key={action.href}
          href={action.href}
          className="flex items-center gap-2 rounded-lg border border-border p-3 text-sm font-medium transition-colors hover:border-primary/40 hover:bg-accent/40"
        >
          <action.icon className="h-4 w-4 text-primary" />
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
  },
  component: QuickActionsPanel,
});
