"use client";

import { FileText, Pin, PinOff, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/error-state";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SearchField } from "@/components/search-field";
import { Skeleton } from "@/components/ui/skeleton";
import { ProjectPicker } from "@/features/projects/project-picker";
import { formatRelativeTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { DocumentSummary } from "./api";

export function DocumentSidebar({
  documents,
  isLoading,
  isError,
  onRetry,
  selectedId,
  query,
  onQueryChange,
  projectId,
  onProjectChange,
  onSelect,
  onNew,
  onTogglePin,
  onDelete,
}: {
  documents: DocumentSummary[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  selectedId: string | null;
  query: string;
  onQueryChange: (q: string) => void;
  projectId: string | null;
  onProjectChange: (id: string | null) => void;
  onSelect: (id: string) => void;
  onNew: () => void;
  onTogglePin: (doc: DocumentSummary) => void;
  onDelete: (doc: DocumentSummary) => void;
}) {
  const pinned = documents.filter((d) => d.pinned);
  const others = documents.filter((d) => !d.pinned);

  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      <div className="flex flex-col gap-2 border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <SearchField value={query} onChange={onQueryChange} placeholder="Search documents…" className="flex-1" />
          <Button size="icon-sm" title="New document" onClick={onNew}>
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        <ProjectPicker value={projectId} onChange={onProjectChange} className="w-full" />
      </div>

      {isLoading ? (
        <div className="flex flex-col gap-2 p-1">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState description="Couldn't load your documents." onRetry={onRetry} />
      ) : (
        <ScrollArea className="min-h-0 flex-1">
          <div className="flex flex-col gap-3 p-1">
            {documents.length === 0 ? (
              <p className="px-2 py-6 text-center text-xs text-muted-foreground">
                {query.trim() ? "No documents match your search." : "No documents yet."}
              </p>
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
      )}
    </div>
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
  onDelete: (doc: DocumentSummary) => void;
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
              <Button variant="ghost" size="icon-xs" title="Delete" onClick={() => onDelete(doc)}>
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
