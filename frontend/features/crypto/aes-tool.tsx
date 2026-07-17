"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { OutputField } from "@/components/output-field";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";
import { cryptoApi } from "./api";

export function AesTool() {
  const [plaintext, setPlaintext] = useState("");
  const [passphrase, setPassphrase] = useState("");
  const [ciphertext, setCiphertext] = useState("");
  const [nonce, setNonce] = useState("");
  const [salt, setSalt] = useState("");
  const [decryptPassphrase, setDecryptPassphrase] = useState("");

  const encrypt = useMutation({
    mutationFn: () => cryptoApi.aesEncrypt(plaintext, passphrase),
    onSuccess: (data) => {
      setCiphertext(data.ciphertext);
      setNonce(data.nonce);
      setSalt(data.salt);
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Encryption failed"),
  });

  const decrypt = useMutation({
    mutationFn: () => cryptoApi.aesDecrypt(ciphertext, nonce, salt, decryptPassphrase),
    onError: (err) => toast.error(err instanceof Error ? err.message : "Decryption failed"),
  });

  return (
    <ToolCard title="AES-256-GCM" description="Passphrase-based authenticated encryption">
      <Textarea
        value={plaintext}
        onChange={(e) => setPlaintext(e.target.value)}
        placeholder="Plaintext to encrypt…"
        rows={2}
        className="font-mono text-xs"
      />
      <div className="flex items-center gap-2">
        <Label className="w-20 shrink-0 text-xs text-muted-foreground">Passphrase</Label>
        <Input type="password" value={passphrase} onChange={(e) => setPassphrase(e.target.value)} className="h-8" />
        <Button size="sm" variant="outline" onClick={() => encrypt.mutate()} disabled={!plaintext || !passphrase}>
          Encrypt
        </Button>
      </div>

      {ciphertext ? (
        <div className="flex flex-col gap-1.5">
          <OutputField value={ciphertext} placeholder="ciphertext" />
          <div className="grid grid-cols-2 gap-1.5">
            <OutputField value={nonce} placeholder="nonce" />
            <OutputField value={salt} placeholder="salt" />
          </div>
        </div>
      ) : null}

      <div className="mt-2 flex flex-col gap-2 border-t border-border pt-3">
        <p className="text-xs font-medium text-muted-foreground">Decrypt</p>
        <div className="grid grid-cols-3 gap-1.5">
          <Input value={ciphertext} onChange={(e) => setCiphertext(e.target.value)} placeholder="ciphertext" className="h-7 text-xs" />
          <Input value={nonce} onChange={(e) => setNonce(e.target.value)} placeholder="nonce" className="h-7 text-xs" />
          <Input value={salt} onChange={(e) => setSalt(e.target.value)} placeholder="salt" className="h-7 text-xs" />
        </div>
        <div className="flex items-center gap-2">
          <Input
            type="password"
            value={decryptPassphrase}
            onChange={(e) => setDecryptPassphrase(e.target.value)}
            placeholder="Passphrase"
            className="h-8"
          />
          <Button
            size="sm"
            variant="outline"
            onClick={() => decrypt.mutate()}
            disabled={!ciphertext || !nonce || !salt || !decryptPassphrase}
          >
            Decrypt
          </Button>
        </div>
        {decrypt.data ? <OutputField value={decrypt.data.text} /> : null}
      </div>
    </ToolCard>
  );
}
