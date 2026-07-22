"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, X } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { AI_INSTRUCTIONS_FILES, type AiInstructionsConfig, type AiInstructionsFile } from "./api";
import { generateAndDownload } from "./generation-actions";

const MAX_PROJECT_NAME = 80;
const MAX_DESCRIPTION = 1000;
const MAX_TECH_STACK = 20;

export function AiInstructionsForm({ onGenerated }: { onGenerated: () => void }) {
  const [projectName, setProjectName] = useState("");
  const [description, setDescription] = useState("");
  const [conventions, setConventions] = useState("");
  const [techStack, setTechStack] = useState<string[]>([]);
  const [techStackInput, setTechStackInput] = useState("");
  const [outputFiles, setOutputFiles] = useState<AiInstructionsFile[]>(["CLAUDE.md"]);
  const [touched, setTouched] = useState(false);
  const qc = useQueryClient();

  const errors = {
    projectName: !projectName.trim()
      ? "Project name is required."
      : projectName.length > MAX_PROJECT_NAME
        ? `Keep it under ${MAX_PROJECT_NAME} characters.`
        : null,
    description: !description.trim()
      ? "Description is required."
      : description.length > MAX_DESCRIPTION
        ? `Keep it under ${MAX_DESCRIPTION} characters.`
        : null,
    outputFiles: outputFiles.length === 0 ? "Pick at least one file to generate." : null,
  };
  const isValid = !errors.projectName && !errors.description && !errors.outputFiles;

  function addTechStackTag() {
    const value = techStackInput.trim();
    if (!value || techStack.includes(value) || techStack.length >= MAX_TECH_STACK) return;
    setTechStack([...techStack, value]);
    setTechStackInput("");
  }

  function toggleOutputFile(file: AiInstructionsFile, checked: boolean) {
    setOutputFiles((prev) => (checked ? [...prev, file] : prev.filter((f) => f !== file)));
  }

  const generate = useMutation({
    mutationFn: () => {
      const config: AiInstructionsConfig = {
        project_name: projectName.trim(),
        description: description.trim(),
        tech_stack: techStack,
        conventions: conventions.trim(),
        output_files: outputFiles,
      };
      return generateAndDownload("ai_instructions", config);
    },
    onSuccess: (generation) => {
      qc.invalidateQueries({ queryKey: ["project-init", "history"] });
      toast.success(`Generated ${generation.name} (${generation.file_count} files).`);
      onGenerated();
    },
    onError: () => toast.error("Couldn't generate the instructions. Try again."),
  });

  function handleSubmit() {
    setTouched(true);
    if (isValid) generate.mutate();
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="project-name">Project name</Label>
        <Input
          id="project-name"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          onBlur={() => setTouched(true)}
          placeholder="acme-api"
          aria-invalid={touched && !!errors.projectName}
        />
        {touched && errors.projectName ? <p className="text-xs text-destructive">{errors.projectName}</p> : null}
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="project-description">Description</Label>
        <Textarea
          id="project-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          onBlur={() => setTouched(true)}
          rows={3}
          placeholder="An internal API for managing customer orders."
          aria-invalid={touched && !!errors.description}
        />
        {touched && errors.description ? <p className="text-xs text-destructive">{errors.description}</p> : null}
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="tech-stack">Tech stack</Label>
        <div className="flex gap-2">
          <Input
            id="tech-stack"
            value={techStackInput}
            onChange={(e) => setTechStackInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addTechStackTag();
              }
            }}
            placeholder="FastAPI"
          />
          <Button type="button" variant="outline" size="sm" onClick={addTechStackTag}>
            Add
          </Button>
        </div>
        {techStack.length > 0 ? (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {techStack.map((tag) => (
              <span key={tag} className="inline-flex items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-xs">
                {tag}
                <button
                  type="button"
                  onClick={() => setTechStack(techStack.filter((t) => t !== tag))}
                  aria-label={`Remove ${tag}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        ) : null}
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="conventions">Conventions (optional)</Label>
        <Textarea
          id="conventions"
          value={conventions}
          onChange={(e) => setConventions(e.target.value)}
          rows={3}
          placeholder="Use snake_case for Python, prefer composition over inheritance..."
        />
      </div>

      <fieldset className="flex flex-col gap-1.5">
        <legend className="text-sm font-medium">Files to generate</legend>
        <div className="flex flex-col gap-2 pt-1">
          {AI_INSTRUCTIONS_FILES.map((file) => (
            <label key={file} className="flex items-center gap-2 text-sm">
              <Checkbox
                checked={outputFiles.includes(file)}
                onCheckedChange={(checked) => toggleOutputFile(file, Boolean(checked))}
              />
              {file}
            </label>
          ))}
        </div>
        {touched && errors.outputFiles ? <p className="text-xs text-destructive">{errors.outputFiles}</p> : null}
      </fieldset>

      <Button onClick={handleSubmit} disabled={!isValid || generate.isPending} className="w-fit">
        {generate.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
        Generate & Download
      </Button>
    </div>
  );
}
