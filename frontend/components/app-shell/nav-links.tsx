"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";
import { getGroupedNavItems, getUtilityNavItems, type NavItem } from "@/lib/nav-registry";

// Shared between Sidebar (desktop rail) and MobileNav (drawer) so both
// render from one grouped structure and one active-state rule, not two
// independently-maintained loops — the audit's §6.4 finding (pre-Phase-09,
// the two diverged in their active-state classes). `variant` only changes
// which colour-token family is used: "rail" sits on the --sidebar-* surface,
// "drawer" sits on the regular --background inside a Sheet.
export function NavLinks({
  variant,
  onNavigate,
}: {
  variant: "rail" | "drawer";
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const groups = getGroupedNavItems();
  const utilityItems = getUtilityNavItems();

  function isActive(href: string) {
    return href === "/" ? pathname === "/" : pathname.startsWith(href);
  }

  function linkClass(active: boolean) {
    if (variant === "rail") {
      return cn(
        "group flex items-center gap-2.5 rounded-lg border-l-2 border-transparent px-2.5 py-1.5 text-sm transition-colors",
        active
          ? "border-sidebar-primary bg-sidebar-accent font-medium text-sidebar-accent-foreground"
          : "text-sidebar-foreground/70 hover:bg-sidebar-accent/60 hover:text-sidebar-foreground",
      );
    }
    return cn(
      "group flex items-center gap-2.5 rounded-lg border-l-2 border-transparent px-2.5 py-2 text-sm transition-colors",
      active
        ? "border-primary bg-accent font-medium text-accent-foreground"
        : "text-foreground/70 hover:bg-accent/60 hover:text-foreground",
    );
  }

  function iconClass(active: boolean) {
    if (variant === "rail") {
      return cn("h-4 w-4 shrink-0", active ? "text-sidebar-primary" : "text-sidebar-foreground/50");
    }
    return cn("h-4 w-4 shrink-0", active ? "text-primary" : "text-foreground/50");
  }

  function renderItem(item: NavItem) {
    const active = isActive(item.href);
    const Icon = item.icon;
    return (
      <Link key={item.href} href={item.href} onClick={onNavigate} className={linkClass(active)}>
        <Icon className={iconClass(active)} />
        <span className="truncate">{item.title}</span>
      </Link>
    );
  }

  return (
    <>
      <nav aria-label="Primary" className="flex flex-1 flex-col gap-4 overflow-y-auto px-3 py-2">
        {groups.map(({ group, label, items }) => {
          const labelId = `nav-group-${group}`;
          return (
            <div key={group} role="group" aria-labelledby={labelId} className="flex flex-col gap-0.5">
              <div id={labelId} className="label-structural px-2.5 pb-1">
                {label}
              </div>
              {items.map(renderItem)}
            </div>
          );
        })}
      </nav>

      <div
        className={cn(
          "border-t px-3 py-2",
          variant === "rail" ? "border-sidebar-border" : "border-border",
        )}
      >
        {utilityItems.map(renderItem)}
      </div>
    </>
  );
}
