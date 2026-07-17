import { PageHeader } from "@/components/page-header";
import { JsonTool } from "@/features/converters/json-tool";
import { UrlEncodeTool, UnicodeInspector } from "@/features/converters/url-unicode-tool";
import { RegexTool } from "@/features/converters/regex-tool";
import { CronTool } from "@/features/converters/cron-tool";
import { DiffTool } from "@/features/converters/diff-tool";
import { TimestampTool } from "@/features/converters/timestamp-tool";

export default function ConvertersPage() {
  return (
    <div>
      <PageHeader title="Converters" description="JSON, regex, cron, diffs, and timestamps" />
      <div className="grid gap-4 p-4 md:grid-cols-2 md:p-6">
        <JsonTool />
        <RegexTool />
        <UrlEncodeTool />
        <UnicodeInspector />
        <CronTool />
        <TimestampTool />
        <DiffTool />
      </div>
    </div>
  );
}
