"use client";

import { useState } from "react";
import { Folder as FolderIcon, Plus, Tag as TagIcon, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useFolders, useTags, useVaultMutations } from "./api";

export function VaultFilters({
  folderId,
  tagId,
  onFolderChange,
  onTagChange,
}: {
  folderId: string | null;
  tagId: string | null;
  onFolderChange: (id: string | null) => void;
  onTagChange: (id: string | null) => void;
}) {
  const foldersQuery = useFolders();
  const tagsQuery = useTags();
  const { createFolder, deleteFolder, createTag, deleteTag } = useVaultMutations();

  const [newFolder, setNewFolder] = useState("");
  const [newTag, setNewTag] = useState("");

  async function addFolder() {
    if (!newFolder.trim()) return;
    try {
      await createFolder.mutateAsync({ name: newFolder.trim() });
      setNewFolder("");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create folder");
    }
  }

  async function addTag() {
    if (!newTag.trim()) return;
    try {
      await createTag.mutateAsync({ name: newTag.trim() });
      setNewTag("");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create tag");
    }
  }

  return (
    <div className="flex w-56 shrink-0 flex-col gap-6 border-r border-border p-4">
      <div>
        <button
          onClick={() => onFolderChange(null)}
          className={cn(
            "w-full rounded-lg px-2 py-1.5 text-left text-sm",
            !folderId ? "bg-accent font-medium text-accent-foreground" : "text-muted-foreground hover:bg-accent/50",
          )}
        >
          All secrets
        </button>
      </div>

      <div>
        <div className="mb-1.5 flex items-center justify-between px-2">
          <span className="text-xs font-medium text-muted-foreground">Folders</span>
        </div>
        <div className="flex flex-col gap-0.5">
          {foldersQuery.data?.map((folder) => (
            <div key={folder.id} className="group flex items-center">
              <button
                onClick={() => onFolderChange(folder.id)}
                className={cn(
                  "flex flex-1 items-center gap-2 truncate rounded-lg px-2 py-1.5 text-left text-sm",
                  folderId === folder.id
                    ? "bg-accent font-medium text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent/50",
                )}
              >
                <FolderIcon className="h-3.5 w-3.5 shrink-0" />
                <span className="truncate">{folder.name}</span>
              </button>
              <Button
                variant="ghost"
                size="icon-xs"
                className="shrink-0 opacity-0 group-hover:opacity-100"
                onClick={() => deleteFolder.mutate(folder.id)}
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
        <div className="mt-1 flex items-center gap-1 px-1">
          <Input
            value={newFolder}
            onChange={(e) => setNewFolder(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addFolder()}
            placeholder="New folder"
            className="h-7 text-xs"
          />
          <Button variant="ghost" size="icon-sm" onClick={addFolder}>
            <Plus className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      <div>
        <div className="mb-1.5 flex items-center justify-between px-2">
          <span className="text-xs font-medium text-muted-foreground">Tags</span>
        </div>
        <div className="flex flex-col gap-0.5">
          {tagsQuery.data?.map((tag) => (
            <div key={tag.id} className="group flex items-center">
              <button
                onClick={() => onTagChange(tag.id)}
                className={cn(
                  "flex flex-1 items-center gap-2 truncate rounded-lg px-2 py-1.5 text-left text-sm",
                  tagId === tag.id
                    ? "bg-accent font-medium text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent/50",
                )}
              >
                <TagIcon className="h-3.5 w-3.5 shrink-0" style={{ color: tag.color }} />
                <span className="truncate">{tag.name}</span>
              </button>
              <Button
                variant="ghost"
                size="icon-xs"
                className="shrink-0 opacity-0 group-hover:opacity-100"
                onClick={() => deleteTag.mutate(tag.id)}
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
        <div className="mt-1 flex items-center gap-1 px-1">
          <Input
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addTag()}
            placeholder="New tag"
            className="h-7 text-xs"
          />
          <Button variant="ghost" size="icon-sm" onClick={addTag}>
            <Plus className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
