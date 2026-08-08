"use client";

import { Flame } from "lucide-react";

import { NavLinks } from "./nav-links";

export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-sidebar-border bg-sidebar md:flex">
      <div className="flex h-14 items-center gap-2 px-5">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Flame className="h-4 w-4" />
        </div>
        <span className="text-sm font-semibold tracking-tight text-sidebar-foreground">Forge</span>
      </div>

      <NavLinks variant="rail" />

      <div className="border-t border-sidebar-border p-3 text-[11px] text-sidebar-foreground/60">
        Forge · self-hosted
      </div>
    </aside>
  );
}
