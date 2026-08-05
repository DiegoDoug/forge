"use client";

import { useRouter, useSearchParams } from "next/navigation";

import { PageHeader } from "@/components/page-header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PasswordGenerator } from "@/features/generators/password-generator";
import {
  ApiKeyGenerator,
  JwtSecretGenerator,
  NanoIdGenerator,
  RandomBytesGenerator,
  UuidGenerator,
} from "@/features/generators/simple-generators";
import { EntropyEstimator } from "@/features/generators/entropy-estimator";
import { Base64Tool, HashTool } from "@/features/crypto/base64-hash-tool";
import { AesTool } from "@/features/crypto/aes-tool";
import { JwtBuildTool, JwtDecodeTool, JwtVerifyTool } from "@/features/crypto/jwt-tool";
import { EccTool, RsaTool } from "@/features/crypto/asymmetric-tool";
import { QrTool } from "@/features/utilities/qr-tool";
import { ChecksumTool } from "@/features/utilities/checksum-tool";
import { ColorTool } from "@/features/utilities/color-tool";
import { TimezoneTool } from "@/features/utilities/timezone-tool";

// The three top-level sections, per 02_UI.md §1. These values are also the
// `?tab=` query-param values the retired /generators, /crypto, and /utilities
// routes redirect to (next.config.ts), so they are part of this phase's
// external contract - see 01_SPEC.md §3 requirement 2.
const TABS = ["generators", "crypto", "utilities"] as const;
type TabValue = (typeof TABS)[number];

const DEFAULT_TAB: TabValue = "generators";

function parseTab(value: string | null): TabValue {
  return TABS.includes(value as TabValue) ? (value as TabValue) : DEFAULT_TAB;
}

export default function DeveloperToolkitPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeTab = parseTab(searchParams.get("tab"));

  // `replace`, not `push`: switching tabs keeps the URL shareable and keeps a
  // reload on the same tab, but walking back through every tab a user clicked
  // isn't useful history. Deep-link entry (the redirects, the sidebar) still
  // produces a normal history entry of its own.
  function selectTab(value: string) {
    router.replace(`/developer-toolkit?tab=${parseTab(value)}`, { scroll: false });
  }

  return (
    <div>
      <PageHeader title="Developer Toolkit" description="Generators, crypto, and utilities" />
      <div className="p-4 md:p-6">
        <Tabs value={activeTab} onValueChange={(value) => selectTab(String(value))}>
          <TabsList>
            <TabsTrigger value="generators">Generators</TabsTrigger>
            <TabsTrigger value="crypto">Crypto</TabsTrigger>
            <TabsTrigger value="utilities">Utilities</TabsTrigger>
          </TabsList>

          {/* Each panel below composes the retired page's components in its
              original order and grid, unmodified - see 08_ACCEPTANCE.md FR1. */}
          <TabsContent value="generators" className="mt-4">
            <div className="grid gap-4 md:grid-cols-2">
              <PasswordGenerator />
              <UuidGenerator />
              <NanoIdGenerator />
              <RandomBytesGenerator />
              <ApiKeyGenerator />
              <JwtSecretGenerator />
              <EntropyEstimator />
            </div>
          </TabsContent>

          {/* Crypto keeps its own nested tab set exactly as the standalone
              page had it (02_UI.md §1) - this is the one section that was
              already internally tabbed, and why the page uses tabs at all. */}
          <TabsContent value="crypto" className="mt-4">
            <Tabs defaultValue="encode">
              <TabsList>
                <TabsTrigger value="encode">Encode &amp; Hash</TabsTrigger>
                <TabsTrigger value="aes">AES</TabsTrigger>
                <TabsTrigger value="jwt">JWT</TabsTrigger>
                <TabsTrigger value="asymmetric">RSA &amp; ECC</TabsTrigger>
              </TabsList>

              <TabsContent value="encode" className="mt-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <Base64Tool />
                  <HashTool />
                </div>
              </TabsContent>

              <TabsContent value="aes" className="mt-4">
                <div className="grid gap-4 md:grid-cols-1 md:max-w-xl">
                  <AesTool />
                </div>
              </TabsContent>

              <TabsContent value="jwt" className="mt-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <JwtDecodeTool />
                  <JwtVerifyTool />
                  <JwtBuildTool />
                </div>
              </TabsContent>

              <TabsContent value="asymmetric" className="mt-4">
                <div className="grid gap-4">
                  <RsaTool />
                  <EccTool />
                </div>
              </TabsContent>
            </Tabs>
          </TabsContent>

          <TabsContent value="utilities" className="mt-4">
            <div className="grid gap-4 md:grid-cols-2">
              <QrTool />
              <ColorTool />
              <TimezoneTool />
              <ChecksumTool />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
