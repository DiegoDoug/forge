"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { Archive, ArchiveRestore, FileText, FolderKanban, KeyRound, Pencil, StickyNote, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { DataList, DataListRow } from "@/components/data-list";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/error-state";
import { PageHeader } from "@/components/page-header";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useDocuments } from "@/features/documents/api";
import { useNotes } from "@/features/notes/api";
import { useSecrets } from "@/features/secrets/api";
import { useProject, useProjectMutations } from "@/features/projects/api";
import { ProjectAiConfig } from "@/features/projects/project-ai-config";
import { ProjectAiQuickRun } from "@/features/projects/project-ai-quick-run";
import { ProjectDeleteDialog } from "@/features/projects/project-delete-dialog";
import { ProjectFormDialog } from "@/features/projects/project-form-dialog";

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const projectId = params.id;

  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const { update } = useProjectMutations();

  const projectQuery = useProject(projectId);
  const secretsQuery = useSecrets({ project_id: projectId });
  const notesQuery = useNotes(false, projectId);
  const documentsQuery = useDocuments(projectId);

  if (projectQuery.isLoading) {
    return (
      <div className="flex flex-col gap-4 p-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (projectQuery.isError || !projectQuery.data) {
    return (
      <div className="flex flex-1 items-center justify-center p-6">
        <EmptyState
          icon={FolderKanban}
          title="Project not found"
          description="It may have been deleted."
          action={
            <Button size="sm" nativeButton={false} render={<Link href="/projects" />}>
              Back to projects
            </Button>
          }
        />
      </div>
    );
  }

  const project = projectQuery.data;

  async function toggleArchived() {
    try {
      await update.mutateAsync({ id: project.id, input: { archived: !project.archived } });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to update project");
    }
  }

  return (
    <div className="flex flex-col">
      <PageHeader
        title={project.name}
        description={project.description || undefined}
        breadcrumb={
          <>
            <Link href="/projects" className="hover:text-foreground hover:underline">
              Projects
            </Link>
            <span aria-hidden="true">/</span>
            <span className="text-foreground">{project.name}</span>
          </>
        }
        actions={
          <>
            <Button variant="outline" size="sm" onClick={() => setEditOpen(true)}>
              <Pencil className="h-4 w-4" />
              Edit
            </Button>
            <Button variant="outline" size="sm" onClick={toggleArchived}>
              {project.archived ? <ArchiveRestore className="h-4 w-4" /> : <Archive className="h-4 w-4" />}
              {project.archived ? "Unarchive" : "Archive"}
            </Button>
            <Separator orientation="vertical" className="h-5" />
            <Button variant="outline" size="sm" className="text-destructive" onClick={() => setDeleteOpen(true)}>
              <Trash2 className="h-4 w-4" />
              Delete
            </Button>
          </>
        }
      />

      <div className="grid grid-cols-1 gap-6 p-4 md:p-6 lg:grid-cols-[1fr_20rem]">
        <div className="flex flex-col gap-4">
          <ScopedList
            title="Secrets"
            icon={KeyRound}
            href={`/secrets?project_id=${project.id}`}
            isLoading={secretsQuery.isLoading}
            isError={secretsQuery.isError}
            onRetry={() => secretsQuery.refetch()}
            items={(secretsQuery.data ?? []).map((s) => ({ id: s.id, label: s.name }))}
            emptyLabel="No secrets in this project yet."
          />
          <ScopedList
            title="Notes"
            icon={StickyNote}
            href={`/notes?project_id=${project.id}`}
            isLoading={notesQuery.isLoading}
            isError={notesQuery.isError}
            onRetry={() => notesQuery.refetch()}
            items={(notesQuery.data ?? []).map((n) => ({ id: n.id, label: n.title || "Untitled" }))}
            emptyLabel="No notes in this project yet."
          />
          <ScopedList
            title="Documents"
            icon={FileText}
            href={`/documents?project_id=${project.id}`}
            isLoading={documentsQuery.isLoading}
            isError={documentsQuery.isError}
            onRetry={() => documentsQuery.refetch()}
            items={(documentsQuery.data ?? []).map((d) => ({ id: d.id, label: d.title || "Untitled" }))}
            emptyLabel="No documents in this project yet."
          />
        </div>

        <div className="flex flex-col gap-4">
          <ProjectAiConfig project={project} />
          <ProjectAiQuickRun project={project} />
        </div>
      </div>

      <ProjectFormDialog open={editOpen} onOpenChange={setEditOpen} project={project} />
      <ProjectDeleteDialog
        project={project}
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        onDeleted={() => router.push("/projects")}
      />
    </div>
  );
}

function ScopedList({
  title,
  icon: Icon,
  href,
  isLoading,
  isError,
  onRetry,
  items,
  emptyLabel,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  isLoading: boolean;
  isError?: boolean;
  onRetry?: () => void;
  items: { id: string; label: string }[];
  emptyLabel: string;
}) {
  return (
    <div className="rounded-xl border border-border">
      <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
        <span className="flex items-center gap-2 text-sm font-medium">
          <Icon className="h-4 w-4 text-muted-foreground" />
          {title}
          <span className="text-xs font-normal text-muted-foreground">({items.length})</span>
        </span>
        <Link href={href} className="text-xs text-muted-foreground underline underline-offset-2">
          View all
        </Link>
      </div>
      {isLoading ? (
        <div className="p-3">
          <Skeleton className="h-6 w-full" />
        </div>
      ) : isError ? (
        <div className="p-3">
          <ErrorState description={`Couldn't load ${title.toLowerCase()}.`} onRetry={onRetry} />
        </div>
      ) : items.length === 0 ? (
        <p className="px-4 py-6 text-center text-xs text-muted-foreground">{emptyLabel}</p>
      ) : (
        <DataList className="rounded-none border-none">
          {items.slice(0, 6).map((item) => (
            <DataListRow key={item.id}>
              <span className="data-primary truncate">{item.label}</span>
            </DataListRow>
          ))}
        </DataList>
      )}
    </div>
  );
}
