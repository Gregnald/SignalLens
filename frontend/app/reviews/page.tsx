"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { api, ApiError } from "@/lib/api";
import { useDataset } from "@/lib/dataset-context";
import type { ReviewListResponse } from "@/lib/types";
import { EmptyState, ErrorState, Skeleton } from "@/components/ui/states";
import { Button } from "@/components/ui/button";

export default function ReviewExplorerPage() {
  const { datasetId } = useDataset();
  const [data, setData] = useState<ReviewListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .listReviews(datasetId, { page, page_size: 20 })
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load reviews"))
      .finally(() => setLoading(false));
  }, [datasetId, page]);

  if (!datasetId) return <EmptyState title="No dataset selected" />;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Review Explorer</h1>

      {loading && (
        <div className="flex flex-col gap-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      )}

      {error && <ErrorState message={error} />}

      {!loading && !error && data && data.items.length === 0 && (
        <EmptyState title="No reviews found" />
      )}

      {!loading && !error && data && data.items.length > 0 && (
        <>
          <div className="flex flex-col gap-2">
            {data.items.map((r) => (
              <Link
                key={r.id}
                href={`/reviews/${r.id}`}
                className="flex items-start justify-between gap-4 rounded-lg border border-border bg-card px-4 py-3 hover:bg-muted"
              >
                <div className="flex-1">
                  <p className="text-sm">{r.clean_text || r.raw_text}</p>
                  <div className="mt-1 flex gap-3 text-xs text-muted-foreground">
                    {r.product_name && <span className="font-medium text-foreground">{r.product_name}</span>}
                    {r.product_category && <span>{r.product_category}</span>}
                    {r.review_date && <span>{r.review_date}</span>}
                    {r.is_duplicate && <span className="text-critical">duplicate</span>}
                    {r.rating_text_conflict && <span className="text-critical">rating conflict</span>}
                  </div>
                </div>
                {r.rating !== null && (
                  <span className="shrink-0 text-sm font-semibold">{r.rating}★</span>
                )}
              </Link>
            ))}
          </div>

          <div className="mt-6 flex items-center justify-between">
            <Button variant="secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {data.page} of {Math.max(1, Math.ceil(data.total / data.page_size))}
            </span>
            <Button
              variant="secondary"
              disabled={page * data.page_size >= data.total}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
