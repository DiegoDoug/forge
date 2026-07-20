"use client";

import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { downloadDocumentExport, EXPORT_FORMATS, type ExportFormat } from "./api";

const FORMAT_LABELS: Record<ExportFormat, string> = {
  txt: "Plain text (.txt)",
  md: "Markdown (.md)",
  doc: "Word 97-2003 (.doc)",
  docx: "Word (.docx)",
  pdf: "PDF (.pdf)",
  xml: "XML (.xml)",
};

export function DownloadMenu({ documentId, title }: { documentId: string | null; title: string }) {
  const [pending, setPending] = useState<ExportFormat | null>(null);

  async function handleDownload(format: ExportFormat) {
    if (!documentId) return;
    setPending(format);
    try {
      await downloadDocumentExport(documentId, format, title || "Untitled");
    } catch {
      toast.error(`Couldn't export as ${format.toUpperCase()}`);
    } finally {
      setPending(null);
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <Button size="sm" variant="outline" disabled={!documentId}>
            {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
            Download
          </Button>
        }
      />
      <DropdownMenuContent align="end">
        {EXPORT_FORMATS.map((format) => (
          <DropdownMenuItem key={format} onClick={() => handleDownload(format)} disabled={pending !== null}>
            {FORMAT_LABELS[format]}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
