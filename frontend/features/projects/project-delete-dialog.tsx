"use client";

import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Project } from "./api";
import { useProjectMutations } from "./api";

export function ProjectDeleteDialog({
  project,
  open,
  onOpenChange,
  onDeleted,
}: {
  project: Project | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDeleted?: () => void;
}) {
  const { remove } = useProjectMutations();

  async function handleDelete() {
    if (!project) return;
    try {
      await remove.mutateAsync(project.id);
      onOpenChange(false);
      onDeleted?.();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete project");
    }
  }

  const itemCount = project ? project.secret_count + project.note_count + project.document_count : 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Delete &quot;{project?.name}&quot;?</DialogTitle>
          <DialogDescription>
            {itemCount > 0
              ? `This project has ${itemCount} item${itemCount === 1 ? "" : "s"} (secrets, notes, documents). ` +
                "They will not be deleted — only unassigned from this project. This action cannot be undone."
              : "This action cannot be undone."}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={handleDelete} disabled={remove.isPending}>
            {remove.isPending ? "Deleting…" : "Delete project"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
