import type { LucideIcon } from "lucide-react";

/**
 * A precondition for a panel to render something meaningful (not access
 * control — Forge has no roles/RBAC). If `check()` fails, the panel renders
 * its own "not available yet" state; the host never force-hides it.
 * Unused by any Phase 01 panel — shape may evolve once one needs it (e.g. a
 * future Model Playground panel), per 12_PANEL_INTERFACE.md §8, §11.
 */
export interface WorkbenchPanelPrecondition {
  description: string;
  check: () => boolean;
}

export interface WorkbenchPanelMetadata {
  title: string;
  description: string;
  icon: LucideIcon;
  defaultVisible: boolean;
  minColumnSpan?: number;
  permissions?: WorkbenchPanelPrecondition[];
}

export interface WorkbenchPanelProps {
  mode: "view" | "customize";
  onError: (error: unknown) => void;
}

export interface WorkbenchPanelDefinition {
  type: string;
  metadata: WorkbenchPanelMetadata;
  component: React.ComponentType<WorkbenchPanelProps>;
}
