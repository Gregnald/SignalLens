"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { api, ApiError } from "@/lib/api";
import { useDataset } from "@/lib/dataset-context";
import type { ReviewDetail } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/states";

const SENTIMENT_COLOR: Record<string, string> = {
  positive: "text-green-600",
  negative: "text-critical",
  neutral: "text-muted-foreground",
};

export default function ReviewDetailPage() {
  const params = useParams<{ reviewId: string }>();
  const { datasetId } = useDataset();
  const reviewId = Number(params.reviewId);

  const [review, setReview] = useState<ReviewDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) return;
    setLoading(true);
    api
      .getReview(datasetId, reviewId)
      .then(setReview)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load review"))
      .finally(() => setLoading(false));
  }, [datasetId, reviewId]);

  if (!datasetId) return <EmptyState title="No dataset selected" />;
  if (loading) return <LoadingState label="Loading review…" />;
  if (error) return <ErrorState message={error} />;
  if (!review) return <EmptyState title="Review not found" />;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <Card>
        <div className="mb-3 flex flex-wrap gap-2">
          {review.product_name && <Badge>{review.product_name}</Badge>}
          {review.product_category && <Badge>{review.product_category}</Badge>}
          {review.product_price && <Badge>₹{review.product_price.toLocaleString()}</Badge>}
          {review.rating !== null && <Badge>{review.rating}★</Badge>}
        </div>
        <p className="text-sm">{review.clean_text || review.raw_text}</p>
        {(review.is_duplicate || review.rating_text_conflict) && (
          <p className="mt-3 text-xs text-critical">
            {review.is_duplicate && "Flagged as a near-duplicate. "}
            {review.rating_text_conflict && "Flagged for rating/text conflict."}
          </p>
        )}
      </Card>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Feedback units</h2>
        <div className="flex flex-col gap-2">
          {review.feedback_units.map((unit) => (
            <div key={unit.id} className="rounded-lg border border-border bg-card px-4 py-3 text-sm">
              <p>{unit.text}</p>
              <p className={`mt-1 text-xs ${SENTIMENT_COLOR[unit.sentiment || ""] || ""}`}>
                {unit.sentiment ?? "unscored"}
                {unit.sentiment_score !== null && ` (${Math.round((unit.sentiment_score ?? 0) * 100)}%)`}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
