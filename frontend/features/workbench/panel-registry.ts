import type { WorkbenchPanelDefinition } from "./panel-types";

const registry = new Map<string, WorkbenchPanelDefinition>();

/** Registers a panel's `type` as renderable. Called once, at module load, by each panel-owning feature. */
export function registerWorkbenchPanel(definition: WorkbenchPanelDefinition): void {
  registry.set(definition.type, definition);
}

/** Every panel registered so far, in registration order. */
export function getRegisteredPanels(): WorkbenchPanelDefinition[] {
  return Array.from(registry.values());
}
