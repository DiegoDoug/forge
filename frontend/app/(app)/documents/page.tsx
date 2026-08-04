"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { FileText, Pin, PinOff, Tags, Trash2 } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useDocument, useDocumentMutations, useDocumentSearch, useDocuments } from "@/features/documents/api";
import { DocumentSidebar } from "@/features/documents/document-sidebar";
import { DownloadMenu } from "@/features/documents/download-menu";
import { useKnowledgeList } from "@/features/knowledge/api";
import { KnowledgeLinkPanel } from "@/features/knowledge/knowledge-link-panel";
import { KnowledgeTagPicker } from "@/features/knowledge/knowledge-tag-picker";
import { RichTextEditor } from "@/features/documents/rich-text-editor";
import { ProjectPicker } from "@/features/projects/project-picker";

export default function DocumentsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const selectedId = searchParams.get("open");

  const [query, setQuery] = useState("");
  const [projectId, setProjectId] = useState<string | null>(() => searchParams.get("project_id"));
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const loadedFor = useRef<string | null>(null);

  const listQuery = useDocuments(projectId ?? undefined);
  const searchQuery = useDocumentSearch(query);
  const documentQuery = useDocument(selectedId);
  const { create, update, remove } = useDocumentMutations();
  // Document/DocumentOut carries no `tags` field (untouched by this phase,
  // per 03_ARCHITECTURE.md SS2's "no cross-feature import" boundary) - the
  // selected document's current tags are read from the Hub's own list
  // instead, capped to its first 100 most-recently-updated documents.
  const hubDocumentsQuery = useKnowledgeList({ type: "document" });

  const documents = query.trim() ? (searchQuery.data ?? []) : (listQuery.data ?? []);
  const doc = documentQuery.data;

  useEffect(() => {
    if (doc && loadedFor.current !== doc.id) {
      setTitle(doc.title);
      setContent(doc.content);
      loadedFor.current = doc.id;
    }
    if (!selectedId) {
      loadedFor.current = null;
      setTitle("");
      setContent("");
    }
  }, [doc, selectedId]);

  function selectDocument(id: string) {
    router.push(`/documents?open=${id}`);
  }

  async function handleNew() {
    const created = await create.mutateAsync({ title: "", content: "", project_id: projectId ?? undefined });
    router.push(`/documents?open=${created.id}`);
  }

  function scheduleSave(patch: { title?: string; content?: string }) {
    if (!selectedId) return;
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => {
      update.mutate({ id: selectedId, input: patch });
    }, 600);
  }

  function handleTitleChange(value: string) {
    setTitle(value);
    scheduleSave({ title: value });
  }

  function handleContentChange(html: string) {
    setContent(html);
    scheduleSave({ content: html });
  }

  function handleTogglePin() {
    if (!selectedId || !doc) return;
    update.mutate({ id: selectedId, input: { pinned: !doc.pinned } });
  }

  async function handleDelete(id: string) {
    await remove.mutateAsync(id);
    if (id === selectedId) router.push("/documents");
  }

  return (
    <div className="flex h-[calc(100dvh-3.5rem)]">
      <DocumentSidebar
        documents={documents}
        selectedId={selectedId}
        query={query}
        onQueryChange={setQuery}
        projectId={projectId}
        onProjectChange={setProjectId}
        onSelect={selectDocument}
        onNew={handleNew}
        onTogglePin={(d) => update.mutate({ id: d.id, input: { pinned: !d.pinned } })}
        onDelete={handleDelete}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        {selectedId && doc ? (
          <>
            <div className="flex items-center gap-2 border-b border-border px-4 py-3">
              <Input
                value={title}
                onChange={(e) => handleTitleChange(e.target.value)}
                placeholder="Untitled document"
                className="h-8 flex-1 border-none bg-transparent px-1 text-base font-semibold shadow-none focus-visible:ring-0"
              />
              <ProjectPicker
                value={doc.project_id}
                onChange={(pid) => update.mutate({ id: selectedId, input: { project_id: pid } })}
                className="h-8 w-40 shrink-0"
              />
              <Button variant="ghost" size="icon-sm" title={doc.pinned ? "Unpin" : "Pin"} onClick={handleTogglePin}>
                {doc.pinned ? <PinOff className="h-4 w-4" /> : <Pin className="h-4 w-4" />}
              </Button>
              <Popover>
                <PopoverTrigger render={<Button variant="ghost" size="icon-sm" title="Tags & linked items" />}>
                  <Tags className="h-4 w-4" />
                </PopoverTrigger>
                <PopoverContent className="w-64 space-y-3 p-3">
                  <div>
                    <p className="mb-1 text-[11px] font-medium tracking-wide text-muted-foreground uppercase">Tags</p>
                    <KnowledgeTagPicker
                      itemType="document"
                      itemId={selectedId}
                      tags={hubDocumentsQuery.data?.items.find((i) => i.id === selectedId)?.tags ?? []}
                    />
                  </div>
                  <div>
                    <p className="mb-1 text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
                      Linked items
                    </p>
                    <KnowledgeLinkPanel itemType="document" itemId={selectedId} />
                  </div>
                </PopoverContent>
              </Popover>
              <DownloadMenu documentId={selectedId} title={title} />
              <Button variant="ghost" size="icon-sm" title="Delete" onClick={() => handleDelete(selectedId)}>
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
            <div className="min-h-0 flex-1">
              <RichTextEditor documentId={selectedId} html={content} title={title} onChange={handleContentChange} />
            </div>
          </>
        ) : (
          <div className="flex flex-1 items-center justify-center p-6">
            <EmptyState
              icon={FileText}
              title="No document selected"
              description="Create a new document or pick one from the history on the left."
              action={
                <Button size="sm" onClick={handleNew}>
                  New document
                </Button>
              }
            />
          </div>
        )}
      </div>
    </div>
  );
}
