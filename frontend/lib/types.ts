export type Severity = "critical" | "high" | "medium" | "low";

export interface Dataset {
  id: number;
  name: string;
  source: string | null;
  file_name: string | null;
  total_reviews: number;
  status: "uploaded" | "processing" | "processed" | "failed";
  processing_error: string | null;
  created_at: string;
}

export interface DatasetUploadResponse {
  dataset: Dataset;
  columns_detected: Record<string, string | null>;
  rows_ingested: number;
  rows_skipped: number;
  warnings: string[];
}

export interface ProcessStatus {
  dataset_id: number;
  status: string;
  stage: string | null;
  progress_percent: number;
  error: string | null;
}

export interface WhatChangedItem {
  theme_id: number;
  theme_name: string;
  growth_percent: number;
  severity: Severity;
}

export interface TopIssueItem {
  theme_id: number;
  theme_name: string;
  impact_score: number;
  severity: Severity;
}

export interface IncidentSummary {
  id: number;
  dataset_id: number;
  theme_id: number;
  title: string;
  summary: string | null;
  severity: Severity;
  impact_score: number;
  first_detected_at: string | null;
  last_detected_at: string | null;
  growth_percent: number | null;
  likely_driver: string | null;
  root_cause_confidence: number | null;
  affected_platforms: Record<string, number> | null;
  affected_versions: Record<string, number> | null;
  affected_devices: Record<string, number> | null;
  recommended_owner: string | null;
  recommended_priority: string | null;
  status: string;
  created_at: string;
}

export interface Evidence {
  id: number;
  incident_id: number;
  review_id: number | null;
  feedback_unit_id: number | null;
  evidence_type: string;
  evidence_text: string;
  relevance_score: number | null;
}

export interface IncidentDetail extends IncidentSummary {
  evidence: Evidence[];
  rating_impact: number | null;
}

export interface DashboardData {
  dataset_id: number;
  total_reviews: number;
  average_rating: number | null;
  negative_percent: number;
  emerging_issues: number;
  critical_incidents: number;
  complaint_increase_multiplier: number | null;
  sentiment_breakdown: Record<string, number>;
  what_changed: WhatChangedItem[];
  top_issues: TopIssueItem[];
  recent_incidents: IncidentSummary[];
}

export interface Theme {
  id: number;
  dataset_id: number;
  name: string;
  category: string | null;
  description: string | null;
  volume: number;
  growth_percent: number | null;
  avg_sentiment: number | null;
  negative_percent: number | null;
  severity: Severity | null;
  impact_score: number | null;
  confidence: number | null;
  is_emerging: boolean;
  created_at: string;
  updated_at: string;
}

export interface ThemeTrendPoint {
  date: string;
  volume: number;
  avg_rating: number | null;
}

export interface ThemeDetail extends Theme {
  trend: ThemeTrendPoint[];
  affected_segments: Record<string, Record<string, number>>;
  representative_reviews: string[];
}

export interface ReviewSummary {
  id: number;
  dataset_id: number;
  raw_text: string;
  clean_text: string | null;
  rating: number | null;
  review_date: string | null;
  app_version: string | null;
  platform: string | null;
  device: string | null;
  country: string | null;
  source: string | null;
  product_name: string | null;
  product_category: string | null;
  product_price: number | null;
  is_duplicate: boolean;
  duplicate_group_id: number | null;
  integrity_risk: number;
  rating_text_conflict: boolean;
  created_at: string;
}

export interface ReviewListResponse {
  total: number;
  page: number;
  page_size: number;
  items: ReviewSummary[];
}

export interface FeedbackUnit {
  id: number;
  review_id: number;
  text: string;
  sentiment: string | null;
  sentiment_score: number | null;
  theme_id: number | null;
  confidence: number | null;
}

export interface ReviewDetail extends ReviewSummary {
  feedback_units: FeedbackUnit[];
}

export interface DuplicateGroup {
  duplicate_group_id: number;
  review_count: number;
  avg_similarity: number;
  sample_texts: string[];
}

export interface Burst {
  window_start: string;
  window_end: string;
  review_count: number;
  dominant_rating: number | null;
  sample_texts: string[];
}

export interface Conflict {
  review_id: number;
  rating: number | null;
  text: string;
}

export interface IntegrityReport {
  dataset_id: number;
  total_reviews: number;
  flagged_percent: number;
  duplicate_groups: DuplicateGroup[];
  bursts: Burst[];
  rating_text_conflicts: Conflict[];
}

export interface ActionReport {
  title: string;
  problem: string;
  impact: string;
  affected_users: string;
  likely_driver: string;
  representative_evidence_summary: string;
  severity: string;
  recommended_owner: string;
  priority: string;
  next_steps: string[];
}

export interface ActionReportResponse {
  incident_id: number;
  report: ActionReport;
  generated_by: string;
}

export interface ChatMetric {
  label: string;
  value: string;
}

export interface ChatResponse {
  answer: string;
  evidence_ids: number[];
  metrics: ChatMetric[];
  incident_ids: number[];
  generated_by: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  email: string;
  full_name: string;
}

export interface Category {
  category: string;
  product_count: number;
  review_count: number;
  avg_rating: number | null;
}

export interface ProductSummary {
  product_name: string;
  category: string | null;
  review_count: number;
  avg_rating: number | null;
  avg_price: number | null;
  negative_percent: number;
}

export interface ThemeMention {
  theme_id: number;
  theme_name: string;
  severity: Severity;
  mention_count: number;
}

export interface ProductDetail {
  product_name: string;
  category: string | null;
  review_count: number;
  avg_rating: number | null;
  avg_price: number | null;
  sentiment_breakdown: Record<string, number>;
  rating_distribution: Record<string, number>;
  representative_reviews: string[];
  negative_reviews: string[];
  related_themes: ThemeMention[];
}
