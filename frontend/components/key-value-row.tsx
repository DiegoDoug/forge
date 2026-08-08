import { cn } from "@/lib/utils";

// Tabular metadata row — secret detail, project detail, Settings' About
// card. Tabular numerals so values in a stacked list line up.
export function KeyValueRow({
  label,
  value,
  className,
}: {
  label: string;
  value: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex items-center justify-between gap-4 py-1 text-xs", className)}>
      <span className="text-muted-foreground">{label}</span>
      <span className="data-meta font-medium text-foreground">{value}</span>
    </div>
  );
}
