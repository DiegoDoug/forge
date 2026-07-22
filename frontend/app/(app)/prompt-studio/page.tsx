"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { MessageSquareText } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import { usePrompt, usePromptStudioMutations, usePrompts } from "@/features/prompt-studio/api";
import { PromptEditor } from "@/features/prompt-studio/prompt-editor";
import { PromptSidebar } from "@/features/prompt-studio/prompt-sidebar";
import { cn } from "@/lib/utils";

export default function PromptStudioPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const selectedId = searchParams.get("open");

  const [query, setQuery] = useState("");
  const [activeTag, setActiveTag] = useState<string | null>(null);

  const listQuery = usePrompts(query || undefined, activeTag || undefined);
  const promptQuery = usePrompt(selectedId);
  const { create } = usePromptStudioMutations();

  function selectPrompt(id: string) {
    router.push(`/prompt-studio?open=${id}`);
  }

  async function handleNew() {
    try {
      // body must be non-empty (schemas/prompt_studio.py PromptCreate.body has
      // min_length=1) - a single space is the least presumptuous non-empty
      // default; the user immediately overwrites it in the body editor.
      const created = await create.mutateAsync({ name: "Untitled prompt", body: " " });
      router.push(`/prompt-studio?open=${created.id}`);
    } catch {
      toast.error("Couldn't create a new prompt.");
    }
  }

  // Below the lg breakpoint (1024px, per 02_UI.md §4), the list and editor
  // never share the viewport - whichever one is relevant is shown full-width,
  // with a back affordance in PromptEditor to return to the list.
  return (
    <div className="flex h-[calc(100dvh-3.5rem)]">
      <PromptSidebar
        prompts={listQuery.data?.items ?? []}
        isLoading={listQuery.isLoading}
        isError={listQuery.isError}
        selectedId={selectedId}
        query={query}
        onQueryChange={setQuery}
        activeTag={activeTag}
        onTagChange={setActiveTag}
        onSelect={selectPrompt}
        onNew={handleNew}
        className={cn(selectedId && "hidden lg:flex")}
      />

      <div className={cn("flex min-w-0 flex-1 flex-col", !selectedId && "hidden lg:flex")}>
        {selectedId && promptQuery.data ? (
          <PromptEditor
            key={selectedId}
            prompt={promptQuery.data}
            onDeleted={() => router.push("/prompt-studio")}
            onDuplicated={(newId) => router.push(`/prompt-studio?open=${newId}`)}
            onBack={() => router.push("/prompt-studio")}
          />
        ) : selectedId && promptQuery.isError ? (
          <div className="flex flex-1 items-center justify-center p-6">
            <EmptyState
              icon={MessageSquareText}
              title="Couldn't load this prompt"
              description="It may have been deleted. Pick another one from the list."
            />
          </div>
        ) : selectedId && promptQuery.isLoading ? (
          <div className="p-6 text-sm text-muted-foreground">Loading…</div>
        ) : (
          <div className="flex flex-1 items-center justify-center p-6">
            <EmptyState
              icon={MessageSquareText}
              title="Select a prompt, or create a new one"
              description="Author, structure, and version-control reusable LLM prompts — right here, no external tools needed."
              action={
                <Button size="sm" onClick={handleNew}>
                  New prompt
                </Button>
              }
            />
          </div>
        )}
      </div>
    </div>
  );
}
