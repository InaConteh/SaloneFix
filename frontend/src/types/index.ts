export type UserRole = "CITIZEN" | "MODERATOR" | "OFFICER" | "ADMIN" | "AUDITOR";

export type ReportStatus =
  | "SUBMITTED"
  | "UNDER_REVIEW"
  | "NEEDS_CLARIFICATION"
  | "VERIFIED"
  | "MERGED"
  | "REJECTED"
  | "ESCALATED";

export type IncidentStatus =
  | "VERIFIED"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "RESOLUTION_UNDER_REVIEW"
  | "RESOLVED"
  | "DISPUTED"
  | "ESCALATED"
  | "CLOSED";

export type AssignmentStatus = "ASSIGNED" | "ACCEPTED" | "DECLINED";

export type LocationPrecision = "EXACT" | "APPROXIMATE" | "USER_ENTERED" | "UNAVAILABLE";

export interface User {
  id: string;
  role: UserRole;
  name_or_alias: string;
  contact: string;
  institution_id?: string | null;
  institution_name?: string | null;
  is_active?: boolean;
  created_at: string;
}

export interface ServiceCategory {
  id: string;
  code: string;
  name: string;
  description?: string;
  requires_resolution_evidence: boolean;
  is_active: boolean;
}

export interface Institution {
  id: string;
  name: string;
  description?: string;
  service_area: string;
  contact_channel?: string;
  is_active: boolean;
}

export interface MediaAsset {
  id: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  created_at: string;
  url?: string;
}

export interface Report {
  id: string;
  tracking_reference: string;
  reporter_id: string;
  category_id: string;
  category_code?: string;
  category_name?: string;
  description: string;
  latitude?: number | null;
  longitude?: number | null;
  location_precision: LocationPrecision;
  submitted_at: string;
  current_status: ReportStatus;
  source_channel: string;
  clarification_notes?: string | null;
  media_assets: MediaAsset[];
  incident_id?: string | null;
}

export interface ReportPublicStatus {
  tracking_reference: string;
  current_status: ReportStatus;
  category_name: string;
  description: string;
  submitted_at: string;
  last_update: string;
  next_step: string;
  responsible_institution?: string | null;
  can_dispute: boolean;
  incident_id?: string | null;
  resolution_description?: string | null;
}

export interface Incident {
  id: string;
  category_id: string;
  category_name?: string;
  title: string;
  summary: string;
  priority: "LOW" | "MEDIUM" | "HIGH" | "URGENT";
  lifecycle_status: IncidentStatus;
  centroid_latitude?: number | null;
  centroid_longitude?: number | null;
  created_at: string;
  updated_at: string;
  closed_at?: string | null;
  linked_reports_count: number;
  linked_reports?: {
    link_id: string;
    linked_at: string;
    notes?: string | null;
    report: Report;
  }[];
  assigned_institution_name?: string | null;
  active_assignment?: {
    id: string;
    institution_id: string;
    institution_name?: string | null;
    officer_id?: string | null;
    officer_name?: string | null;
    status: AssignmentStatus;
    due_at?: string | null;
    accepted_at?: string | null;
    declined_at?: string | null;
    is_overdue?: boolean;
  } | null;
  requires_resolution_evidence?: boolean;
  resolution_evidence?: ResolutionEvidence[];
  disputes?: Dispute[];
}

export type EvidenceReviewStatus = "PENDING" | "APPROVED" | "REJECTED";
export type DisputeStatus = "SUBMITTED" | "UNDER_REVIEW" | "ACCEPTED" | "REJECTED";

export interface ResolutionEvidence {
  id: string;
  incident_id: string;
  uploader_id: string;
  uploader_name?: string | null;
  description: string;
  submitted_at: string;
  review_status: EvidenceReviewStatus;
  reviewer_id?: string | null;
  review_reason?: string | null;
  reviewed_at?: string | null;
  media_assets: MediaAsset[];
}

export interface Dispute {
  id: string;
  incident_id: string;
  reporter_id: string;
  reason: string;
  status: DisputeStatus;
  created_at: string;
  resolved_at?: string | null;
}

export interface ModerationQueueItem {
  report: Report;
  nearby_reports: Report[];
}

export interface AuditEvent {
  id: string;
  actor_id?: string | null;
  actor_name?: string | null;
  actor_role?: string | null;
  entity_type: string;
  entity_id: string;
  action: string;
  previous_value?: string | null;
  new_value?: string | null;
  reason?: string | null;
  request_id?: string | null;
  created_at: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  entity_type?: string | null;
  entity_id?: string | null;
  is_read: boolean;
  created_at: string;
}
