import { PageHeader } from "@/components/page-header";
import { QrTool } from "@/features/utilities/qr-tool";
import { ChecksumTool } from "@/features/utilities/checksum-tool";
import { ColorTool } from "@/features/utilities/color-tool";
import { TimezoneTool } from "@/features/utilities/timezone-tool";

export default function UtilitiesPage() {
  return (
    <div>
      <PageHeader title="Utilities" description="QR codes, checksums, colors, and timezones" />
      <div className="grid gap-4 p-4 md:grid-cols-2 md:p-6">
        <QrTool />
        <ColorTool />
        <TimezoneTool />
        <ChecksumTool />
      </div>
    </div>
  );
}
