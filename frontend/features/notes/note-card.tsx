"use client";

import { useDraggable } from "@dnd-kit/core";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Archive, ArchiveRestore, Pin, PinOff, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Note } from "./api";
import { useNoteMutations } from "./api";
import { NOTE_COLORS } from "./note-colors";

const MIN_WIDTH = 200;
const MIN_HEIGHT = 160;

export function NoteCard({ note, dragDelta }: { note: Note; dragDelta: { x: number; y: number } | null }) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({ id: note.id });
  const { update, remove } = useNoteMutations();

  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(note.title);
  const [content, setContent] = useState(note.content);
  const [size, setSize] = useState({ width: note.width, height: note.height });
  const resizing = useRef(false);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!editing) {
      setTitle(note.title);
      setContent(note.content);
    }
  }, [note.title, note.content, editing]);

  useEffect(() => {
    setSize({ width: note.width, height: note.height });
  }, [note.width, note.height]);

  function scheduleSave(patch: Partial<Note>) {
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => {
      update.mutate({ id: note.id, input: patch });
    }, 500);
  }

  function handleResizeStart(e: React.PointerEvent) {
    e.stopPropagation();
    resizing.current = true;
    const startX = e.clientX;
    const startY = e.clientY;
    const startWidth = size.width;
    const startHeight = size.height;

    function onMove(ev: PointerEvent) {
      const width = Math.max(MIN_WIDTH, startWidth + (ev.clientX - startX));
      const height = Math.max(MIN_HEIGHT, startHeight + (ev.clientY - startY));
      setSize({ width, height });
    }
    function onUp() {
      resizing.current = false;
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      setSize((current) => {
        update.mutate({ id: note.id, input: { width: current.width, height: current.height } });
        return current;
      });
    }
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
  }

  const left = note.pos_x + (isDragging && dragDelta ? dragDelta.x : 0);
  const top = note.pos_y + (isDragging && dragDelta ? dragDelta.y : 0);

  return (
    <div
      ref={setNodeRef}
      style={{
        left,
        top,
        width: size.width,
        height: size.height,
        backgroundColor: note.color,
        zIndex: isDragging ? 50 : note.z_index,
      }}
      className={cn(
        "absolute flex flex-col overflow-hidden rounded-lg text-neutral-900 shadow-md ring-1 ring-black/5 transition-shadow",
        isDragging && "shadow-xl",
      )}
    >
      <div
        {...listeners}
        {...attributes}
        className="flex cursor-grab items-center justify-between gap-1 px-2.5 py-1.5 active:cursor-grabbing"
      >
        <input
          value={title}
          onChange={(e) => {
            setTitle(e.target.value);
            scheduleSave({ title: e.target.value });
          }}
          placeholder="Untitled"
          className="min-w-0 flex-1 truncate bg-transparent text-sm font-medium outline-none placeholder:text-neutral-900/40"
        />
        <div className="flex shrink-0 items-center gap-0.5">
          <IconAction
            label={note.pinned ? "Unpin" : "Pin"}
            onClick={() => update.mutate({ id: note.id, input: { pinned: !note.pinned } })}
          >
            {note.pinned ? <PinOff className="h-3 w-3" /> : <Pin className="h-3 w-3" />}
          </IconAction>
          <IconAction
            label={note.archived ? "Restore" : "Archive"}
            onClick={() => update.mutate({ id: note.id, input: { archived: !note.archived } })}
          >
            {note.archived ? <ArchiveRestore className="h-3 w-3" /> : <Archive className="h-3 w-3" />}
          </IconAction>
          <IconAction label="Delete" onClick={() => remove.mutate(note.id)}>
            <Trash2 className="h-3 w-3" />
          </IconAction>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto px-2.5 pb-1.5">
        {editing ? (
          <textarea
            autoFocus
            value={content}
            onChange={(e) => {
              setContent(e.target.value);
              scheduleSave({ content: e.target.value });
            }}
            onBlur={() => setEditing(false)}
            className="h-full w-full resize-none bg-transparent text-sm outline-none"
            placeholder="Write in markdown…"
          />
        ) : (
          <div onClick={() => setEditing(true)} className="prose prose-sm h-full max-w-none cursor-text text-sm">
            {content ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
            ) : (
              <span className="text-neutral-900/40">Click to write…</span>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center justify-between px-2.5 pb-1.5">
        <div className="flex gap-1">
          {NOTE_COLORS.map((c) => (
            <button
              key={c}
              onClick={() => update.mutate({ id: note.id, input: { color: c } })}
              className={cn(
                "h-3 w-3 rounded-full ring-1 ring-black/10",
                note.color === c && "ring-2 ring-black/40",
              )}
              style={{ backgroundColor: c }}
            />
          ))}
        </div>
        <div
          onPointerDown={handleResizeStart}
          className="h-3 w-3 cursor-nwse-resize rounded-tl border-t border-l border-neutral-900/20"
        />
      </div>
    </div>
  );
}

function IconAction({ label, onClick, children }: { label: string; onClick: () => void; children: React.ReactNode }) {
  return (
    <Button
      variant="ghost"
      size="icon-xs"
      title={label}
      onClick={onClick}
      className="text-neutral-900/60 hover:bg-black/10 hover:text-neutral-900"
    >
      {children}
    </Button>
  );
}
