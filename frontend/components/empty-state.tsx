import type { LucideIcon } from "lucide-react";

// Retuned to Rams (Phase 09 T6): the dashed border and tinted icon chip read
// as decoration without function, so both are dropped — a plain outline
// icon on a quiet border communicates "nothing here yet" just as clearly.
// API unchanged: same props, same names, no consumer needs to change.
export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-border px-6 py-16 text-center">
      <Icon className="h-8 w-8 text-muted-foreground/50" />
      <div>
        <p className="text-sm font-medium">{title}</p>
        {description ? <p className="mt-1 max-w-sm text-sm text-muted-foreground">{description}</p> : null}
      </div>
      {action}
    </div>
  );
}
