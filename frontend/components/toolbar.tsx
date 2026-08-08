import { cn } from "@/lib/utils";

// Owns spacing/wrap behaviour for the above-list control row pattern
// repeated across Secrets, Notes, Knowledge, and Documents (search field +
// filter pickers, above a list or board).
export function Toolbar({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-wrap items-center gap-2 border-b border-border p-3", className)}>
      {children}
    </div>
  );
}
