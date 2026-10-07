// dataviz tokens defined in app/globals.css — categorical series in fixed order,
// status colors reserved for state (never reused as a generic series color).
export const CHART_SERIES = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
] as const;

export const STATUS_COLOR: Record<string, string> = {
  good: "var(--status-good)",
  positive: "var(--status-good)",
  warning: "var(--status-warning)",
  low: "var(--status-good)",
  medium: "var(--status-warning)",
  serious: "var(--status-serious)",
  high: "var(--status-serious)",
  critical: "var(--status-critical)",
  negative: "var(--status-critical)",
};

export const CHART_GRID = "var(--chart-grid)";
export const CHART_AXIS = "var(--chart-axis)";
export const CHART_MUTED_TEXT = "rgb(var(--muted-foreground))";

export const TOOLTIP_STYLE = {
  backgroundColor: "rgb(var(--card))",
  border: "1px solid rgb(var(--border))",
  borderRadius: 8,
  fontSize: 12,
};

export const TOOLTIP_LABEL_STYLE = { color: "rgb(var(--muted-foreground))" };
