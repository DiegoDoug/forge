"use client";

import { SlidersHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";

// Owns the rail-at-lg / drawer-below-lg responsive contract (invariant I4,
// 02_UI.md §4). Secrets (w-56, no responsive handling at all) and Documents
// (w-72, same defect) are the two surfaces this replaces — see 00_AUDIT.md
// §5.2. Content is passed as `children`; this component owns geometry and
// the breakpoint switch only, never filter semantics (those stay
// feature-owned, e.g. features/secrets/secrets-filters.tsx).
//
// Below `lg`, the exact same `children` render inside a Sheet triggered
// from the toolbar — not a second, parallel implementation of the filter
// UI, so the two can never drift out of sync with each other.
export function FilterRail({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <>
      <aside className="hidden w-[var(--shell-filter-rail-w)] shrink-0 flex-col gap-6 overflow-y-auto border-r border-border p-4 lg:flex">
        {children}
      </aside>

      <div className="lg:hidden">
        <Sheet>
          <SheetTrigger
            render={
              <Button variant="outline" size="sm" aria-label={`Open ${title.toLowerCase()}`} />
            }
          >
            <SlidersHorizontal className="h-3.5 w-3.5" />
            {title}
          </SheetTrigger>
          <SheetContent side="left" className="w-72 overflow-y-auto">
            <SheetTitle className="p-4 pb-0">{title}</SheetTitle>
            <div className="flex flex-col gap-6 p-4">{children}</div>
          </SheetContent>
        </Sheet>
      </div>
    </>
  );
}
