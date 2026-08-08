"use client";

import * as React from "react";

interface PanelErrorBoundaryProps {
  fallback: (error: unknown, reset: () => void) => React.ReactNode;
  children: React.ReactNode;
}

interface PanelErrorBoundaryState {
  error: unknown;
}

// Generalized in Phase 09 T8 from features/workbench/components/ — where it
// started (per 12_PANEL_INTERFACE.md §3 item 4, "wraps every panel so one
// panel's thrown error can never blank the rest of the grid") to the shared
// layer, so any feature can wrap a region without a cross-feature import
// into Workbench's internals. Logic is byte-identical to the original;
// nothing about it was ever Workbench-specific. React error boundaries must
// be class components — no hook equivalent exists.
export class PanelErrorBoundary extends React.Component<PanelErrorBoundaryProps, PanelErrorBoundaryState> {
  state: PanelErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: unknown): PanelErrorBoundaryState {
    return { error };
  }

  reset = (): void => this.setState({ error: null });

  render(): React.ReactNode {
    if (this.state.error !== null) {
      return this.props.fallback(this.state.error, this.reset);
    }
    return this.props.children;
  }
}
