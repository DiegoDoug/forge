"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import type { FdkPhaseConfig } from "./api";
import { generateAndDownload } from "./generation-actions";

const MAX_PHASE_NAME = 80;
const MAX_OBJECTIVE = 500;

function slugPreview(phaseNumber: string, phaseName: string): string {
  const num = Number(phaseNumber);
  const padded = Number.isInteger(num) && num > 0 ? String(num).padStart(2, "0") : "XX";
  const slug =
    phaseName
      .trim()
      .replace(/[^A-Za-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "Name";
  return `Phase-${padded}-${slug}`;
}

export function FdkPhaseForm({ onGenerated }: { onGenerated: () => void }) {
  const [phaseNumber, setPhaseNumber] = useState("");
  const [phaseName, setPhaseName] = useState("");
  const [objective, setObjective] = useState("");
  const [touched, setTouched] = useState(false);
  const qc = useQueryClient();

  const phaseNumberValue = Number(phaseNumber);
  const errors = {
    phaseNumber:
      !phaseNumber || !Number.isInteger(phaseNumberValue) || phaseNumberValue < 1
        ? "Enter a phase number of 1 or higher."
        : null,
    phaseName: !phaseName.trim()
      ? "Phase name is required."
      : phaseName.length > MAX_PHASE_NAME
        ? `Keep it under ${MAX_PHASE_NAME} characters.`
        : null,
    objective: !objective.trim()
      ? "Objective is required."
      : objective.length > MAX_OBJECTIVE
        ? `Keep it under ${MAX_OBJECTIVE} characters.`
        : null,
  };
  const isValid = !errors.phaseNumber && !errors.phaseName && !errors.objective;

  const generate = useMutation({
    mutationFn: () => {
      const config: FdkPhaseConfig = {
        phase_number: phaseNumberValue,
        phase_name: phaseName.trim(),
        objective: objective.trim(),
      };
      return generateAndDownload("fdk_phase", config);
    },
    onSuccess: (generation) => {
      qc.invalidateQueries({ queryKey: ["project-init", "history"] });
      toast.success(`Generated ${generation.name} (${generation.file_count} files).`);
      onGenerated();
    },
    onError: () => toast.error("Couldn't generate the scaffold. Try again."),
  });

  function handleSubmit() {
    setTouched(true);
    if (isValid) generate.mutate();
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="phase-number">Phase number</Label>
        <Input
          id="phase-number"
          type="number"
          min={1}
          value={phaseNumber}
          onChange={(e) => setPhaseNumber(e.target.value)}
          onBlur={() => setTouched(true)}
          aria-invalid={touched && !!errors.phaseNumber}
        />
        {touched && errors.phaseNumber ? <p className="text-xs text-destructive">{errors.phaseNumber}</p> : null}
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="phase-name">Phase name</Label>
        <Input
          id="phase-name"
          value={phaseName}
          onChange={(e) => setPhaseName(e.target.value)}
          onBlur={() => setTouched(true)}
          placeholder="Knowledge Hub"
          aria-invalid={touched && !!errors.phaseName}
        />
        {touched && errors.phaseName ? <p className="text-xs text-destructive">{errors.phaseName}</p> : null}
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="phase-objective">Objective</Label>
        <Textarea
          id="phase-objective"
          value={objective}
          onChange={(e) => setObjective(e.target.value)}
          onBlur={() => setTouched(true)}
          placeholder="Unify Notes, Documents, and Ingest output into one searchable knowledge base."
          rows={3}
          aria-invalid={touched && !!errors.objective}
        />
        {touched && errors.objective ? <p className="text-xs text-destructive">{errors.objective}</p> : null}
      </div>

      {phaseNumber || phaseName ? (
        <p className="text-xs text-muted-foreground">
          Will generate: <code className="font-mono">{slugPreview(phaseNumber, phaseName)}/</code>
        </p>
      ) : null}

      <Button onClick={handleSubmit} disabled={!isValid || generate.isPending} className="w-fit">
        {generate.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
        Generate & Download
      </Button>
    </div>
  );
}
