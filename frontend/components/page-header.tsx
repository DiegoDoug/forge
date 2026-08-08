import { cn } from "@/lib/utils";

// v2 (Phase 09 T6): adds an optional breadcrumb slot and a size variant,
// and is now sticky by default — `main` (components/app-shell/app-shell.tsx)
// is the app's one scroll container, so pinning the header while content
// scrolls beneath it is a shell-wide behaviour, not a per-page opt-in.
// `title`/`description`/`actions` are unchanged from v1: same names, same
// types, same rendering — no existing consumer needs to change.
//
// Deliberately NOT included here: overflow-menu collapse for action
// clusters past two (02_UI.md §4). `actions` is an opaque ReactNode, so a
// generic wrapper can't safely introspect and collapse it without breaking
// the "no consumer needs to change" constraint. Screens with 3+ actions
// (Projects, Project detail) apply the collapse themselves when migrated —
// see 09_IMPLEMENTATION_TASKS.md T15.
export function PageHeader({
  title,
  description,
  breadcrumb,
  actions,
  size = "default",
}: {
  title: string;
  description?: string;
  breadcrumb?: React.ReactNode;
  actions?: React.ReactNode;
  size?: "default" | "compact";
}) {
  return (
    <div
      className={cn(
        "sticky top-0 z-10 flex flex-wrap items-start justify-between gap-3 border-b border-border bg-background px-4 md:px-6",
        size === "compact" ? "py-3" : "py-5",
      )}
    >
      <div className="min-w-0">
        {breadcrumb ? <div className="mb-1 flex items-center gap-1 text-xs text-muted-foreground">{breadcrumb}</div> : null}
        <h1 className="heading-page truncate">{title}</h1>
        {description ? <p className="mt-0.5 text-sm text-muted-foreground">{description}</p> : null}
      </div>
      {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
    </div>
  );
}
