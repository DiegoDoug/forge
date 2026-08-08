"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Archive, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/page-header";
import { SearchField } from "@/components/search-field";
import { Toolbar } from "@/components/toolbar";
import { useNoteMutations, useNotes, useNoteSearch } from "@/features/notes/api";
import { NOTE_COLORS } from "@/features/notes/note-colors";
import { NotesBoard } from "@/features/notes/notes-board";
import { ProjectPicker } from "@/features/projects/project-picker";

export default function NotesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const openId = searchParams.get("open");
  const [showArchived, setShowArchived] = useState(false);
  const [query, setQuery] = useState("");
  const [projectId, setProjectId] = useState<string | null>(() => searchParams.get("project_id"));
  const { create } = useNoteMutations();

  const notesQuery = useNotes(showArchived, projectId ?? undefined);
  const searchQuery = useNoteSearch(query);

  const isSearching = query.trim().length > 0;
  const notes = isSearching ? searchQuery.data ?? [] : notesQuery.data ?? [];
  const boardIsLoading = isSearching ? searchQuery.isLoading : notesQuery.isLoading;
  const boardIsError = isSearching ? searchQuery.isError : notesQuery.isError;
  const retryBoard = () => (isSearching ? searchQuery.refetch() : notesQuery.refetch());

  function handleNewNote() {
    const color = NOTE_COLORS[Math.floor(Math.random() * NOTE_COLORS.length)].hex;
    create.mutate({
      pos_x: 40 + Math.random() * 200,
      pos_y: 40 + Math.random() * 120,
      color,
      project_id: projectId ?? undefined,
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
    <div className="flex h-full flex-col">
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

      <Toolbar>
        <SearchField value={query} onChange={setQuery} placeholder="Search notes…" className="max-w-sm flex-1" />
        <ProjectPicker value={projectId} onChange={setProjectId} className="w-48" />
      </Toolbar>

      <NotesBoard
        notes={notes}
        highlightId={openId}
        isLoading={boardIsLoading}
        isError={boardIsError}
        onRetry={retryBoard}
        isFiltered={isSearching}
      />
    </div>
  );
}
