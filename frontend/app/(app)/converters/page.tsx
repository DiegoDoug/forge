import { PageHeader } from "@/components/page-header";
import { JsonTool } from "@/features/converters/json-tool";
import { YamlTool } from "@/features/converters/yaml-tool";
import { XmlTool } from "@/features/converters/xml-tool";
import { CsvTool } from "@/features/converters/csv-tool";
import { UrlEncodeTool, UnicodeInspector } from "@/features/converters/url-unicode-tool";
import { RegexTool } from "@/features/converters/regex-tool";
import { CronTool } from "@/features/converters/cron-tool";
import { DiffTool } from "@/features/converters/diff-tool";
import { TimestampTool } from "@/features/converters/timestamp-tool";

export default function ConvertersPage() {
  return (
    <div>
      <PageHeader title="Converters" description="JSON, YAML, XML, CSV, regex, cron, diffs, and timestamps" />
      <div className="grid gap-4 p-4 md:grid-cols-2 md:p-6">
        <JsonTool />
        <YamlTool />
        <XmlTool />
        <CsvTool />
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
