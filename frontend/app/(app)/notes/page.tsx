"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Archive, Plus, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/page-header";
import { useNoteMutations, useNotes, useNoteSearch } from "@/features/notes/api";
import { NOTE_COLORS } from "@/features/notes/note-colors";
import { NotesBoard } from "@/features/notes/notes-board";

export default function NotesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [showArchived, setShowArchived] = useState(false);
  const [query, setQuery] = useState("");
  const { create } = useNoteMutations();

  const notesQuery = useNotes(showArchived);
  const searchQuery = useNoteSearch(query);

  const notes = query.trim() ? searchQuery.data ?? [] : notesQuery.data ?? [];

  function handleNewNote() {
    const color = NOTE_COLORS[Math.floor(Math.random() * NOTE_COLORS.length)];
    create.mutate({
      pos_x: 40 + Math.random() * 200,
      pos_y: 40 + Math.random() * 120,
      color,
    });
  }

  // Deep-link from the Workbench Quick Actions panel (?new=1): start the
  // note-creation flow immediately, then drop the param so it doesn't
  // re-trigger on refresh/back-navigation.
  const consumedNewParam = useRef(false);
  useEffect(() => {
    if (searchParams.get("new") && !consumedNewParam.current) {
      consumedNewParam.current = true;
      handleNewNote();
      router.replace("/notes");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  return (
    <div>
      <PageHeader
        title="Notes"
        description="An infinite sticky note board — drag, resize, and write in Markdown"
        actions={
          <>
            <Button
              variant={showArchived ? "secondary" : "outline"}
              size="sm"
              onClick={() => setShowArchived((s) => !s)}
            >
              <Archive className="h-4 w-4" />
              {showArchived ? "Viewing archived" : "Archived"}
            </Button>
            <Button size="sm" onClick={handleNewNote}>
              <Plus className="h-4 w-4" />
              New note
            </Button>
          </>
        }
      />

      <div className="border-b border-border p-3">
        <div className="relative max-w-sm">
          <Search className="pointer-events-none absolute top-1/2 left-2.5 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search notes…" className="pl-8" />
        </div>
      </div>

      <NotesBoard notes={notes} />
    </div>
  );
}
