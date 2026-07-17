"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { OutputField } from "@/components/output-field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ToolCard } from "@/components/tool-card";
import { cryptoApi } from "./api";

export function RsaTool() {
  const [keySize, setKeySize] = useState(2048);
  const [publicKey, setPublicKey] = useState("");
  const [privateKey, setPrivateKey] = useState("");
  const [plaintext, setPlaintext] = useState("");
  const [ciphertext, setCiphertext] = useState("");

  const keypair = useMutation({
    mutationFn: () => cryptoApi.rsaKeypair(keySize),
    onSuccess: (data) => {
      setPublicKey(data.public_key);
      setPrivateKey(data.private_key);
    },
  });
  const encrypt = useMutation({
    mutationFn: () => cryptoApi.rsaEncrypt(publicKey, plaintext),
    onSuccess: (data) => setCiphertext(data.text),
    onError: (err) => toast.error(err instanceof Error ? err.message : "Encryption failed"),
  });
  const decrypt = useMutation({
    mutationFn: () => cryptoApi.rsaDecrypt(privateKey, ciphertext),
    onError: (err) => toast.error(err instanceof Error ? err.message : "Decryption failed"),
  });

  return (
    <ToolCard title="RSA" description="Keypair generation and OAEP encryption">
      <div className="flex items-center gap-2">
        <Select value={String(keySize)} onValueChange={(v) => v && setKeySize(Number(v))}>
          <SelectTrigger className="h-8 w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="2048">2048-bit</SelectItem>
            <SelectItem value="3072">3072-bit</SelectItem>
            <SelectItem value="4096">4096-bit</SelectItem>
          </SelectContent>
        </Select>
        <Button size="sm" variant="outline" onClick={() => keypair.mutate()} disabled={keypair.isPending}>
          {keypair.isPending ? "Generating…" : "Generate keypair"}
        </Button>
      </div>

      {publicKey ? (
        <div className="grid grid-cols-2 gap-2">
          <LabeledKey label="Public key" value={publicKey} />
          <LabeledKey label="Private key" value={privateKey} />
        </div>
      ) : null}

      <div className="mt-1 flex flex-col gap-2 border-t border-border pt-3">
        <Textarea value={plaintext} onChange={(e) => setPlaintext(e.target.value)} placeholder="Message to encrypt…" rows={2} className="font-mono text-xs" />
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => encrypt.mutate()} disabled={!publicKey || !plaintext}>
            Encrypt with public key
          </Button>
          <Button size="sm" variant="outline" onClick={() => decrypt.mutate()} disabled={!privateKey || !ciphertext}>
            Decrypt with private key
          </Button>
        </div>
        {ciphertext ? <OutputField value={ciphertext} placeholder="ciphertext" /> : null}
        {decrypt.data ? <OutputField value={decrypt.data.text} /> : null}
      </div>
    </ToolCard>
  );
}

export function EccTool() {
  const [publicKey, setPublicKey] = useState("");
  const [privateKey, setPrivateKey] = useState("");
  const [message, setMessage] = useState("");
  const [signature, setSignature] = useState("");

  const keypair = useMutation({
    mutationFn: cryptoApi.eccKeypair,
    onSuccess: (data) => {
      setPublicKey(data.public_key);
      setPrivateKey(data.private_key);
    },
  });
  const sign = useMutation({
    mutationFn: () => cryptoApi.eccSign(privateKey, message),
    onSuccess: (data) => setSignature(data.text),
  });
  const verify = useMutation({ mutationFn: () => cryptoApi.eccVerify(publicKey, message, signature) });

  return (
    <ToolCard title="ECDSA (P-256)" description="Keypair generation, signing, and verification">
      <Button size="sm" variant="outline" className="w-fit" onClick={() => keypair.mutate()} disabled={keypair.isPending}>
        {keypair.isPending ? "Generating…" : "Generate keypair"}
      </Button>

      {publicKey ? (
        <div className="grid grid-cols-2 gap-2">
          <LabeledKey label="Public key" value={publicKey} />
          <LabeledKey label="Private key" value={privateKey} />
        </div>
      ) : null}

      <div className="mt-1 flex flex-col gap-2 border-t border-border pt-3">
        <Textarea value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Message to sign…" rows={2} className="font-mono text-xs" />
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => sign.mutate()} disabled={!privateKey || !message}>
            Sign
          </Button>
          <Button size="sm" variant="outline" onClick={() => verify.mutate()} disabled={!publicKey || !message || !signature}>
            Verify
          </Button>
        </div>
        {signature ? <OutputField value={signature} placeholder="signature" /> : null}
        {verify.data ? (
          <p className={`text-xs font-medium ${verify.data.valid ? "text-emerald-500" : "text-destructive"}`}>
            {verify.data.valid ? "Signature valid" : "Signature invalid"}
          </p>
        ) : null}
      </div>
    </ToolCard>
  );
}

function LabeledKey({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <OutputField value={value} mono />
    </div>
  );
}
