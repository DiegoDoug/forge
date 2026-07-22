import { downloadGeneration, projectInitApi, type GenerateConfig, type GenerationOut, type TemplateKind } from "./api";

/** Generates a bundle then immediately triggers its browser download - the
 * shared action both forms call on submit, matching how
 * features/documents/api.ts keeps its export logic in one place. */
export async function generateAndDownload(kind: TemplateKind, config: GenerateConfig): Promise<GenerationOut> {
  const generation = await projectInitApi.generate(kind, config);
  await downloadGeneration(generation.id, generation.name);
  return generation;
}
