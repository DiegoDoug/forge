"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowLeft, Copy, History, Save, Trash2, Undo2 } from "lucide-react";
import { toast } from "sonner";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { type Prompt, type PromptVariable, usePromptStudioMutations } from "./api";
import { PreviewPanel } from "./preview-panel";
import { PromptBodyEditor } from "./prompt-body-editor";
import { extractPlaceholders } from "./templating";
import { VariablesPanel } from "./variables-panel";
import { VersionHistorySheet } from "./version-history-sheet";

// Must match backend/app/schemas/prompt_studio.py exactly - these are
// enforced client-side too (01_SPEC.md §3.15) so a limit violation is an
// inline error, not a round trip to discover.
const MAX_NAME_LENGTH = 200;
const MAX_DESCRIPTION_LENGTH = 1000;
const MAX_BODY_LENGTH = 20000;
const MAX_TAGS = 10;
const MAX_TAG_LENGTH = 30;

export function PromptEditor({
  prompt,
  onDeleted,
  onDuplicated,
  onBack,
}: {
  prompt: Prompt;
  onDeleted: () => void;
  onDuplicated: (newId: string) => void;
  onBack: () => void;
}) {
  const { updateMeta, updateContent, remove, duplicate } = usePromptStudioMutations();

  const [name, setName] = useState(prompt.name);
  const [description, setDescription] = useState(prompt.description ?? "");
  const [tagsText, setTagsText] = useState(prompt.tags.join(", "));
  const [body, setBody] = useState(prompt.body);
  const [variables, setVariables] = useState<PromptVariable[]>(prompt.variables);
  const [historyOpen, setHistoryOpen] = useState(false);
  const metaSaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const loadedFor = useRef<string | null>(null);

  useEffect(() => {
    // Keyed by id *and* version_number: a restore (or any other operation
    // that changes the server's current content) must resync the local edit
    // buffer even though the prompt id hasn't changed - otherwise the editor
    // shows a stale "unsaved changes" state comparing the old edit buffer
    // against the newly-restored content, instead of reflecting what
    // actually just became current.
    const key = `${prompt.id}:${prompt.version_number}`;
    if (loadedFor.current !== key) {
      setName(prompt.name);
      setDescription(prompt.description ?? "");
      setTagsText(prompt.tags.join(", "));
      setBody(prompt.body);
      setVariables(prompt.variables);
      loadedFor.current = key;
    }
  }, [prompt]);

  const contentDirty = body !== prompt.body || JSON.stringify(variables) !== JSON.stringify(prompt.variables);

  const declaredNames = variables.map((v) => v.name).filter(Boolean);
  const undeclared = Array.from(extractPlaceholders(body)).filter((name) => !declaredNames.includes(name));
  const bodyTooLong = body.length > MAX_BODY_LENGTH;

  const parsedTags = tagsText
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);
  const tagsError =
    parsedTags.length > MAX_TAGS
      ? `At most ${MAX_TAGS} tags.`
      : parsedTags.some((t) => t.length > MAX_TAG_LENGTH)
        ? `Each tag must be at most ${MAX_TAG_LENGTH} characters.`
        : null;

  function scheduleMetaSave(patch: { name?: string; description?: string; tags?: string[] }) {
    if (metaSaveTimer.current) clearTimeout(metaSaveTimer.current);
    metaSaveTimer.current = setTimeout(() => {
      updateMeta.mutate(
        { id: prompt.id, input: patch },
        { onError: () => toast.error("Couldn't save changes.") },
      );
    }, 600);
  }

  function handleNameChange(value: string) {
    setName(value);
    scheduleMetaSave({ name: value.slice(0, MAX_NAME_LENGTH) });
  }

  function handleDescriptionChange(value: string) {
    setDescription(value);
    scheduleMetaSave({ description: value.slice(0, MAX_DESCRIPTION_LENGTH) });
  }

  function handleTagsChange(value: string) {
    setTagsText(value);
    const tags = value
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    // Don't autosave invalid tags - the inline error (tagsError) is the
    // client-side signal; only a valid tag set reaches the backend.
    if (tags.length <= MAX_TAGS && tags.every((t) => t.length <= MAX_TAG_LENGTH)) {
      scheduleMetaSave({ tags });
    }
  }

  function handleSaveContent() {
    if (undeclared.length > 0) {
      toast.error(`Body references undeclared variable(s): ${undeclared.join(", ")}`);
      return;
    }
    if (bodyTooLong) {
      toast.error(`Body must be at most ${MAX_BODY_LENGTH.toLocaleString()} characters.`);
      return;
    }
    updateContent.mutate(
      { id: prompt.id, input: { body, variables } },
      {
        onSuccess: (updated) => toast.success(`Saved v${updated.version_number}.`),
        onError: () => toast.error("Couldn't save — check for undeclared variables or invalid variable names."),
      },
    );
  }

  function handleDiscardContent() {
    setBody(prompt.body);
    setVariables(prompt.variables);
  }

  function handleDelete() {
    remove.mutate(prompt.id, {
      onSuccess: onDeleted,
      onError: () => toast.error("Couldn't delete this prompt."),
    });
  }

  function handleDuplicate() {
    duplicate.mutate(prompt.id, {
      onSuccess: (created) => {
        toast.success(`Duplicated as "${created.name}".`);
        onDuplicated(created.id);
      },
      onError: () => toast.error("Couldn't duplicate this prompt."),
    });
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto">
      <div className="flex flex-col gap-2 border-b border-border p-4">
        <div className="flex items-center gap-2">
          <Button size="icon-sm" variant="ghost" title="Back to list" aria-label="Back to list" onClick={onBack} className="lg:hidden">
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <Input
            value={name}
            onChange={(e) => handleNameChange(e.target.value)}
            placeholder="Untitled prompt"
            maxLength={MAX_NAME_LENGTH}
            className="h-8 flex-1 border-none bg-transparent px-1 text-base font-semibold shadow-none focus-visible:ring-0"
          />
          <Badge variant="secondary">v{prompt.version_number}</Badge>
          <Button size="icon-sm" variant="ghost" title="Duplicate" onClick={handleDuplicate}>
            <Copy className="h-4 w-4" />
          </Button>
          <Button size="icon-sm" variant="ghost" title="Version history" onClick={() => setHistoryOpen(true)}>
            <History className="h-4 w-4" />
          </Button>
          <AlertDialog>
            <AlertDialogTrigger render={<Button size="icon-sm" variant="ghost" title="Delete" />}>
              <Trash2 className="h-4 w-4" />
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete this prompt?</AlertDialogTitle>
                <AlertDialogDescription>
                  This permanently removes &quot;{prompt.name}&quot; and all {prompt.version_number} of its versions.
                  This can&apos;t be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
        <Input
          value={description}
          onChange={(e) => handleDescriptionChange(e.target.value)}
          placeholder="Description (optional)"
          maxLength={MAX_DESCRIPTION_LENGTH}
          className="h-7 border-none bg-transparent px-1 text-sm text-muted-foreground shadow-none focus-visible:ring-0"
        />
        <Input
          value={tagsText}
          onChange={(e) => handleTagsChange(e.target.value)}
          placeholder="Tags, comma-separated (optional)"
          aria-invalid={!!tagsError}
          className="h-7 border-none bg-transparent px-1 text-xs shadow-none focus-visible:ring-0"
        />
        {tagsError ? <p className="px-1 text-[11px] text-destructive">{tagsError}</p> : null}
      </div>

      <div className="flex flex-col gap-4 p-4">
        <VariablesPanel variables={variables} onChange={setVariables} />

        <div>
          <div className="mb-1.5 flex items-center justify-between">
            <h3 className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
              Body{" "}
              <span className={bodyTooLong ? "text-destructive" : ""}>
                ({body.length.toLocaleString()}/{MAX_BODY_LENGTH.toLocaleString()})
              </span>
            </h3>
            {contentDirty ? (
              <div className="flex items-center gap-1.5">
                <Button size="xs" variant="ghost" onClick={handleDiscardContent}>
                  <Undo2 className="h-3 w-3" />
                  Discard
                </Button>
                <Button
                  size="xs"
                  onClick={handleSaveContent}
                  disabled={updateContent.isPending || bodyTooLong || undeclared.length > 0}
                >
                  <Save className="h-3 w-3" />
                  Save
                </Button>
              </div>
            ) : null}
          </div>
          <PromptBodyEditor value={body} onChange={setBody} declaredNames={declaredNames} />
          {bodyTooLong ? (
            <p className="mt-1 text-xs text-destructive">
              Body must be at most {MAX_BODY_LENGTH.toLocaleString()} characters ({body.length.toLocaleString()} now).
            </p>
          ) : null}
          {undeclared.length > 0 ? (
            <p className="mt-1 text-xs text-destructive">
              References undeclared variable(s): {undeclared.join(", ")}. Escape a literal $ as $$.
            </p>
          ) : null}
        </div>

        <PreviewPanel body={body} variables={variables} />
      </div>

      <VersionHistorySheet promptId={prompt.id} open={historyOpen} onOpenChange={setHistoryOpen} />
    </div>
  );
}
