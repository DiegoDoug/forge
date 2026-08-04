"use client";

import { FolderKanban } from "lucide-react";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useProjects } from "./api";

const NONE_VALUE = "__none__";

export function ProjectPicker({
  value,
  onChange,
  className,
}: {
  value: string | null;
  onChange: (projectId: string | null) => void;
  className?: string;
}) {
  const { data: projects } = useProjects(false);
  const labelsById = new Map((projects ?? []).map((p) => [p.id, p.name]));

  return (
    <Select
      value={value ?? NONE_VALUE}
      onValueChange={(v) => onChange(v && v !== NONE_VALUE ? String(v) : null)}
    >
      <SelectTrigger className={className}>
        <FolderKanban className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
        {/* Select.Value renders the raw item `value`, not its label, unless
            given a render function - see Base UI SelectValueProps.children. */}
        <SelectValue placeholder="No project">
          {(v: string) => (v && v !== NONE_VALUE ? (labelsById.get(v) ?? "No project") : "No project")}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={NONE_VALUE}>No project</SelectItem>
        {(projects ?? []).map((project) => (
          <SelectItem key={project.id} value={project.id}>
            {project.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
