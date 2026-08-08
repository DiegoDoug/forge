import { AlertCircle, AlertTriangle, CheckCircle2, Info, type LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

export type StatusTone = "success" | "warning" | "danger" | "info" | "neutral";

const TONE_ICON: Record<StatusTone, LucideIcon | null> = {
  success: CheckCircle2,
  warning: AlertTriangle,
  danger: AlertCircle,
  info: Info,
  neutral: null,
};

const TONE_CLASS: Record<StatusTone, string> = {
  success: "bg-success-subtle text-success border-success-border",
  warning: "bg-warning-subtle text-warning border-warning-border",
  danger: "bg-danger-subtle text-destructive border-danger-border",
  info: "bg-info-subtle text-info border-info-border",
  neutral: "bg-muted text-muted-foreground border-transparent",
};

// Consumes the --success/--warning/--info status roles Phase 09 added
// (only --destructive existed pre-phase — 00_AUDIT.md §2.5). Colour is
// never the only signal: every tone pairs with an icon by default
// (04_UI_GUIDELINES.md §4) — pass `icon={null}` explicitly to opt out for a
// label that already carries the meaning in text (e.g. a column of terse
// "Active"/"Archived" pills next to other unambiguous context).
export function StatusBadge({
  tone,
  icon,
  children,
  className,
}: {
  tone: StatusTone;
  icon?: LucideIcon | null;
  children: React.ReactNode;
  className?: string;
}) {
  const Icon = icon === undefined ? TONE_ICON[tone] : icon;
  return (
    <span
      className={cn(
        "inline-flex h-5 w-fit shrink-0 items-center gap-1 rounded-4xl border px-2 py-0.5 text-xs font-medium whitespace-nowrap",
        TONE_CLASS[tone],
        className,
      )}
    >
      {Icon ? <Icon className="h-3 w-3 shrink-0" /> : null}
      {children}
    </span>
  );
}
