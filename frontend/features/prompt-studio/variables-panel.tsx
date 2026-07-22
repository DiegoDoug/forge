"use client";

import { Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { PromptVariable, PromptVariableType } from "./api";

const VARIABLE_NAME_PATTERN = /^[A-Za-z_][A-Za-z0-9_]{0,63}$/;

export function isValidVariableName(name: string): boolean {
  return VARIABLE_NAME_PATTERN.test(name);
}

export function VariablesPanel({
  variables,
  onChange,
}: {
  variables: PromptVariable[];
  onChange: (variables: PromptVariable[]) => void;
}) {
  function updateVariable(index: number, patch: Partial<PromptVariable>) {
    onChange(variables.map((v, i) => (i === index ? { ...v, ...patch } : v)));
  }

  function removeVariable(index: number) {
    onChange(variables.filter((_, i) => i !== index));
  }

  function addVariable() {
    onChange([...variables, { name: "", type: "string", required: true, default: null, description: "" }]);
  }

  const names = variables.map((v) => v.name);

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-medium tracking-wide text-muted-foreground uppercase">Variables</h3>
        <Button size="xs" variant="outline" onClick={addVariable} disabled={variables.length >= 50}>
          <Plus className="h-3 w-3" />
          Add variable
        </Button>
      </div>

      {variables.length === 0 ? (
        <p className="text-xs text-muted-foreground">
          No variables declared. Reference one in the body as <code>${"{name}"}</code> once you add it here.
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {variables.map((variable, index) => {
            const isDuplicate = names.filter((n) => n === variable.name).length > 1 && variable.name.length > 0;
            const isInvalidName = variable.name.length > 0 && !isValidVariableName(variable.name);
            return (
              <div key={index} className="flex flex-col gap-1.5 rounded-lg border border-border p-2">
                <div className="flex items-center gap-1.5">
                  <Input
                    value={variable.name}
                    onChange={(e) => updateVariable(index, { name: e.target.value })}
                    placeholder="variable_name"
                    maxLength={64}
                    className="h-7 flex-1 font-mono text-xs"
                    aria-invalid={isInvalidName || isDuplicate}
                  />
                  <Select
                    value={variable.type}
                    onValueChange={(value) => updateVariable(index, { type: value as PromptVariableType })}
                  >
                    <SelectTrigger size="sm" className="h-7 w-24 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="string">string</SelectItem>
                      <SelectItem value="number">number</SelectItem>
                      <SelectItem value="boolean">boolean</SelectItem>
                    </SelectContent>
                  </Select>
                  <label className="flex items-center gap-1 text-xs whitespace-nowrap">
                    <Checkbox
                      checked={variable.required}
                      onCheckedChange={(checked) => updateVariable(index, { required: checked === true })}
                    />
                    Required
                  </label>
                  <Button
                    size="icon-xs"
                    variant="ghost"
                    aria-label={`Remove variable ${variable.name || index + 1}`}
                    onClick={() => removeVariable(index)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
                <div className="flex items-center gap-1.5">
                  <Input
                    value={variable.default != null ? String(variable.default) : ""}
                    onChange={(e) => updateVariable(index, { default: e.target.value })}
                    placeholder="Default value (optional)"
                    className="h-7 flex-1 text-xs"
                  />
                  <Input
                    value={variable.description ?? ""}
                    onChange={(e) => updateVariable(index, { description: e.target.value })}
                    placeholder="Description (optional)"
                    maxLength={500}
                    className="h-7 flex-1 text-xs"
                  />
                </div>
                {isInvalidName ? (
                  <p className="text-[11px] text-destructive">
                    Must start with a letter/underscore and contain only letters, numbers, underscores.
                  </p>
                ) : isDuplicate ? (
                  <p className="text-[11px] text-destructive">Variable names must be unique.</p>
                ) : null}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
