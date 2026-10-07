"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { CHART_AXIS, CHART_GRID, TOOLTIP_STYLE, TOOLTIP_LABEL_STYLE } from "./chart-colors";

interface CategoryDatum {
  category: string;
  review_count: number;
}

/** Magnitude comparison across categories — one series, sequential blue. */
export function CategoryVolumeChart({ data }: { data: CategoryDatum[] }) {
  if (data.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No categories yet.</p>;
  }

  const top = [...data].sort((a, b) => b.review_count - a.review_count).slice(0, 10).reverse();

  return (
    <ResponsiveContainer width="100%" height={Math.max(180, top.length * 32)}>
      <BarChart data={top} layout="vertical" margin={{ top: 4, right: 24, left: 8, bottom: 4 }}>
        <CartesianGrid horizontal={false} stroke={CHART_GRID} />
        <XAxis type="number" tick={{ fontSize: 11 }} stroke={CHART_AXIS} allowDecimals={false} />
        <YAxis
          type="category"
          dataKey="category"
          width={150}
          tick={{ fontSize: 11 }}
          stroke={CHART_AXIS}
        />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          labelStyle={TOOLTIP_LABEL_STYLE}
          formatter={(value: number) => [value.toLocaleString(), "Reviews"]}
          cursor={{ fill: "rgb(var(--muted))" }}
        />
        <Bar dataKey="review_count" fill="var(--chart-1)" radius={[0, 4, 4, 0]} maxBarSize={20} />
      </BarChart>
    </ResponsiveContainer>
  );
}
