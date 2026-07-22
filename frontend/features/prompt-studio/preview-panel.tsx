"use client";

import { useMemo, useState } from "react";
import { Check, Copy } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { PromptVariable } from "./api";
import { substitute } from "./templating";

/** Client-side only - never calls a backend endpoint per keystroke, per
 * 01_SPEC.md §3.5. Substitution/escaping/validation only, per §3.16. */
export function PreviewPanel({ body, variables }: { body: string; variables: PromptVariable[] }) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [copied, setCopied] = useState(false);

  const resolvedValues = useMemo(() => {
    const merged: Record<string, string> = {};
    for (const v of variables) {
      const entered = values[v.name];
      if (entered !== undefined) {
        merged[v.name] = entered;
      } else if (v.default != null) {
        merged[v.name] = String(v.default);
      }
    }
    return merged;
  }, [values, variables]);

  const { rendered, missing } = useMemo(() => substitute(body, resolvedValues), [body, resolvedValues]);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(rendered);
    } catch {
      toast.error("Couldn't copy to clipboard.");
      return;
    }
    setCopied(true);
    toast.success("Copied rendered prompt to clipboard.");
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="flex flex-col gap-3">
      <h3 className="text-xs font-medium tracking-wide text-muted-foreground uppercase">Preview</h3>

      {variables.length > 0 ? (
        <div className="flex flex-col gap-2">
          {variables.map((variable) => (
            <div key={variable.name} className="flex items-center gap-2">
              <label className="w-32 shrink-0 truncate font-mono text-xs text-muted-foreground" title={variable.name}>
                {variable.name}
                {variable.required ? <span className="text-destructive"> *</span> : null}
              </label>
              <Input
                value={values[variable.name] ?? (variable.default != null ? String(variable.default) : "")}
                onChange={(e) => setValues((prev) => ({ ...prev, [variable.name]: e.target.value }))}
                placeholder={variable.description ?? undefined}
                className="h-7 flex-1 text-xs"
              />
            </div>
          ))}
        </div>
      ) : null}

      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">
          {missing.length > 0 ? `Unresolved: ${missing.join(", ")}` : "All variables resolved"}
        </span>
        <Button size="xs" variant="outline" onClick={handleCopy} disabled={!rendered}>
          {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
          Copy
        </Button>
      </div>

      <pre className="max-h-56 overflow-auto rounded-lg border border-border bg-muted/40 p-2 font-mono text-xs whitespace-pre-wrap">
        {rendered.split(new RegExp(`(${missing.map((m) => `\\$\\{${m}\\}`).join("|") || "$^"})`)).map((chunk, i) =>
          missing.includes(chunk.slice(2, -1)) ? (
            <span key={i} className="rounded bg-destructive/15 px-0.5 text-destructive" title="Missing value">
              {chunk}
            </span>
          ) : (
            <span key={i}>{chunk}</span>
          ),
        )}
      </pre>
    </div>
  );
}
