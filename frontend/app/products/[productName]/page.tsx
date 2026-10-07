"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ChevronLeft } from "lucide-react";

import { api, ApiError } from "@/lib/api";
import { useDataset } from "@/lib/dataset-context";
import type { ProductDetail } from "@/lib/types";
import { Card, CardTitle, CardValue } from "@/components/ui/card";
import { SeverityBadge } from "@/components/ui/badge";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/states";
import { SentimentBar } from "@/components/charts/sentiment-bar";
import { RatingDistributionChart } from "@/components/charts/rating-distribution-chart";

export default function ProductDetailPage() {
  const params = useParams<{ productName: string }>();
  const productName = decodeURIComponent(params.productName);
  const { datasetId } = useDataset();

  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) return;
    setLoading(true);
    api
      .getProduct(datasetId, productName)
      .then(setProduct)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load product"))
      .finally(() => setLoading(false));
  }, [datasetId, productName]);

  if (loading) return <LoadingState label="Loading product…" />;
  if (error) return <ErrorState message={error} />;
  if (!product) return <EmptyState title="Product not found" />;

  return (
    <div className="flex flex-col gap-6">
      <div>
        {product.category && (
          <Link
            href={`/categories/${encodeURIComponent(product.category)}`}
            className="mb-2 flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            <ChevronLeft className="h-4 w-4" /> {product.category}
          </Link>
        )}
        <h1 className="text-2xl font-semibold">{product.product_name}</h1>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card>
          <CardTitle>Reviews</CardTitle>
          <CardValue>{product.review_count}</CardValue>
        </Card>
        <Card>
          <CardTitle>Average rating</CardTitle>
          <CardValue>{product.avg_rating ?? "—"}★</CardValue>
        </Card>
        <Card>
          <CardTitle>Average price</CardTitle>
          <CardValue>{product.avg_price ? `₹${product.avg_price.toLocaleString()}` : "—"}</CardValue>
        </Card>
        <Card>
          <CardTitle>Related issues</CardTitle>
          <CardValue>{product.related_themes.length}</CardValue>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardTitle>Sentiment breakdown</CardTitle>
          <div className="mt-3">
            <SentimentBar
              positive={product.sentiment_breakdown.positive ?? 0}
              neutral={product.sentiment_breakdown.neutral ?? 0}
              negative={product.sentiment_breakdown.negative ?? 0}
            />
          </div>
        </Card>
        <Card>
          <CardTitle>Rating distribution</CardTitle>
          <RatingDistributionChart distribution={product.rating_distribution} />
        </Card>
      </div>

      {product.related_themes.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold">Related issues (marketplace-wide patterns)</h2>
          <p className="mb-3 text-xs text-muted-foreground">
            This product&apos;s reviews contribute to these cross-product themes discovered across the catalog.
          </p>
          <div className="flex flex-col gap-2">
            {product.related_themes.map((t) => (
              <Link
                key={t.theme_id}
                href={`/issues/${datasetId}/${t.theme_id}`}
                className="flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3 hover:bg-muted"
              >
                <div className="flex items-center gap-3">
                  <SeverityBadge severity={t.severity} />
                  <span className="font-medium">{t.theme_name}</span>
                </div>
                <span className="text-sm text-muted-foreground">{t.mention_count} mentions</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {product.negative_reviews.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold">Lowest-rated reviews</h2>
          <div className="flex flex-col gap-2">
            {product.negative_reviews.map((text, i) => (
              <div key={i} className="rounded-lg border border-border bg-card px-4 py-3 text-sm">
                {text}
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-lg font-semibold">Representative reviews</h2>
        <div className="flex flex-col gap-2">
          {product.representative_reviews.map((text, i) => (
            <div key={i} className="rounded-lg border border-border bg-card px-4 py-3 text-sm">
              {text}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
