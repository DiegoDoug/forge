"use client";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

// One destructive-action treatment, used everywhere. Names the object,
// states what is lost. Replaces ~6 ad-hoc AlertDialog compositions and
// closes the 3 silent deletes the Phase 09 audit found (Documents, Notes,
// Project Init) — see 00_AUDIT.md §5.1, 08_ACCEPTANCE.md AC36-AC38.
//
// Controlled (open/onOpenChange), matching the shape those three call sites
// need: a delete button in a list row sets `open`, rather than every row
// individually wrapping itself in an AlertDialogTrigger. `onConfirm` fires
// on click and the dialog closes immediately — the same convention already
// established at every existing AlertDialog call site in this codebase
// (e.g. features/secrets/secret-detail-sheet.tsx): the mutation runs async,
// success/failure is reported via toast, the dialog does not block on it.
export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel = "Delete",
  cancelLabel = "Cancel",
  onConfirm,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Name the object being acted on, e.g. `Delete "Onboarding Runbook"?` */
  title: string;
  /** State what is lost, concretely — not a generic "this cannot be undone." */
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
}) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{cancelLabel}</AlertDialogCancel>
          <AlertDialogAction
            className="bg-destructive text-white hover:bg-destructive/90"
            onClick={onConfirm}
          >
            {confirmLabel}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
