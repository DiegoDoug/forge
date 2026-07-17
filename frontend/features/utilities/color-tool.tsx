"use client";

import { useMemo, useState } from "react";

import { Input } from "@/components/ui/input";
import { OutputField } from "@/components/output-field";
import { ToolCard } from "@/components/tool-card";

function hexToRgb(hex: string): [number, number, number] | null {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex.trim());
  if (!m) return null;
  return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)];
}

function rgbToHsl(r: number, g: number, b: number): [number, number, number] {
  r /= 255;
  g /= 255;
  b /= 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0;
  let s = 0;
  const l = (max + min) / 2;
  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r:
        h = (g - b) / d + (g < b ? 6 : 0);
        break;
      case g:
        h = (b - r) / d + 2;
        break;
      default:
        h = (r - g) / d + 4;
    }
    h /= 6;
  }
  return [Math.round(h * 360), Math.round(s * 100), Math.round(l * 100)];
}

export function ColorTool() {
  const [hex, setHex] = useState("#6366f1");

  const rgb = useMemo(() => hexToRgb(hex), [hex]);
  const hsl = rgb ? rgbToHsl(...rgb) : null;

  return (
    <ToolCard title="Color picker" description="Convert between HEX, RGB, and HSL">
      <div className="flex items-center gap-3">
        <input
          type="color"
          value={rgb ? hex : "#000000"}
          onChange={(e) => setHex(e.target.value)}
          className="h-10 w-14 shrink-0 cursor-pointer rounded-md border border-border bg-transparent"
        />
        <Input value={hex} onChange={(e) => setHex(e.target.value)} className="font-mono text-xs" />
      </div>

      {rgb && hsl ? (
        <div className="flex flex-col gap-1.5">
          <OutputField value={`rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`} />
          <OutputField value={`hsl(${hsl[0]}, ${hsl[1]}%, ${hsl[2]}%)`} />
          <OutputField value={hex.startsWith("#") ? hex : `#${hex}`} />
        </div>
      ) : (
        <p className="text-xs text-destructive">Enter a valid hex color (e.g. #6366f1)</p>
      )}
    </ToolCard>
  );
}
