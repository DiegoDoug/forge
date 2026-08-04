"use client";

import { useRouter } from "next/navigation";
import { FileText, StickyNote } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { formatRelativeTime } from "@/lib/format";
import type { KnowledgeItem } from "./api";

function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
}

// Navigation is landing-on-the-feature, not per-item deep linking, per
// 02_UI.md SS1.1: Documents supports ?open={id} (real deep link, confirmed
// in app/(app)/documents/page.tsx), Notes has no per-note route (it's a
// free-positioned canvas board) - the Hub uses what each feature actually
// supports rather than guessing.
function targetHref(item: KnowledgeItem): string {
  return item.type === "document" ? `/documents?open=${item.id}` : "/notes";
}

export function KnowledgeResultRow({ item }: { item: KnowledgeItem }) {
  const router = useRouter();
  const Icon = item.type === "note" ? StickyNote : FileText;
  const excerpt = item.type === "document" ? stripHtml(item.excerpt) : item.excerpt;

  function activate() {
    router.push(targetHref(item));
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={activate}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activate();
        }
      }}
      className="flex cursor-pointer items-start gap-3 rounded-lg border border-transparent px-3 py-2.5 outline-none hover:bg-accent/50 focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/50"
    >
      <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" aria-hidden="true" />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className="h-4.5 px-1.5 text-[10px] uppercase">
            {item.type}
          </Badge>
          <span className="truncate text-sm font-medium">{item.title}</span>
        </div>
        {excerpt ? <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">{excerpt}</p> : null}
        {item.tags.length > 0 ? (
          <div className="mt-1 flex flex-wrap gap-1">
            {item.tags.map((tag) => (
              <Badge key={tag.id} variant="secondary" className="h-4.5 px-1.5 text-[10px]">
                {tag.name}
              </Badge>
            ))}
          </div>
        ) : null}
      </div>
      <span className="shrink-0 text-[11px] text-muted-foreground">{formatRelativeTime(item.updated_at)}</span>
    </div>
  );
}
