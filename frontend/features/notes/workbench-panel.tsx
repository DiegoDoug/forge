"use client";

import type { ComponentType } from "react";
import Link from "next/link";
import { StickyNote } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { registerWorkbenchPanel } from "@/features/workbench/panel-registry";
import type { WorkbenchPanelProps } from "@/features/workbench/panel-types";
import { useNotes } from "./api";

const RecentNotesPanel: ComponentType<WorkbenchPanelProps> = () => {
  const { data, isLoading, isError, refetch } = useNotes(false);

  if (isLoading) {
    return (
      <div className="flex flex-col gap-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-8 w-full" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center gap-2 py-4 text-center">
        <p className="text-xs text-muted-foreground">Couldn&apos;t load recent notes.</p>
        <Button size="xs" variant="outline" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const recentNotes = [...data].sort((a, b) => b.updated_at.localeCompare(a.updated_at)).slice(0, 6);

  if (recentNotes.length === 0) {
    return (
      <EmptyState
        icon={StickyNote}
        title="No notes yet"
        description="Create a sticky note to see it here."
        action={
          <Button size="sm" nativeButton={false} render={<Link href="/notes?new=1" />}>
            New note
          </Button>
        }
      />
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {recentNotes.map((note) => (
        <li key={note.id}>
          <Link
            href={`/notes?open=${note.id}`}
            className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm hover:bg-accent/40"
          >
            <span className="h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: note.color }} />
            <span className="truncate">{note.title || "Untitled"}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
};

registerWorkbenchPanel({
  type: "recent_notes",
  metadata: {
    title: "Recent Notes",
    description: "Your most recently updated notes.",
    icon: StickyNote,
    defaultVisible: true,
  },
  component: RecentNotesPanel,
});
