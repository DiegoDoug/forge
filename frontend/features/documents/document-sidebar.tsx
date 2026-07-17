"use client";

import { FileText, Pin, PinOff, Plus, Search, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { formatRelativeTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { DocumentSummary } from "./api";

export function DocumentSidebar({
  documents,
  selectedId,
  query,
  onQueryChange,
  onSelect,
  onNew,
  onTogglePin,
  onDelete,
}: {
  documents: DocumentSummary[];
  selectedId: string | null;
  query: string;
  onQueryChange: (q: string) => void;
  onSelect: (id: string) => void;
  onNew: () => void;
  onTogglePin: (doc: DocumentSummary) => void;
  onDelete: (id: string) => void;
}) {
  const pinned = documents.filter((d) => d.pinned);
  const others = documents.filter((d) => !d.pinned);

  return (
    <aside className="flex w-72 shrink-0 flex-col border-r border-border">
      <div className="flex items-center gap-2 border-b border-border p-3">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute top-1/2 left-2.5 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search documents…"
            className="h-8 pl-8 text-sm"
          />
        </div>
        <Button size="icon-sm" title="New document" onClick={onNew}>
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      <ScrollArea className="min-h-0 flex-1">
        <div className="flex flex-col gap-3 p-2">
          {documents.length === 0 ? (
            <p className="px-2 py-6 text-center text-xs text-muted-foreground">No documents yet.</p>
          ) : (
            <>
              {pinned.length > 0 ? (
                <DocumentGroup
                  label="Pinned"
                  items={pinned}
                  selectedId={selectedId}
                  onSelect={onSelect}
                  onTogglePin={onTogglePin}
                  onDelete={onDelete}
                />
              ) : null}
              <DocumentGroup
                label={pinned.length > 0 ? "History" : undefined}
                items={others}
                selectedId={selectedId}
                onSelect={onSelect}
                onTogglePin={onTogglePin}
                onDelete={onDelete}
              />
            </>
          )}
        </div>
      </ScrollArea>
    </aside>
  );
}

function DocumentGroup({
  label,
  items,
  selectedId,
  onSelect,
  onTogglePin,
  onDelete,
}: {
  label?: string;
  items: DocumentSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onTogglePin: (doc: DocumentSummary) => void;
  onDelete: (id: string) => void;
}) {
  if (items.length === 0) return null;
  return (
    <div>
      {label ? <p className="px-2 pb-1 text-[11px] font-medium tracking-wide text-muted-foreground uppercase">{label}</p> : null}
      <div className="flex flex-col gap-0.5">
        {items.map((doc) => (
          <div
            key={doc.id}
            className={cn(
              "group flex items-center gap-2 rounded-lg px-2 py-2 text-left transition-colors",
              selectedId === doc.id ? "bg-accent text-accent-foreground" : "hover:bg-accent/50",
            )}
          >
            <button onClick={() => onSelect(doc.id)} className="flex min-w-0 flex-1 items-center gap-2 text-left">
              <FileText className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm">{doc.title || "Untitled"}</span>
                <span className="block text-[11px] text-muted-foreground">{formatRelativeTime(doc.updated_at)}</span>
              </span>
            </button>
            <div className="flex shrink-0 items-center gap-0.5 opacity-0 group-hover:opacity-100">
              <Button
                variant="ghost"
                size="icon-xs"
                title={doc.pinned ? "Unpin" : "Pin"}
                onClick={() => onTogglePin(doc)}
              >
                {doc.pinned ? <PinOff className="h-3 w-3" /> : <Pin className="h-3 w-3" />}
              </Button>
              <Button variant="ghost" size="icon-xs" title="Delete" onClick={() => onDelete(doc.id)}>
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
