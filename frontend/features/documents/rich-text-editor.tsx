"use client";

import { useEffect, useRef } from "react";

import { RichTextToolbar } from "./rich-text-toolbar";

export function RichTextEditor({
  documentId,
  html,
  title,
  onChange,
  placeholder = "Start writing…",
}: {
  documentId: string;
  html: string;
  title: string;
  onChange: (html: string) => void;
  placeholder?: string;
}) {
  const editorRef = useRef<HTMLDivElement>(null);
  const lastDocId = useRef<string | null>(null);

  // Sync DOM from the `html` prop when switching documents, or when it
  // changes for the current document while the editor isn't focused (e.g.
  // the document finished loading asynchronously after this component
  // mounted). Skip while focused so a live keystroke's own onChange→prop
  // round-trip doesn't reset the caret to the start on every render.
  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) return;
    const switchedDoc = lastDocId.current !== documentId;
    if (!switchedDoc && document.activeElement === editor) return;
    if (!switchedDoc && editor.innerHTML === html) return;
    editor.innerHTML = html;
    lastDocId.current = documentId;
  }, [documentId, html]);

  useEffect(() => {
    document.execCommand("defaultParagraphSeparator", false, "p");
  }, []);

  function emitChange() {
    if (editorRef.current) onChange(editorRef.current.innerHTML);
  }

  function handlePrint() {
    const editor = editorRef.current;
    if (!editor) return;
    const printWindow = window.open("", "_blank", "noopener,noreferrer,width=900,height=1200");
    if (!printWindow) return;
    printWindow.document.write(
      `<!doctype html><html><head><title>${escapeHtml(title || "Untitled")}</title>` +
        `<meta charset="utf-8" />` +
        `<style>
          body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.5; color: #111; }
          h1, h2, h3 { line-height: 1.25; }
        </style></head><body>` +
        `<h1>${escapeHtml(title || "Untitled")}</h1>${editor.innerHTML}` +
        `</body></html>`,
    );
    printWindow.document.close();
    printWindow.focus();
    printWindow.onload = () => {
      printWindow.print();
    };
  }

  return (
    <div className="flex h-full flex-col">
      <RichTextToolbar editorRef={editorRef} onCommand={emitChange} onPrint={handlePrint} />
      <div className="min-h-0 flex-1 overflow-y-auto">
        <div
          ref={editorRef}
          contentEditable
          suppressContentEditableWarning
          onInput={emitChange}
          onBlur={emitChange}
          data-placeholder={placeholder}
          className="forge-document-editor prose prose-sm mx-auto min-h-full max-w-3xl px-10 py-8 text-sm outline-none empty:before:pointer-events-none empty:before:text-muted-foreground empty:before:content-[attr(data-placeholder)]"
        />
      </div>
    </div>
  );
}

function escapeHtml(text: string): string {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
