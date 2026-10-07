"use client";

import { useId, useState } from "react";

import { STATUS_COLOR, CHART_MUTED_TEXT } from "./chart-colors";

interface SentimentBarProps {
  positive: number;
  neutral: number;
  negative: number;
}

/** Diverging stacked bar centered on neutral — the dataviz skill's recommended form
 * for an ordered-scale share (sentiment is exactly that: negative <-> positive). A
 * single row reads as a sentiment "meter"; negative grows left, positive grows right.
 */
export function SentimentBar({ positive, neutral, negative }: SentimentBarProps) {
  const total = positive + neutral + negative;
  const titleId = useId();
  const [hovered, setHovered] = useState<"positive" | "neutral" | "negative" | null>(null);

  if (total === 0) {
    return <p className="py-4 text-center text-sm text-muted-foreground">No sentiment data yet.</p>;
  }

  const negPct = (100 * negative) / total;
  const neuPct = (100 * neutral) / total;
  const posPct = (100 * positive) / total;

  const segments: { key: "negative" | "neutral" | "positive"; pct: number; count: number; color: string; label: string }[] = [
    { key: "negative", pct: negPct, count: negative, color: STATUS_COLOR.negative, label: "Negative" },
    { key: "neutral", pct: neuPct, count: neutral, color: "rgb(var(--muted-foreground))", label: "Neutral" },
    { key: "positive", pct: posPct, count: positive, color: STATUS_COLOR.positive, label: "Positive" },
  ];

  return (
    <div role="group" aria-labelledby={titleId}>
      <span id={titleId} className="sr-only">
        Sentiment breakdown
      </span>
      <div className="flex h-5 w-full overflow-hidden rounded-full" style={{ gap: 2, backgroundColor: "rgb(var(--muted))" }}>
        {segments.map((s) =>
          s.pct > 0 ? (
            <div
              key={s.key}
              role="img"
              aria-label={`${s.label}: ${s.count} (${s.pct.toFixed(1)}%)`}
              tabIndex={0}
              className="relative h-full cursor-default outline-none transition-opacity focus-visible:ring-2 focus-visible:ring-primary"
              style={{
                width: `${s.pct}%`,
                backgroundColor: s.color,
                opacity: hovered && hovered !== s.key ? 0.55 : 1,
              }}
              onMouseEnter={() => setHovered(s.key)}
              onMouseLeave={() => setHovered(null)}
              onFocus={() => setHovered(s.key)}
              onBlur={() => setHovered(null)}
            >
              {hovered === s.key && (
                <div
                  className="pointer-events-none absolute -top-9 left-1/2 z-10 -translate-x-1/2 whitespace-nowrap rounded-md border px-2 py-1 text-xs shadow-sm"
                  style={{ backgroundColor: "rgb(var(--card))", borderColor: "rgb(var(--border))" }}
                >
                  <span className="font-semibold">{s.count}</span>{" "}
                  <span style={{ color: CHART_MUTED_TEXT }}>{s.label.toLowerCase()}</span>
                </div>
              )}
            </div>
          ) : null
        )}
      </div>

      <div className="mt-2 flex flex-wrap gap-4 text-xs">
        {segments.map((s) => (
          <span key={s.key} className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: s.color }} />
            <span style={{ color: CHART_MUTED_TEXT }}>{s.label}</span>
            <span className="font-medium text-foreground">{s.count}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
