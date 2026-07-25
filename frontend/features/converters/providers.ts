import type { ComponentType } from "react";

import { JsonTool } from "./json-tool";
import { YamlTool } from "./yaml-tool";
import { XmlTool } from "./xml-tool";
import { CsvTool } from "./csv-tool";
import { RegexTool } from "./regex-tool";
import { UrlEncodeTool, UnicodeInspector } from "./url-unicode-tool";
import { CronTool } from "./cron-tool";
import { TimestampTool } from "./timestamp-tool";
import { DiffTool } from "./diff-tool";

/**
 * A declarative, provider-shaped manifest for the client-side text/data
 * tools — Universal Converter (Phase 04) Milestone 4. This is a frontend
 * organizational construct only: it does not move any tool's execution off
 * the browser (per `01_SPEC.md` §1's confirmed decision), and nothing in the
 * running app consumes it yet (that's Milestone 5). Each entry's `label`/
 * `description` mirrors that tool's own `ToolCard` props exactly, verbatim.
 */
export interface ConverterToolProvider {
  slug: string;
  label: string;
  description: string;
  Component: ComponentType;
}

export const CONVERTER_TOOL_PROVIDERS: ConverterToolProvider[] = [
  { slug: "json", label: "JSON", description: "Format, minify, and validate", Component: JsonTool },
  { slug: "yaml", label: "YAML", description: "Convert between YAML and JSON", Component: YamlTool },
  { slug: "xml", label: "XML", description: "Convert between XML and JSON", Component: XmlTool },
  { slug: "csv", label: "CSV", description: "Convert between CSV and JSON", Component: CsvTool },
  {
    slug: "regex",
    label: "Regex tester",
    description: "Live match highlighting and capture groups",
    Component: RegexTool,
  },
  {
    slug: "url-encode",
    label: "URL encode / decode",
    description: "Percent-encode text for use in a URL",
    Component: UrlEncodeTool,
  },
  {
    slug: "unicode-inspector",
    label: "Unicode inspector",
    description: "Code points and JS escape sequence for each character",
    Component: UnicodeInspector,
  },
  {
    slug: "cron",
    label: "Cron parser",
    description: "Explain a cron expression and preview upcoming runs (UTC)",
    Component: CronTool,
  },
  {
    slug: "timestamp",
    label: "Timestamp converter",
    description: "Unix epoch, ISO 8601, and local time",
    Component: TimestampTool,
  },
  { slug: "diff", label: "Diff viewer", description: "Line-by-line comparison", Component: DiffTool },
];
