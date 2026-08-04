"use client";

import Link from "next/link";
import { FileText, KeyRound, StickyNote } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ProjectSummary } from "./api";

export function ProjectCard({ project }: { project: ProjectSummary }) {
  return (
    <Link href={`/projects/${project.id}`}>
      <Card size="sm" className="h-full transition hover:border-foreground/30">
        <CardHeader>
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: project.color }} />
              <CardTitle className="text-sm">{project.name}</CardTitle>
            </div>
            {project.archived ? <Badge variant="secondary">Archived</Badge> : null}
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <KeyRound className="h-3.5 w-3.5" /> {project.secret_count}
            </span>
            <span className="flex items-center gap-1">
              <StickyNote className="h-3.5 w-3.5" /> {project.note_count}
            </span>
            <span className="flex items-center gap-1">
              <FileText className="h-3.5 w-3.5" /> {project.document_count}
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
