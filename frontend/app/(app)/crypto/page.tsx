import { PageHeader } from "@/components/page-header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Base64Tool, HashTool } from "@/features/crypto/base64-hash-tool";
import { AesTool } from "@/features/crypto/aes-tool";
import { JwtBuildTool, JwtDecodeTool, JwtVerifyTool } from "@/features/crypto/jwt-tool";
import { EccTool, RsaTool } from "@/features/crypto/asymmetric-tool";

export default function CryptoPage() {
  return (
    <div>
      <PageHeader title="Crypto" description="Encrypt, hash, sign, and inspect tokens" />
      <div className="p-4 md:p-6">
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
      </div>
    </div>
  );
}
