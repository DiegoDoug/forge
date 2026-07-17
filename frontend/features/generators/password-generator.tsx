"use client";

import { useMutation } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { OutputField } from "@/components/output-field";
import { Slider } from "@/components/ui/slider";
import { ToolCard } from "@/components/tool-card";
import { generatorsApi } from "./api";

export function PasswordGenerator() {
  const [length, setLength] = useState(20);
  const [useUpper, setUseUpper] = useState(true);
  const [useLower, setUseLower] = useState(true);
  const [useDigits, setUseDigits] = useState(true);
  const [useSymbols, setUseSymbols] = useState(true);
  const [excludeAmbiguous, setExcludeAmbiguous] = useState(false);

  const generate = useMutation({
    mutationFn: () =>
      generatorsApi.password({
        length,
        use_upper: useUpper,
        use_lower: useLower,
        use_digits: useDigits,
        use_symbols: useSymbols,
        exclude_ambiguous: excludeAmbiguous,
      }),
  });

  useEffect(() => {
    generate.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <ToolCard title="Password" description="Cryptographically random, generated server-side">
      <OutputField value={generate.data?.value ?? ""} />

      <div className="flex items-center gap-3">
        <Label className="w-24 shrink-0 text-xs text-muted-foreground">Length: {length}</Label>
        <Slider
          value={[length]}
          onValueChange={(v) => setLength(Array.isArray(v) ? v[0] : v)}
          min={4}
          max={128}
          step={1}
        />
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <CheckboxOption label="Uppercase A-Z" checked={useUpper} onCheckedChange={setUseUpper} />
        <CheckboxOption label="Lowercase a-z" checked={useLower} onCheckedChange={setUseLower} />
        <CheckboxOption label="Digits 0-9" checked={useDigits} onCheckedChange={setUseDigits} />
        <CheckboxOption label="Symbols !@#$" checked={useSymbols} onCheckedChange={setUseSymbols} />
        <CheckboxOption label="Exclude ambiguous (Il1O0)" checked={excludeAmbiguous} onCheckedChange={setExcludeAmbiguous} />
      </div>

      <Button size="sm" variant="outline" className="w-fit" onClick={() => generate.mutate()} disabled={generate.isPending}>
        <RefreshCw className="h-3.5 w-3.5" />
        Regenerate
      </Button>
    </ToolCard>
  );
}

function CheckboxOption({
  label,
  checked,
  onCheckedChange,
}: {
  label: string;
  checked: boolean;
  onCheckedChange: (v: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-2 text-xs text-muted-foreground">
      <Checkbox checked={checked} onCheckedChange={(v) => onCheckedChange(Boolean(v))} />
      {label}
    </label>
  );
}
