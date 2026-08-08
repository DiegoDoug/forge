import { useId } from "react";

import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

// Wires Label + control + error consistently: `aria-describedby` on the
// control points at the error/hint text, and `aria-invalid` is set whenever
// an error is present — per-form ad hoc today, so this is what makes it
// systematic (04_UI_GUIDELINES.md §2, 08_ACCEPTANCE.md AC45). `children` is
// a render function so the control receives the generated ids without every
// call site wiring them by hand.
export function Field({
  label,
  htmlFor,
  error,
  hint,
  required,
  className,
  children,
}: {
  label: string;
  htmlFor?: string;
  error?: string;
  hint?: string;
  required?: boolean;
  className?: string;
  children: (props: { id: string; "aria-describedby"?: string; "aria-invalid"?: boolean }) => React.ReactNode;
}) {
  const generatedId = useId();
  const id = htmlFor ?? generatedId;
  const describedById = error || hint ? `${id}-description` : undefined;

  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <Label htmlFor={id}>
        {label}
        {required ? <span className="text-destructive">*</span> : null}
      </Label>
      {children({
        id,
        "aria-describedby": describedById,
        "aria-invalid": Boolean(error),
      })}
      {error ? (
        <p id={describedById} className="text-xs text-destructive">
          {error}
        </p>
      ) : hint ? (
        <p id={describedById} className="text-xs text-muted-foreground">
          {hint}
        </p>
      ) : null}
    </div>
  );
}
