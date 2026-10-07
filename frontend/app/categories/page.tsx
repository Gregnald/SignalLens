"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Layers } from "lucide-react";

import { api, ApiError } from "@/lib/api";
import { useDataset } from "@/lib/dataset-context";
import type { Category } from "@/lib/types";
import { Card, CardTitle, CardValue } from "@/components/ui/card";
import { EmptyState, ErrorState, Skeleton } from "@/components/ui/states";
import { CategoryVolumeChart } from "@/components/charts/category-volume-chart";

export default function CategoriesPage() {
  const { datasetId } = useDataset();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .listCategories(datasetId)
      .then(setCategories)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load categories"))
      .finally(() => setLoading(false));
  }, [datasetId]);

  if (!datasetId) return <EmptyState title="Catalog is still loading" description="Give the pipeline a moment and refresh." />;

  return (
    <div>
      <div className="mb-6 flex items-center gap-2">
        <Layers className="h-6 w-6" />
        <h1 className="text-2xl font-semibold">Product Categories</h1>
      </div>

      {loading && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      )}

      {error && <ErrorState message={error} />}

      {!loading && !error && categories.length === 0 && (
        <EmptyState
          title="No categorized products yet"
          description="The catalog may still be processing — check back shortly."
        />
      )}

      {!loading && !error && categories.length > 0 && (
        <>
          <Card className="mb-6">
            <CardTitle>Reviews by category</CardTitle>
            <div className="mt-2">
              <CategoryVolumeChart data={categories} />
            </div>
          </Card>

          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          {categories.map((c) => (
            <Link key={c.category} href={`/categories/${encodeURIComponent(c.category)}`}>
              <Card className="h-full transition-shadow hover:shadow-md">
                <CardTitle>{c.category}</CardTitle>
                <CardValue>{c.product_count}</CardValue>
                <p className="mt-1 text-xs text-muted-foreground">
                  {c.review_count.toLocaleString()} reviews · {c.avg_rating ?? "—"}★ avg
                </p>
              </Card>
            </Link>
          ))}
          </div>
        </>
      )}
    </div>
  );
}
