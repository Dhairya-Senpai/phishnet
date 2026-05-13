import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": import.meta.env.VITE_API_KEY ?? "change-me",
  },
});

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Campaign {
  id: string;
  name: string;
  description?: string;
  target?: string;
  created_at: string;
  email_count: number;
}

export interface EmailSummary {
  id: string;
  sender?: string;
  recipient?: string;
  subject?: string;
  delivery_status: string;
  received_at: string;
  threat_score?: number;
  spf_result?: string;
  dkim_result?: string;
  dmarc_result?: string;
}

export interface EmailDetail extends EmailSummary {
  campaign_id?: string;
  message_id?: string;
  raw_headers?: Record<string, string>;
  raw_body?: string;
  relay_path?: Array<{ ip?: string; by?: string; raw: string }>;
  bypass_indicators?: string[];
  analysis_notes?: string;
  analyzed_at?: string;
  links: Array<{
    id: string;
    url: string;
    domain?: string;
    is_redirect: boolean;
    anchor_text?: string;
  }>;
}

export interface OverviewStats {
  total_emails: number;
  total_campaigns: number;
  delivery: { total: number; delivered: number; bounced: number; rejected: number; quarantined: number };
  auth: { spf_pass: number; spf_fail: number; dkim_pass: number; dkim_fail: number; dmarc_pass: number; dmarc_fail: number };
  avg_threat_score?: number;
  recent_bypass_count: number;
}

// ── API calls ─────────────────────────────────────────────────────────────────

export const campaignApi = {
  list: () => api.get<Campaign[]>("/campaigns").then(r => r.data),
  create: (data: { name: string; description?: string; target?: string }) =>
    api.post<Campaign>("/campaigns", data).then(r => r.data),
  delete: (id: string) => api.delete(`/campaigns/${id}`),
};

export const emailApi = {
  list: (params?: { campaign_id?: string; min_threat_score?: number; limit?: number }) =>
    api.get<EmailSummary[]>("/emails", { params }).then(r => r.data),
  get: (id: string) => api.get<EmailDetail>(`/emails/${id}`).then(r => r.data),
  ingest: (raw_email: string, campaign_id?: string) =>
    api.post<EmailDetail>("/emails/ingest", { raw_email, campaign_id }).then(r => r.data),
  delete: (id: string) => api.delete(`/emails/${id}`),
};

export const analyticsApi = {
  overview: () => api.get<OverviewStats>("/analytics/overview").then(r => r.data),
  threatDistribution: (campaign_id?: string) =>
    api.get<Array<{ range: string; count: number }>>("/analytics/threat-distribution", { params: { campaign_id } }).then(r => r.data),
  authTimeline: (days = 30) =>
    api.get<Array<{ date: string; spf_pass: number; spf_fail: number }>>("/analytics/auth-timeline", { params: { days } }).then(r => r.data),
  bypassIndicators: () =>
    api.get<Array<{ indicator: string; count: number }>>("/analytics/bypass-indicators").then(r => r.data),
};

export default api;
