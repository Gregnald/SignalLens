import type {
  ActionReportResponse,
  Category,
  ChatResponse,
  Dataset,
  DatasetUploadResponse,
  DashboardData,
  IncidentDetail,
  IncidentSummary,
  IntegrityReport,
  ProcessStatus,
  ProductDetail,
  ProductSummary,
  ReviewDetail,
  ReviewListResponse,
  Theme,
  ThemeDetail,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(options?.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...options?.headers,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore - fall back to statusText
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string; token_type: string; email: string; full_name: string }>(
      "/api/auth/login",
      { method: "POST", body: JSON.stringify({ email, password }) }
    ),

  listDatasets: () => request<Dataset[]>("/api/datasets"),
  getDataset: (id: number) => request<Dataset>(`/api/datasets/${id}`),
  deleteDataset: (id: number) => request<{ deleted: boolean }>(`/api/datasets/${id}`, { method: "DELETE" }),

  uploadDataset: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<DatasetUploadResponse>("/api/datasets/upload", {
      method: "POST",
      body: formData,
    });
  },

  startProcessing: (id: number) =>
    request<ProcessStatus>(`/api/datasets/${id}/process`, { method: "POST" }),
  getProcessStatus: (id: number) => request<ProcessStatus>(`/api/datasets/${id}/process-status`),

  getDashboard: (datasetId: number) => request<DashboardData>(`/api/dashboard/${datasetId}`),

  listThemes: (datasetId: number, params?: { severity?: string }) => {
    const qs = params?.severity ? `?severity=${params.severity}` : "";
    return request<Theme[]>(`/api/themes/${datasetId}${qs}`);
  },
  getTheme: (datasetId: number, themeId: number) =>
    request<ThemeDetail>(`/api/themes/${datasetId}/${themeId}`),

  listIncidents: (datasetId: number) => request<IncidentSummary[]>(`/api/incidents/${datasetId}`),
  getIncident: (datasetId: number, incidentId: number) =>
    request<IncidentDetail>(`/api/incidents/${datasetId}/${incidentId}`),
  generateAction: (incidentId: number) =>
    request<ActionReportResponse>(`/api/incidents/${incidentId}/generate-action`, { method: "POST" }),

  listReviews: (
    datasetId: number,
    params?: { page?: number; page_size?: number; platform?: string; min_rating?: number }
  ) => {
    const search = new URLSearchParams();
    if (params?.page) search.set("page", String(params.page));
    if (params?.page_size) search.set("page_size", String(params.page_size));
    if (params?.platform) search.set("platform", params.platform);
    if (params?.min_rating) search.set("min_rating", String(params.min_rating));
    const qs = search.toString() ? `?${search.toString()}` : "";
    return request<ReviewListResponse>(`/api/reviews/${datasetId}${qs}`);
  },
  getReview: (datasetId: number, reviewId: number) =>
    request<ReviewDetail>(`/api/reviews/${datasetId}/${reviewId}`),

  getIntegrity: (datasetId: number) => request<IntegrityReport>(`/api/integrity/${datasetId}`),

  chat: (datasetId: number, question: string) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ dataset_id: datasetId, question }),
    }),

  listCategories: (datasetId: number) => request<Category[]>(`/api/products/${datasetId}/categories`),
  listProducts: (datasetId: number, category?: string) => {
    const qs = category ? `?category=${encodeURIComponent(category)}` : "";
    return request<ProductSummary[]>(`/api/products/${datasetId}${qs}`);
  },
  getProduct: (datasetId: number, productName: string) =>
    request<ProductDetail>(`/api/products/${datasetId}/detail?product_name=${encodeURIComponent(productName)}`),
};
