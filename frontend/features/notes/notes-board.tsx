"use client";

import { DndContext, type DragEndEvent } from "@dnd-kit/core";
import { useEffect, useRef, useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/error-state";
import { Skeleton } from "@/components/ui/skeleton";
import { SearchX, StickyNote } from "lucide-react";
import type { Note } from "./api";
import { useNoteMutations } from "./api";
import { NoteCard } from "./note-card";

const HIGHLIGHT_DURATION_MS = 2000;

export function NotesBoard({
  notes,
  highlightId,
  isLoading,
  isError,
  onRetry,
  matchIds,
}: {
  notes: Note[];
  highlightId?: string | null;
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
  // When set, the board is under a text-search filter: notes NOT in this
  // set render dimmed rather than being removed, so canvas position keeps
  // meaning results as "where I put things," not a swapped-in result list.
  matchIds?: Set<string> | null;
}) {
  const { update } = useNoteMutations();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [activeHighlight, setActiveHighlight] = useState<string | null>(null);
  const consumedHighlight = useRef<string | null>(null);

  // Deep-link from the command palette, /search, and Knowledge Hub
  // (?open={id}): scroll the target note into view and briefly ring-highlight
  // it, since the board is a free-positioned canvas with no per-note route
  // to land on otherwise (see CURRENT_STATE.md Known Issue #15).
  //
  // Split into two effects deliberately: this one's ref-guard makes the
  // scroll-and-arm step run exactly once per id, which is correct, but under
  // React Strict Mode's mount->cleanup->mount double-invocation, a *single*
  // effect combining that guard with the expiry timer clears the first
  // timer on the synthetic remount and then - because the guard is already
  // tripped - never re-arms it, so the highlight would never turn off. The
  // expiry timer below has no such guard, so its own cleanup+rerun nets out
  // to exactly one live timer regardless of how many times it's invoked.
  useEffect(() => {
    if (!highlightId || consumedHighlight.current === highlightId) return;
    const note = notes.find((n) => n.id === highlightId);
    if (!note || !scrollRef.current) return;
    consumedHighlight.current = highlightId;

    scrollRef.current.scrollTo({
      left: Math.max(0, note.pos_x + note.width / 2 - scrollRef.current.clientWidth / 2),
      top: Math.max(0, note.pos_y + note.height / 2 - scrollRef.current.clientHeight / 2),
      behavior: "smooth",
    });
    setActiveHighlight(highlightId);
  }, [highlightId, notes]);

  useEffect(() => {
    if (!activeHighlight) return;
    const timer = setTimeout(() => setActiveHighlight(null), HIGHLIGHT_DURATION_MS);
    return () => clearTimeout(timer);
  }, [activeHighlight]);

  function handleDragEnd(event: DragEndEvent) {
    const note = notes.find((n) => n.id === event.active.id);
    if (!note) return;
    update.mutate({
      id: note.id,
      input: {
        pos_x: Math.round(note.pos_x + event.delta.x),
        pos_y: Math.round(note.pos_y + event.delta.y),
      },
    });
  }

  if (isLoading) {
    return (
      <div className="flex flex-1 min-h-0 items-center justify-center p-6">
        <div className="grid w-full max-w-2xl grid-cols-2 gap-4 sm:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-40 w-full rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-1 min-h-0 items-center justify-center p-6">
        <ErrorState description="Couldn't load your notes." onRetry={onRetry} />
      </div>
    );
  }

  if (notes.length === 0) {
    return (
      <div className="flex flex-1 min-h-0 items-center justify-center p-6">
        <EmptyState
          icon={StickyNote}
          title="No notes yet"
          description="Create a sticky note and drag it anywhere on the board."
        />
      </div>
    );
  }

  const maxX = Math.max(...notes.map((n) => n.pos_x + n.width), 1200);
  const maxY = Math.max(...notes.map((n) => n.pos_y + n.height), 800);
  const isSearching = matchIds != null;
  // Compare against the notes actually on this board, not the raw match
  // count — search ignores the archived/project scope notesQuery applies,
  // so a match can exist outside what's currently rendered here.
  const noMatches = isSearching && !notes.some((n) => matchIds!.has(n.id));

  return (
    <DndContext onDragEnd={handleDragEnd}>
      <div ref={scrollRef} className="relative flex-1 min-h-0 overflow-auto">
        {noMatches ? (
          <div className="pointer-events-none sticky top-3 left-3 z-10 inline-flex items-center gap-1.5 rounded-md border border-border bg-popover px-2.5 py-1 text-xs text-muted-foreground shadow-sm">
            <SearchX className="h-3.5 w-3.5" aria-hidden="true" />
            No notes match your search — showing all notes dimmed.
          </div>
        ) : null}
        <div className="relative" style={{ width: maxX + 400, height: maxY + 400 }}>
          {notes.map((note) => (
            <NoteCard
              key={note.id}
              note={note}
              highlighted={note.id === activeHighlight}
              dimmed={isSearching && !matchIds!.has(note.id)}
            />
          ))}
        </div>
      </div>
    </DndContext>
  );
}
