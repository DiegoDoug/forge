"use client";

import { QRCodeSVG } from "qrcode.react";
import { useState } from "react";

import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";

export function QrTool() {
  const [text, setText] = useState("https://forge.local");

  return (
    <ToolCard title="QR code" description="Generate a QR code from any text or URL">
      <Textarea value={text} onChange={(e) => setText(e.target.value)} rows={2} className="font-mono text-xs" />
      <div className="flex items-center justify-center rounded-lg border border-border bg-white p-4">
        {text ? <QRCodeSVG value={text} size={180} /> : null}
      </div>
    </ToolCard>
  );
}
