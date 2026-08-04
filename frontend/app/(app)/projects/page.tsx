"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Archive, FolderKanban, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import { ProjectCard } from "@/features/projects/project-card";
import { ProjectFormDialog } from "@/features/projects/project-form-dialog";
import { useProjects } from "@/features/projects/api";

export default function ProjectsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [showArchived, setShowArchived] = useState(false);
  const [formOpen, setFormOpen] = useState(false);

  const projectsQuery = useProjects(showArchived);

  const consumedNewParam = useRef(false);
  useEffect(() => {
    if (searchParams.get("new") && !consumedNewParam.current) {
      consumedNewParam.current = true;
      setFormOpen(true);
      router.replace("/projects");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  return (
    <div className="flex flex-col">
      <PageHeader
        title="Projects"
        description="Group secrets, notes, and documents into per-project workspaces"
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
            <Button size="sm" onClick={() => setFormOpen(true)}>
              <Plus className="h-4 w-4" />
              New project
            </Button>
          </>
        }
      />

      <div className="p-4 md:p-6">
        {projectsQuery.isLoading ? (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        ) : projectsQuery.isError ? (
          <div className="flex flex-col items-center gap-2 py-16 text-center">
            <p className="text-sm text-muted-foreground">Couldn&apos;t load projects.</p>
            <Button size="sm" variant="outline" onClick={() => projectsQuery.refetch()}>
              Retry
            </Button>
          </div>
        ) : (projectsQuery.data?.length ?? 0) === 0 ? (
          <EmptyState
            icon={FolderKanban}
            title={showArchived ? "No archived projects" : "No projects yet"}
            description={
              showArchived
                ? "Projects you archive will show up here."
                : "Create a project to start grouping secrets, notes, and documents."
            }
            action={
              showArchived ? undefined : (
                <Button size="sm" onClick={() => setFormOpen(true)}>
                  New project
                </Button>
              )
            }
          />
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {projectsQuery.data!.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </div>

      <ProjectFormDialog open={formOpen} onOpenChange={setFormOpen} onSaved={(id) => router.push(`/projects/${id}`)} />
    </div>
  );
}
