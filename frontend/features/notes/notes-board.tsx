"use client";

import { DndContext, type DragEndEvent, type DragMoveEvent } from "@dnd-kit/core";
import { useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { StickyNote } from "lucide-react";
import type { Note } from "./api";
import { useNoteMutations } from "./api";
import { NoteCard } from "./note-card";

export function NotesBoard({ notes }: { notes: Note[] }) {
  const { update } = useNoteMutations();
  const [dragging, setDragging] = useState<{ id: string; delta: { x: number; y: number } } | null>(null);

  function handleDragMove(event: DragMoveEvent) {
    setDragging({ id: String(event.active.id), delta: event.delta });
  }

  function handleDragEnd(event: DragEndEvent) {
    const note = notes.find((n) => n.id === event.active.id);
    setDragging(null);
    if (!note) return;
    update.mutate({
      id: note.id,
      input: {
        pos_x: Math.round(note.pos_x + event.delta.x),
        pos_y: Math.round(note.pos_y + event.delta.y),
      },
    });
  }

  if (notes.length === 0) {
    return (
      <div className="p-6">
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

  return (
    <DndContext onDragMove={handleDragMove} onDragEnd={handleDragEnd}>
      <div className="relative overflow-auto" style={{ height: "calc(100dvh - 7.5rem)" }}>
        <div className="relative" style={{ width: maxX + 400, height: maxY + 400 }}>
          {notes.map((note) => (
            <NoteCard
              key={note.id}
              note={note}
              dragDelta={dragging?.id === note.id ? dragging.delta : null}
            />
          ))}
        </div>
      </div>
    </DndContext>
  );
}
