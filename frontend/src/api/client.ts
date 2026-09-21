import type {
  User,
  UserRole,
  ServiceCategory,
  Institution,
  Report,
  ReportPublicStatus,
  Incident,
  ModerationQueueItem,
  AuditEvent,
  ReportStatus,
  IncidentStatus,
  Notification,
  MediaAsset,
  ResolutionEvidence,
} from "../types";

// Base URL comes from the environment so the same build can point at a
// staging/demo API; the fallback matches the local uvicorn default.
export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, "") ||
  "http://localhost:8000/api/v1";

/** Origin of the API (scheme + host), for absolute media URLs. */
export const API_ORIGIN = new URL(API_BASE_URL).origin;

/** Media URLs from the API are relative and already carry a signed token. */
export const mediaUrl = (asset: MediaAsset): string | undefined =>
  asset.url ? `${API_ORIGIN}${asset.url}` : undefined;

export class ApiError extends Error {
  status: number;
  errorCode: string;
  details: Record<string, unknown>;
  requestId?: string;

  constructor(status: number, body: Partial<{ error_code: string; message: string; details: Record<string, unknown>; request_id: string }>) {
    super(body.message || `Request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.errorCode = body.error_code || "UNKNOWN";
    this.details = body.details || {};
    this.requestId = body.request_id;
  }
}

const TOKEN_KEY = "salonefix_token";

let activeToken: string | null = null;
try {
  activeToken = localStorage.getItem(TOKEN_KEY);
} catch {
  activeToken = null;
}

export const setAuthToken = (token: string | null) => {
  activeToken = token;
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable (private mode) — session token still works in memory */
  }
};

export const getAuthToken = () => activeToken;

/** Random key for Idempotency-Key headers on retryable creates/uploads. */
export const newIdempotencyKey = (): string =>
  typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;

export interface Page<T> {
  items: T[];
  total: number;
}

async function rawRequest(endpoint: string, options: RequestInit = {}): Promise<Response> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (activeToken) {
    headers["Authorization"] = `Bearer ${activeToken}`;
  }

  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorData);
  }
  return response;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await rawRequest(endpoint, options);
  return response.json();
}

/** Paginated list: body is an array, total comes from X-Total-Count. */
async function requestPage<T>(endpoint: string, options: RequestInit = {}): Promise<Page<T>> {
  const response = await rawRequest(endpoint, options);
  const items = (await response.json()) as T[];
  const total = Number(response.headers.get("X-Total-Count") ?? items.length);
  return { items, total };
}

const qs = (params: Record<string, string | number | boolean | undefined | null>): string => {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "");
  if (!entries.length) return "";
  return "?" + entries.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join("&");
};

// Authentication
export const login = async (contact: string, password: string) => {
  const res = await request<{ access_token: string; user: User }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ contact, password }),
  });
  setAuthToken(res.access_token);
  return res;
};

export const register = async (data: { name_or_alias: string; contact: string; password: string; consent_status: boolean }) => {
  const res = await request<{ access_token: string; user: User }>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
  setAuthToken(res.access_token);
  return res;
};

export const getMe = () => request<User>("/auth/me");

export const logout = () => setAuthToken(null);

// Common
export const getCategories = () => request<ServiceCategory[]>("/categories");
export const getInstitutions = () => request<Institution[]>("/institutions");

// Reports
export const submitReport = (
  data: {
    category_code: string;
    description: string;
    latitude?: number | null;
    longitude?: number | null;
    location_precision?: string;
  },
  idempotencyKey: string = newIdempotencyKey()
) =>
  request<{ id: string; tracking_reference: string; status: ReportStatus; next_step: string }>("/reports", {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: JSON.stringify(data),
  });

export const uploadReportMedia = async (reportId: string, file: File, idempotencyKey: string = newIdempotencyKey()) => {
  const formData = new FormData();
  formData.append("file", file);
  return request<MediaAsset>(`/reports/${reportId}/media`, {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: formData,
  });
};

export const getPublicReportStatus = (referenceOrId: string) =>
  request<ReportPublicStatus>(`/reports/${encodeURIComponent(referenceOrId)}/status`);

export const listReports = (params: { status?: ReportStatus; limit?: number; offset?: number } = {}) =>
  requestPage<Report>(`/reports${qs(params)}`);

export const getReport = (reportId: string) => request<Report>(`/reports/${reportId}`);

// Moderation
export const getModerationQueue = (categoryCode?: string, page: { limit?: number; offset?: number } = {}) =>
  requestPage<ModerationQueueItem>(`/moderation/queue${qs({ category_code: categoryCode, ...page })}`);

export const submitModerationDecision = (reportId: string, decision: string, reason: string, targetIncidentId?: string) =>
  request<Report>(`/moderation/reports/${reportId}/decision`, {
    method: "POST",
    body: JSON.stringify({ decision, reason, target_incident_id: targetIncidentId }),
  });

// Incidents
export const getIncidents = (params: { status?: IncidentStatus; limit?: number; offset?: number } = {}) =>
  requestPage<Incident>(`/incidents${qs(params)}`);

export const getIncident = (id: string) => request<Incident>(`/incidents/${id}`);

export const createIncident = (data: { category_id: string; title: string; summary: string; priority: string; report_id?: string }) =>
  request<Incident>("/incidents", { method: "POST", body: JSON.stringify(data) });

export const linkReportToIncident = (incidentId: string, reportId: string, notes?: string) =>
  request<Incident>(`/incidents/${incidentId}/reports`, {
    method: "POST",
    body: JSON.stringify({ report_id: reportId, notes }),
  });

export const updateIncidentStatus = (incidentId: string, status: IncidentStatus, reason: string) =>
  request<Incident>(`/incidents/${incidentId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status, reason }),
  });

// Assignments
export const assignIncident = (incidentId: string, institutionId: string, officerId?: string, dueAt?: string) =>
  request(`/incidents/${incidentId}/assignments`, {
    method: "POST",
    body: JSON.stringify({ institution_id: institutionId, officer_id: officerId, due_at: dueAt }),
  });

export const updateAssignmentStatus = (assignmentId: string, status: "ACCEPTED" | "DECLINED", declineReason?: string) =>
  request(`/assignments/${assignmentId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status, decline_reason: declineReason }),
  });

// Resolution & Disputes
export const submitResolutionEvidence = (incidentId: string, description: string) =>
  request<ResolutionEvidence>(`/incidents/${incidentId}/resolution-evidence`, {
    method: "POST",
    body: JSON.stringify({ description }),
  });

export const uploadEvidenceMedia = (incidentId: string, evidenceId: string, file: File, idempotencyKey: string = newIdempotencyKey()) => {
  const formData = new FormData();
  formData.append("file", file);
  return request<MediaAsset>(`/incidents/${incidentId}/resolution-evidence/${evidenceId}/media`, {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: formData,
  });
};

export const reviewResolutionEvidence = (incidentId: string, decision: "APPROVED" | "REJECTED", reason: string) =>
  request<Incident>(`/incidents/${incidentId}/resolution-review`, {
    method: "POST",
    body: JSON.stringify({ decision, reason }),
  });

export const disputeResolution = (incidentId: string, reason: string) =>
  request(`/incidents/${incidentId}/disputes`, { method: "POST", body: JSON.stringify({ reason }) });

export const reopenIncident = (incidentId: string, reason: string) =>
  request<Incident>(`/incidents/${incidentId}/reopen`, { method: "POST", body: JSON.stringify({ reason }) });

// Audit
export const getIncidentAudit = (incidentId: string) => request<AuditEvent[]>(`/incidents/${incidentId}/audit`);
export const getAllAuditEvents = (params: { entity_type?: string; action?: string; limit?: number; offset?: number } = {}) =>
  requestPage<AuditEvent>(`/events${qs(params)}`);

// Notifications
export const getNotifications = (unreadOnly = false, page: { limit?: number; offset?: number } = {}) =>
  requestPage<Notification>(`/notifications${qs({ unread_only: unreadOnly || undefined, ...page })}`);

export const markNotificationRead = (notificationId: string) =>
  request<Notification>(`/notifications/${notificationId}/read`, { method: "PATCH" });

// Admin
export const adminListUsers = (params: { role?: UserRole; include_inactive?: boolean; limit?: number; offset?: number } = {}) =>
  requestPage<User>(`/admin/users${qs(params)}`);

export const adminCreateStaffUser = (data: { name_or_alias: string; contact: string; password: string; role: UserRole; institution_id?: string | null }) =>
  request<User>("/admin/users", { method: "POST", body: JSON.stringify(data) });

export const adminUpdateUser = (userId: string, data: { is_active?: boolean; role?: UserRole; institution_id?: string | null; reason: string }) =>
  request<User>(`/admin/users/${userId}`, { method: "PATCH", body: JSON.stringify(data) });

export const adminCreateInstitution = (data: { name: string; description?: string; service_area: string; contact_channel?: string }) =>
  request<Institution>("/admin/institutions", { method: "POST", body: JSON.stringify(data) });

export const adminUpdateInstitution = (institutionId: string, data: { description?: string; service_area?: string; contact_channel?: string; is_active?: boolean }) =>
  request<Institution>(`/admin/institutions/${institutionId}`, { method: "PATCH", body: JSON.stringify(data) });
