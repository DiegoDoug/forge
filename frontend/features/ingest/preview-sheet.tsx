"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { StickyNote } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { CopyButton } from "@/components/copy-button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ingestApi } from "./api";

export function PreviewSheet({
  jobId,
  fileId,
  onClose,
}: {
  jobId: string | null;
  fileId: string | null;
  onClose: () => void;
}) {
  const [saved, setSaved] = useState(false);

  const contentQuery = useQuery({
    queryKey: ["ingest", "content", jobId, fileId],
    queryFn: () => ingestApi.getFileContent(jobId as string, fileId as string),
    enabled: Boolean(jobId && fileId),
  });

  const saveToNotes = useMutation({
    mutationFn: () => ingestApi.saveToNotes(jobId as string, fileId as string),
    onSuccess: () => {
      setSaved(true);
      toast.success("Saved to Notes");
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed to save"),
  });

  return (
    <Sheet open={Boolean(jobId && fileId)} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="right" className="w-full sm:max-w-2xl">
        <SheetHeader>
          <div className="flex items-center justify-between gap-2">
            <SheetTitle className="truncate">{contentQuery.data?.name ?? "Preview"}</SheetTitle>
            <div className="flex shrink-0 gap-1.5">
              {contentQuery.data ? <CopyButton value={contentQuery.data.markdown} label="Markdown copied" size="icon" /> : null}
              <Button
                variant="outline"
                size="sm"
                onClick={() => saveToNotes.mutate()}
                disabled={saveToNotes.isPending || saved}
              >
                <StickyNote className="h-3.5 w-3.5" />
                {saved ? "Saved" : "Save to Notes"}
              </Button>
            </div>
          </div>
        </SheetHeader>

        <Tabs defaultValue="preview" className="flex min-h-0 flex-1 flex-col px-4">
          <TabsList className="w-fit">
            <TabsTrigger value="preview">Preview</TabsTrigger>
            <TabsTrigger value="raw">Raw Markdown</TabsTrigger>
          </TabsList>
          <TabsContent value="preview" className="min-h-0 flex-1">
            <ScrollArea className="h-full">
              <div className="prose prose-sm max-w-none pb-6 dark:prose-invert">
                {contentQuery.data ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{contentQuery.data.markdown}</ReactMarkdown>
                ) : null}
              </div>
            </ScrollArea>
          </TabsContent>
          <TabsContent value="raw" className="min-h-0 flex-1">
            <ScrollArea className="h-full">
              <pre className="pb-6 font-mono text-xs whitespace-pre-wrap">{contentQuery.data?.markdown}</pre>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </SheetContent>
    </Sheet>
  );
}
