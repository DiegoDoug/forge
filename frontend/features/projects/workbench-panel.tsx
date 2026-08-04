"use client";

import type { ComponentType } from "react";
import Link from "next/link";
import { FolderKanban } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { registerWorkbenchPanel } from "@/features/workbench/panel-registry";
import type { WorkbenchPanelProps } from "@/features/workbench/panel-types";
import { useProjects } from "./api";

const RecentProjectsPanel: ComponentType<WorkbenchPanelProps> = () => {
  const { data, isLoading, isError, refetch } = useProjects(false);

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
        <p className="text-xs text-muted-foreground">Couldn&apos;t load recent projects.</p>
        <Button size="xs" variant="outline" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const recentProjects = [...data].sort((a, b) => b.updated_at.localeCompare(a.updated_at)).slice(0, 6);

  if (recentProjects.length === 0) {
    return (
      <EmptyState
        icon={FolderKanban}
        title="No projects yet"
        description="Create a project to group secrets, notes, and documents."
        action={
          <Button size="sm" nativeButton={false} render={<Link href="/projects?new=1" />}>
            New project
          </Button>
        }
      />
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {recentProjects.map((project) => (
        <li key={project.id}>
          <Link
            href={`/projects/${project.id}`}
            className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm hover:bg-accent/40"
          >
            <span className="h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: project.color }} />
            <span className="truncate">{project.name}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
};

registerWorkbenchPanel({
  type: "recent_projects",
  metadata: {
    title: "Recent Projects",
    description: "Your most recently updated projects.",
    icon: FolderKanban,
    defaultVisible: true,
  },
  component: RecentProjectsPanel,
});
