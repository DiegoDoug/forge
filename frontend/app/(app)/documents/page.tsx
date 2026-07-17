"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { FileText, Pin, PinOff, Trash2 } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useDocument, useDocumentMutations, useDocumentSearch, useDocuments } from "@/features/documents/api";
import { DocumentSidebar } from "@/features/documents/document-sidebar";
import { DownloadMenu } from "@/features/documents/download-menu";
import { RichTextEditor } from "@/features/documents/rich-text-editor";

export default function DocumentsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const selectedId = searchParams.get("open");

  const [query, setQuery] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const loadedFor = useRef<string | null>(null);

  const listQuery = useDocuments();
  const searchQuery = useDocumentSearch(query);
  const documentQuery = useDocument(selectedId);
  const { create, update, remove } = useDocumentMutations();

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
    const created = await create.mutateAsync({ title: "", content: "" });
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
              <Button variant="ghost" size="icon-sm" title={doc.pinned ? "Unpin" : "Pin"} onClick={handleTogglePin}>
                {doc.pinned ? <PinOff className="h-4 w-4" /> : <Pin className="h-4 w-4" />}
              </Button>
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
