"use client";

import { FileText, StickyNote } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { DataListRow } from "@/components/data-list";
import { formatRelativeTime } from "@/lib/format";
import type { KnowledgeItem } from "./api";

function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
}

// Both target features support a real per-item deep link:
// `/documents?open={id}` (app/(app)/documents/page.tsx) and
// `/notes?open={id}` - the same contract the command palette and /search
// already use (see 11_SCREEN_GRAPH.md SS5.3). Previously this routed notes
// to a bare `/notes`, dropping the user on the board with no indication of
// which note they clicked.
function targetHref(item: KnowledgeItem): string {
  return item.type === "document" ? `/documents?open=${item.id}` : `/notes?open=${item.id}`;
}

export function KnowledgeResultRow({ item }: { item: KnowledgeItem }) {
  const Icon = item.type === "note" ? StickyNote : FileText;
  const excerpt = item.type === "document" ? stripHtml(item.excerpt) : item.excerpt;

  return (
    <DataListRow href={targetHref(item)} className="items-start gap-3 py-2.5">
      <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" aria-hidden="true" />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className="h-4.5 px-1.5 text-[10px] uppercase">
            {item.type}
          </Badge>
          <span className="data-primary truncate">{item.title}</span>
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
      <span className="data-meta shrink-0">{formatRelativeTime(item.updated_at)}</span>
    </DataListRow>
  );
}
