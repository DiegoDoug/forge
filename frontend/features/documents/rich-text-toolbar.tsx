"use client";

import { useEffect, useRef, useState } from "react";
import {
  AlignCenter,
  AlignJustify,
  AlignLeft,
  AlignRight,
  Bold,
  Italic,
  List,
  ListOrdered,
  Printer,
  Redo2,
  Strikethrough,
  Underline,
  Undo2,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

export const FONT_FAMILIES = [
  { label: "Sans (Arial)", value: "Arial" },
  { label: "Serif (Times New Roman)", value: "Times New Roman" },
  { label: "Serif (Georgia)", value: "Georgia" },
  { label: "Monospace (Courier New)", value: "Courier New" },
  { label: "Verdana", value: "Verdana" },
];

export const FONT_SIZES = [10, 11, 12, 14, 16, 18, 24, 32];

const BLOCKS = [
  { label: "Paragraph", value: "P" },
  { label: "Heading 1", value: "H1" },
  { label: "Heading 2", value: "H2" },
  { label: "Heading 3", value: "H3" },
];

interface ToolbarState {
  bold: boolean;
  italic: boolean;
  underline: boolean;
  strike: boolean;
  align: "left" | "center" | "right" | "justify";
}

const DEFAULT_STATE: ToolbarState = { bold: false, italic: false, underline: false, strike: false, align: "left" };

export function RichTextToolbar({
  editorRef,
  onCommand,
  onPrint,
}: {
  editorRef: React.RefObject<HTMLDivElement | null>;
  onCommand: () => void;
  onPrint: () => void;
}) {
  const [state, setState] = useState<ToolbarState>(DEFAULT_STATE);
  // The font/size/block controls are Select popups — choosing an option
  // moves focus into a portaled listbox, which collapses the editor's text
  // selection before onValueChange fires. We track the last real selection
  // while the editor is focused and restore it before running a command.
  const savedRange = useRef<Range | null>(null);

  useEffect(() => {
    function syncState() {
      const editor = editorRef.current;
      if (!editor || document.activeElement !== editor) return;
      const sel = window.getSelection();
      if (sel && sel.rangeCount > 0) {
        savedRange.current = sel.getRangeAt(0).cloneRange();
      }
      let align: ToolbarState["align"] = "left";
      if (document.queryCommandState("justifyCenter")) align = "center";
      else if (document.queryCommandState("justifyRight")) align = "right";
      else if (document.queryCommandState("justifyFull")) align = "justify";
      setState({
        bold: document.queryCommandState("bold"),
        italic: document.queryCommandState("italic"),
        underline: document.queryCommandState("underline"),
        strike: document.queryCommandState("strikeThrough"),
        align,
      });
    }
    document.addEventListener("selectionchange", syncState);
    return () => document.removeEventListener("selectionchange", syncState);
  }, [editorRef]);

  function focusEditor() {
    const editor = editorRef.current;
    if (!editor) return;
    editor.focus();
    const sel = window.getSelection();
    if (sel && savedRange.current && editor.contains(savedRange.current.startContainer)) {
      sel.removeAllRanges();
      sel.addRange(savedRange.current);
    }
  }

  function run(command: string, value?: string) {
    focusEditor();
    document.execCommand(command, false, value);
    onCommand();
  }

  function applyFontSize(px: number) {
    focusEditor();
    document.execCommand("fontSize", false, "7");
    const editor = editorRef.current;
    editor?.querySelectorAll('font[size="7"]').forEach((el) => {
      el.removeAttribute("size");
      (el as HTMLElement).style.fontSize = `${px}px`;
    });
    onCommand();
  }

  function applyBlock(tag: string) {
    focusEditor();
    document.execCommand("formatBlock", false, `<${tag}>`);
    onCommand();
  }

  return (
    <div className="flex flex-wrap items-center gap-1 border-b border-border bg-muted/30 px-2 py-1.5">
      <ToolbarButton label="Undo" onClick={() => run("undo")}>
        <Undo2 className="h-3.5 w-3.5" />
      </ToolbarButton>
      <ToolbarButton label="Redo" onClick={() => run("redo")}>
        <Redo2 className="h-3.5 w-3.5" />
      </ToolbarButton>

      <Separator orientation="vertical" className="mx-1 h-5" />

      <Select onValueChange={(v) => v && applyBlock(v)} defaultValue="P">
        <SelectTrigger size="sm" className="h-7 w-[128px] text-xs">
          <SelectValue placeholder="Paragraph" />
        </SelectTrigger>
        <SelectContent>
          {BLOCKS.map((b) => (
            <SelectItem key={b.value} value={b.value} className="text-xs">
              {b.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select onValueChange={(v) => v && run("fontName", v)} defaultValue={FONT_FAMILIES[0].value}>
        <SelectTrigger size="sm" className="h-7 w-[150px] text-xs">
          <SelectValue placeholder="Font" />
        </SelectTrigger>
        <SelectContent>
          {FONT_FAMILIES.map((f) => (
            <SelectItem key={f.value} value={f.value} className="text-xs">
              {f.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select onValueChange={(v) => v && applyFontSize(Number(v))} defaultValue="12">
        <SelectTrigger size="sm" className="h-7 w-[68px] text-xs">
          <SelectValue placeholder="Size" />
        </SelectTrigger>
        <SelectContent>
          {FONT_SIZES.map((s) => (
            <SelectItem key={s} value={String(s)} className="text-xs">
              {s}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Separator orientation="vertical" className="mx-1 h-5" />

      <ToolbarButton label="Bold" active={state.bold} onClick={() => run("bold")}>
        <Bold className="h-3.5 w-3.5" />
      </ToolbarButton>
      <ToolbarButton label="Italic" active={state.italic} onClick={() => run("italic")}>
        <Italic className="h-3.5 w-3.5" />
      </ToolbarButton>
      <ToolbarButton label="Underline" active={state.underline} onClick={() => run("underline")}>
        <Underline className="h-3.5 w-3.5" />
      </ToolbarButton>
      <ToolbarButton label="Strikethrough" active={state.strike} onClick={() => run("strikeThrough")}>
        <Strikethrough className="h-3.5 w-3.5" />
      </ToolbarButton>

      <Separator orientation="vertical" className="mx-1 h-5" />

      <ToolbarButton label="Align left" active={state.align === "left"} onClick={() => run("justifyLeft")}>
        <AlignLeft className="h-3.5 w-3.5" />
      </ToolbarButton>
      <ToolbarButton label="Align center" active={state.align === "center"} onClick={() => run("justifyCenter")}>
        <AlignCenter className="h-3.5 w-3.5" />
      </ToolbarButton>
      <ToolbarButton label="Align right" active={state.align === "right"} onClick={() => run("justifyRight")}>
        <AlignRight className="h-3.5 w-3.5" />
      </ToolbarButton>
      <ToolbarButton label="Justify" active={state.align === "justify"} onClick={() => run("justifyFull")}>
        <AlignJustify className="h-3.5 w-3.5" />
      </ToolbarButton>

      <Separator orientation="vertical" className="mx-1 h-5" />

      <ToolbarButton label="Bullet list" onClick={() => run("insertUnorderedList")}>
        <List className="h-3.5 w-3.5" />
      </ToolbarButton>
      <ToolbarButton label="Numbered list" onClick={() => run("insertOrderedList")}>
        <ListOrdered className="h-3.5 w-3.5" />
      </ToolbarButton>

      <Separator orientation="vertical" className="mx-1 h-5" />

      <ToolbarButton label="Print" onClick={onPrint}>
        <Printer className="h-3.5 w-3.5" />
      </ToolbarButton>
    </div>
  );
}

function ToolbarButton({
  label,
  active,
  onClick,
  children,
}: {
  label: string;
  active?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <Button
      type="button"
      variant="ghost"
      size="icon-xs"
      title={label}
      aria-label={label}
      onMouseDown={(e) => e.preventDefault()}
      onClick={onClick}
      className={cn("h-7 w-7", active && "bg-accent text-accent-foreground")}
    >
      {children}
    </Button>
  );
}
