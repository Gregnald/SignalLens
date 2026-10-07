"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ChevronLeft } from "lucide-react";

import { api, ApiError } from "@/lib/api";
import { useDataset } from "@/lib/dataset-context";
import type { ProductSummary } from "@/lib/types";
import { EmptyState, ErrorState, Skeleton } from "@/components/ui/states";

export default function CategoryProductsPage() {
  const params = useParams<{ category: string }>();
  const category = decodeURIComponent(params.category);
  const { datasetId } = useDataset();

  const [products, setProducts] = useState<ProductSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!datasetId) return;
    setLoading(true);
    api
      .listProducts(datasetId, category)
      .then(setProducts)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load products"))
      .finally(() => setLoading(false));
  }, [datasetId, category]);

  return (
    <div>
      <Link href="/categories" className="mb-4 flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ChevronLeft className="h-4 w-4" /> All categories
      </Link>
      <h1 className="mb-6 text-2xl font-semibold">{category}</h1>

      {loading && (
        <div className="flex flex-col gap-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      )}

      {error && <ErrorState message={error} />}

      {!loading && !error && products.length === 0 && <EmptyState title="No products in this category" />}

      {!loading && !error && products.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-2 text-left">Product</th>
                <th className="px-4 py-2 text-right">Reviews</th>
                <th className="px-4 py-2 text-right">Avg rating</th>
                <th className="px-4 py-2 text-right">Avg price</th>
                <th className="px-4 py-2 text-right">Negative %</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.product_name} className="border-t border-border hover:bg-muted">
                  <td className="px-4 py-3">
                    <Link href={`/products/${encodeURIComponent(p.product_name)}`} className="font-medium hover:underline">
                      {p.product_name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-right">{p.review_count}</td>
                  <td className="px-4 py-3 text-right">{p.avg_rating ?? "—"}★</td>
                  <td className="px-4 py-3 text-right">{p.avg_price ? `₹${p.avg_price.toLocaleString()}` : "—"}</td>
                  <td className="px-4 py-3 text-right">
                    <span className={p.negative_percent > 20 ? "font-semibold text-critical" : ""}>
                      {p.negative_percent}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
