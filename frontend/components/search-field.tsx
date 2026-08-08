"use client";

import { Search, X } from "lucide-react";

import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

// Consolidates the 6 hand-rolled copies of "absolutely-positioned search
// icon + Input" the Phase 09 audit found (Secrets, Notes, Search, Documents
// rail, Prompt Studio rail, Knowledge filter bar) — see 00_AUDIT.md §6.1.
// Adds a clear affordance none of the 6 originals had; every other prop
// mirrors the plain <Input> each site already used, so this is a drop-in
// replacement, not a behavior change.
export function SearchField({
  value,
  onChange,
  placeholder = "Search…",
  autoFocus,
  className,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("relative", className)}>
      <Search className="pointer-events-none absolute top-1/2 left-2.5 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
      <Input
        type="search"
        role="searchbox"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className={cn("pl-8", value ? "pr-8" : undefined)}
      />
      {value ? (
        <button
          type="button"
          aria-label="Clear search"
          onClick={() => onChange("")}
          className="absolute top-1/2 right-2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      ) : null}
    </div>
  );
}
