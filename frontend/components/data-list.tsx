import Link from "next/link";

import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

// The Swiss data surface (design brief: "density with hierarchy, not
// density instead of it"). Replaces the 7 independently hand-rolled
// `rounded-xl border border-border` list containers the audit found
// (Secrets, Search, Knowledge, Ingest jobs, project scoped lists,
// generation history, run history) — see 00_AUDIT.md §6.1, 05_COMPONENTS.md
// §3.2. Owns row rhythm and rule weight; column composition is passed in
// per surface and is not negotiable to this component (05_COMPONENTS.md).
//
// Loading/empty/error are deliberately NOT built into DataList itself —
// compose it with DataListSkeleton, and the shared EmptyState/ErrorState
// (components/empty-state.tsx, components/error-state.tsx) at the call
// site, matching how every existing list screen already branches on
// isLoading/isEmpty/isError. One rhythm, reused failure/empty treatments,
// no fourth reimplementation of either.
export function DataList({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("overflow-hidden rounded-xl border border-border", className)}>
      <div className="divide-y divide-border">{children}</div>
    </div>
  );
}

type DataListRowBaseProps = {
  children: React.ReactNode;
  selected?: boolean;
  className?: string;
};

type DataListRowProps =
  | (DataListRowBaseProps & { href: string; onClick?: never })
  | (DataListRowBaseProps & { onClick: () => void; href?: never })
  | (DataListRowBaseProps & { href?: undefined; onClick?: undefined });

// One row rhythm (invariant I6: 40px desktop / 48px touch), shared by every
// data surface. `.data-primary`/`.data-meta` (globals.css) are the intended
// typography for a row's title and metadata — apply them to children
// directly; this component only owns height, padding, alignment, and state.
export function DataListRow({ children, selected, href, onClick, className }: DataListRowProps) {
  const stateClasses = cn(
    "flex min-h-[var(--row-height-comfy)] w-full items-center gap-3 px-[var(--row-pad-x)] text-left transition-colors lg:min-h-[var(--row-height)]",
    selected ? "bg-accent" : "hover:bg-accent/40",
    className,
  );

  if (href) {
    return (
      <Link href={href} className={stateClasses} aria-current={selected ? "true" : undefined}>
        {children}
      </Link>
    );
  }

  if (onClick) {
    return (
      <button type="button" onClick={onClick} className={stateClasses} aria-current={selected ? "true" : undefined}>
        {children}
      </button>
    );
  }

  return <div className={stateClasses}>{children}</div>;
}

// Row-shaped skeletons so a loading DataList has no layout shift once real
// rows replace them (04_UI_GUIDELINES.md §5).
export function DataListSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <DataList>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex min-h-[var(--row-height-comfy)] items-center gap-3 px-[var(--row-pad-x)] lg:min-h-[var(--row-height)]">
          <Skeleton className="h-4 w-4 shrink-0 rounded-full" />
          <Skeleton className="h-4 flex-1 max-w-xs" />
          <Skeleton className="h-4 w-16 shrink-0" />
        </div>
      ))}
    </DataList>
  );
}
