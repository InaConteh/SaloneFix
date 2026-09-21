import React, { useState, useEffect, useCallback } from "react";
import {
  Briefcase,
  CheckCircle2,
  MapPin,
  FileCheck,
  Send,
  XCircle,
  AlertTriangle,
  Camera,
  Clock,
  ImagePlus,
} from "lucide-react";
import type { Incident, ResolutionEvidence, User } from "../types";
import {
  getIncidents,
  updateAssignmentStatus,
  submitResolutionEvidence,
  uploadEvidenceMedia,
  updateIncidentStatus,
  mediaUrl,
  ApiError,
} from "../api/client";
import { StatusBadge } from "../components/StatusBadge";

interface Props {
  currentUser: User;
}

const describeError = (err: unknown, fallback: string) =>
  err instanceof ApiError ? err.message : err instanceof Error ? err.message : fallback;

export const OfficerView: React.FC<Props> = ({ currentUser }) => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  // Modals
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [showDeclineModal, setShowDeclineModal] = useState(false);
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [evidenceDescription, setEvidenceDescription] = useState("");
  const [evidenceFiles, setEvidenceFiles] = useState<File[]>([]);
  const [declineReason, setDeclineReason] = useState("");
  const [escalateReason, setEscalateReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [attachingTo, setAttachingTo] = useState<string | null>(null);

  const selectedIncident = incidents.find((i) => i.id === selectedId) ?? null;

  const load = useCallback(async () => {
    try {
      const { items } = await getIncidents({ limit: 100 });
      setIncidents(items);
      setSelectedId((current) => current && items.some((i) => i.id === current) ? current : items[0]?.id ?? null);
      setError(null);
    } catch (err) {
      setError(describeError(err, "Could not load assigned cases."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const refresh = () => {
    setLoading(true);
    void load();
  };

  const flash = (msg: string) => {
    setActionMessage(msg);
    setTimeout(() => setActionMessage(null), 4000);
  };

  const handleAcceptAssignment = async () => {
    if (!selectedIncident?.active_assignment) return;
    setSubmitting(true);
    try {
      await updateAssignmentStatus(selectedIncident.active_assignment.id, "ACCEPTED");
      flash("Assignment accepted. Incident moved to IN_PROGRESS.");
      await load();
    } catch (err) {
      setError(describeError(err, "Failed to accept assignment."));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeclineAssignment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIncident?.active_assignment || !declineReason.trim()) return;
    setSubmitting(true);
    try {
      await updateAssignmentStatus(selectedIncident.active_assignment.id, "DECLINED", declineReason.trim());
      setShowDeclineModal(false);
      setDeclineReason("");
      flash("Assignment declined and returned for reassignment review.");
      await load();
    } catch (err) {
      setError(describeError(err, "Failed to decline assignment."));
    } finally {
      setSubmitting(false);
    }
  };

  const handleEscalate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIncident || !escalateReason.trim()) return;
    setSubmitting(true);
    try {
      await updateIncidentStatus(selectedIncident.id, "ESCALATED", escalateReason.trim());
      setShowEscalateModal(false);
      setEscalateReason("");
      flash("Incident escalated. Moderators have been notified.");
      await load();
    } catch (err) {
      setError(describeError(err, "Failed to escalate incident."));
    } finally {
      setSubmitting(false);
    }
  };

  const uploadFiles = async (incidentId: string, evidenceId: string, files: File[]) => {
    let failures = 0;
    for (const file of files) {
      try {
        await uploadEvidenceMedia(incidentId, evidenceId, file);
      } catch (err) {
        failures += 1;
        setError(`Photo "${file.name}" was rejected: ${describeError(err, "invalid image")}`);
      }
    }
    return failures;
  };

  const handleSubmitEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIncident || !evidenceDescription.trim()) return;
    const needsPhoto = selectedIncident.requires_resolution_evidence !== false;
    if (needsPhoto && evidenceFiles.length === 0) {
      setError("This category requires at least one photo of the completed work before it can be approved.");
      return;
    }
    setSubmitting(true);
    try {
      const evidence = await submitResolutionEvidence(selectedIncident.id, evidenceDescription.trim());
      const failures = await uploadFiles(selectedIncident.id, evidence.id, evidenceFiles);
      setShowEvidenceModal(false);
      setEvidenceDescription("");
      setEvidenceFiles([]);
      flash(
        failures
          ? `Evidence submitted, but ${failures} photo(s) were rejected. Attach a valid image below.`
          : "Resolution evidence and photos submitted for moderator verification."
      );
      await load();
    } catch (err) {
      setError(describeError(err, "Failed to submit resolution evidence."));
    } finally {
      setSubmitting(false);
    }
  };

  const handleAttachMore = async (evidence: ResolutionEvidence, files: FileList | null) => {
    if (!files || !selectedIncident) return;
    setAttachingTo(evidence.id);
    try {
      const failures = await uploadFiles(selectedIncident.id, evidence.id, Array.from(files));
      if (!failures) flash("Photo attached to evidence record.");
      await load();
    } finally {
      setAttachingTo(null);
    }
  };

  const overdue = selectedIncident?.active_assignment?.is_overdue;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Briefcase size={22} color="var(--color-primary)" aria-hidden="true" />
            <h2 style={{ fontSize: "1.4rem", fontWeight: 700, color: "var(--color-text)" }}>
              Institutional Operations Workspace
            </h2>
          </div>
          <p style={{ fontSize: "0.85rem", color: "var(--color-text-muted)", marginTop: "2px" }}>
            {currentUser.institution_name ?? "Your institution"} • Field assignment dispatch &amp; resolution evidence
          </p>
        </div>
        <button type="button" className="btn-secondary btn-sm" onClick={refresh} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh assigned cases"}
        </button>
      </div>

      {actionMessage && (
        <div role="status" style={{
          backgroundColor: "var(--color-success-bg)", color: "var(--color-success)",
          padding: "10px 16px", borderRadius: "var(--radius-md)", fontWeight: 600,
          display: "flex", alignItems: "center", gap: "8px",
        }}>
          <CheckCircle2 size={16} aria-hidden="true" />
          <span>{actionMessage}</span>
        </div>
      )}
      {error && (
        <div role="alert" style={{
          backgroundColor: "var(--color-danger-bg)", color: "var(--color-danger)",
          padding: "10px 16px", borderRadius: "var(--radius-md)", fontWeight: 600,
          display: "flex", alignItems: "center", justifyContent: "space-between", gap: "8px",
        }}>
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}><AlertTriangle size={16} aria-hidden="true" /> {error}</span>
          <button type="button" className="btn-sm btn-secondary" onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "minmax(280px, 1fr) 2fr", gap: "20px" }}>
        {/* Left: case list */}
        <div className="card" style={{ padding: "16px", display: "flex", flexDirection: "column", gap: "10px" }}>
          <div style={{ fontWeight: 700, fontSize: "0.9rem", color: "var(--color-text-muted)" }}>
            ASSIGNED CASES ({incidents.length})
          </div>

          {incidents.length === 0 ? (
            <div style={{ padding: "24px 12px", textAlign: "center", color: "var(--color-text-muted)", fontSize: "0.85rem" }}>
              {loading ? "Loading…" : "No incidents currently assigned to your institution."}
            </div>
          ) : (
            incidents.map((inc) => (
              <button
                type="button"
                key={inc.id}
                onClick={() => setSelectedId(inc.id)}
                aria-pressed={selectedId === inc.id}
                style={{
                  textAlign: "left", width: "100%", padding: "12px", borderRadius: "var(--radius-md)",
                  border: selectedId === inc.id ? "2px solid var(--color-primary)" : "1px solid var(--color-border)",
                  backgroundColor: selectedId === inc.id ? "var(--color-primary-light)" : "#ffffff",
                  cursor: "pointer", font: "inherit",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px", gap: 8 }}>
                  <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--color-text-muted)" }}>
                    PRIORITY: {inc.priority}
                  </span>
                  <StatusBadge status={inc.lifecycle_status} />
                </div>
                <div style={{ fontWeight: 600, fontSize: "0.9rem", color: "var(--color-text)" }}>{inc.title}</div>
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "4px", display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <span>{inc.linked_reports_count} citizen report(s)</span>
                  {inc.active_assignment?.is_overdue && (
                    <span style={{ color: "var(--color-danger)", fontWeight: 700 }}>OVERDUE</span>
                  )}
                </div>
              </button>
            ))
          )}
        </div>

        {/* Right: detail */}
        {selectedIncident ? (
          <div className="card" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "10px" }}>
              <div>
                <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>CASE IDENTIFIER: {selectedIncident.id}</span>
                <h3 style={{ fontSize: "1.3rem", fontWeight: 800, color: "var(--color-text)", marginTop: "2px" }}>
                  {selectedIncident.title}
                </h3>
              </div>
              <StatusBadge status={selectedIncident.lifecycle_status} />
            </div>

            {overdue && (
              <div role="alert" style={{
                display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", borderRadius: "var(--radius-md)",
                backgroundColor: "var(--color-danger-bg)", color: "var(--color-danger)", fontSize: "0.85rem", fontWeight: 600,
              }}>
                <Clock size={16} aria-hidden="true" />
                Past due date ({new Date(selectedIncident.active_assignment!.due_at!).toLocaleDateString()}). Please update or escalate.
              </div>
            )}

            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Work order summary</span>
              <div style={{
                backgroundColor: "var(--color-surface)", padding: "12px", borderRadius: "var(--radius-md)",
                border: "1px solid var(--color-border)", fontSize: "0.875rem", marginTop: "4px", lineHeight: 1.5,
              }}>
                {selectedIncident.summary}
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Location</span>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", marginTop: "2px" }}>
                  <MapPin size={16} color="var(--color-primary)" aria-hidden="true" />
                  <span>
                    {selectedIncident.centroid_latitude && selectedIncident.centroid_longitude
                      ? `Lat ${selectedIncident.centroid_latitude.toFixed(4)}, Lon ${selectedIncident.centroid_longitude.toFixed(4)}`
                      : "General municipality area"}
                  </span>
                </div>
              </div>
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Due</span>
                <div style={{ fontSize: "0.85rem", marginTop: "2px" }}>
                  {selectedIncident.active_assignment?.due_at
                    ? new Date(selectedIncident.active_assignment.due_at).toLocaleString()
                    : "No due date set"}
                </div>
              </div>
            </div>

            {/* Linked reports with citizen photos */}
            <div>
              <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--color-text)" }}>
                Linked citizen reports ({selectedIncident.linked_reports?.length || 0})
              </span>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "6px" }}>
                {selectedIncident.linked_reports?.map((lr) => (
                  <div key={lr.link_id} style={{
                    backgroundColor: "var(--color-surface)", padding: "10px", borderRadius: "var(--radius-md)",
                    border: "1px solid var(--color-border)", fontSize: "0.85rem",
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px", gap: 8 }}>
                      <strong>{lr.report.tracking_reference}</strong>
                      <StatusBadge status={lr.report.current_status} />
                    </div>
                    <p style={{ margin: "2px 0", color: "var(--color-text)" }}>{lr.report.description}</p>
                    {lr.report.media_assets?.length > 0 && (
                      <div style={{ display: "flex", gap: 8, marginTop: 8, flexWrap: "wrap" }}>
                        {lr.report.media_assets.map((m) => (
                          <img key={m.id} src={mediaUrl(m)} alt={`Citizen photo ${m.original_filename}`}
                               style={{ width: 96, height: 72, objectFit: "cover", borderRadius: 6, border: "1px solid var(--color-border)" }} />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Resolution evidence records */}
            <div>
              <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--color-text)" }}>
                Resolution evidence ({selectedIncident.resolution_evidence?.length || 0})
              </span>
              {selectedIncident.requires_resolution_evidence !== false && (
                <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: 2 }}>
                  This category requires at least one photo of the completed work before a moderator can approve resolution.
                </p>
              )}
              <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "6px" }}>
                {selectedIncident.resolution_evidence?.map((ev) => (
                  <div key={ev.id} style={{
                    padding: "10px", borderRadius: "var(--radius-md)", fontSize: "0.85rem",
                    border: `1px solid ${ev.review_status === "REJECTED" ? "var(--color-danger)" : "var(--color-border)"}`,
                    backgroundColor: "#fff",
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
                      <span style={{ color: "var(--color-text-muted)", fontSize: "0.75rem" }}>
                        {new Date(ev.submitted_at).toLocaleString()} · {ev.uploader_name ?? "Officer"}
                      </span>
                      <span className="badge" style={{
                        backgroundColor: ev.review_status === "APPROVED" ? "var(--status-resolved-bg)" : ev.review_status === "REJECTED" ? "var(--status-disputed-bg)" : "var(--status-review-bg)",
                        color: ev.review_status === "APPROVED" ? "var(--status-resolved)" : ev.review_status === "REJECTED" ? "var(--status-disputed)" : "var(--status-review)",
                      }}>
                        {ev.review_status}
                      </span>
                    </div>
                    <p style={{ margin: "6px 0" }}>{ev.description}</p>
                    {ev.review_reason && (
                      <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>Reviewer: {ev.review_reason}</p>
                    )}
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", marginTop: 6 }}>
                      {ev.media_assets.map((m) => (
                        <img key={m.id} src={mediaUrl(m)} alt={`Evidence photo ${m.original_filename}`}
                             style={{ width: 96, height: 72, objectFit: "cover", borderRadius: 6, border: "1px solid var(--color-border)" }} />
                      ))}
                      {ev.media_assets.length === 0 && (
                        <span style={{ fontSize: "0.75rem", color: "var(--color-warning)", fontWeight: 600 }}>No photo attached yet</span>
                      )}
                      {ev.review_status === "PENDING" && ev.uploader_id === currentUser.id && (
                        <label className="btn-sm btn-secondary" style={{ cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 4 }}>
                          <ImagePlus size={14} aria-hidden="true" />
                          {attachingTo === ev.id ? "Uploading…" : "Attach photo"}
                          <input type="file" accept="image/jpeg,image/png,image/webp" multiple style={{ display: "none" }}
                                 disabled={attachingTo === ev.id}
                                 onChange={(e) => { void handleAttachMore(ev, e.target.files); e.target.value = ""; }} />
                        </label>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div style={{ marginTop: "12px", borderTop: "1px solid var(--color-border)", paddingTop: "16px", display: "flex", gap: "10px", flexWrap: "wrap" }}>
              {selectedIncident.lifecycle_status === "ASSIGNED" && (
                <>
                  <button type="button" className="btn-primary" onClick={handleAcceptAssignment}
                          disabled={submitting || !selectedIncident.active_assignment}>
                    <CheckCircle2 size={16} aria-hidden="true" />
                    <span>Accept assignment &amp; start work</span>
                  </button>
                  <button type="button" className="btn-danger" onClick={() => setShowDeclineModal(true)}
                          disabled={submitting || !selectedIncident.active_assignment}>
                    <XCircle size={16} aria-hidden="true" />
                    <span>Decline assignment</span>
                  </button>
                </>
              )}

              {(selectedIncident.lifecycle_status === "IN_PROGRESS" || selectedIncident.lifecycle_status === "RESOLUTION_UNDER_REVIEW") && (
                <button type="button" className="btn-primary" onClick={() => setShowEvidenceModal(true)} disabled={submitting}>
                  <FileCheck size={16} aria-hidden="true" />
                  <span>Submit completion evidence</span>
                </button>
              )}

              {(selectedIncident.lifecycle_status === "ASSIGNED" || selectedIncident.lifecycle_status === "IN_PROGRESS") && (
                <button type="button" className="btn-secondary" onClick={() => setShowEscalateModal(true)} disabled={submitting}>
                  <AlertTriangle size={16} aria-hidden="true" />
                  <span>Escalate</span>
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="card" style={{ textAlign: "center", padding: "48px 24px", color: "var(--color-text-muted)" }}>
            Select an incident from the left to view operational details and manage field execution.
          </div>
        )}
      </div>

      {/* Evidence modal */}
      {showEvidenceModal && selectedIncident && (
        <div className="modal-overlay">
          <div className="modal-content" role="dialog" aria-modal="true" aria-labelledby="evidence-title">
            <h3 id="evidence-title" style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "8px" }}>Submit resolution evidence</h3>
            <p style={{ fontSize: "0.85rem", color: "var(--color-text-muted)", marginBottom: "16px" }}>
              Describe the completed work and attach photos of the site after repair. Camera metadata is stripped automatically.
            </p>

            <form onSubmit={handleSubmitEvidence} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <label className="input-label" htmlFor="evidence-desc">Work completion report</label>
                <textarea id="evidence-desc" className="input-field" rows={4} required minLength={10}
                          placeholder="Materials used, equipment deployed, compaction/clearance performed, final site safety inspection…"
                          value={evidenceDescription} onChange={(e) => setEvidenceDescription(e.target.value)} />
              </div>
              <div>
                <label className="input-label" htmlFor="evidence-files">
                  After-repair photos {selectedIncident.requires_resolution_evidence !== false ? "(required)" : "(optional)"}
                </label>
                <input id="evidence-files" type="file" accept="image/jpeg,image/png,image/webp" multiple className="input-field"
                       onChange={(e) => setEvidenceFiles(Array.from(e.target.files ?? []))} />
                {evidenceFiles.length > 0 && (
                  <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: 4, display: "flex", alignItems: "center", gap: 4 }}>
                    <Camera size={12} aria-hidden="true" /> {evidenceFiles.length} photo(s) selected — JPEG/PNG/WEBP up to 10 MB each
                  </p>
                )}
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "8px" }}>
                <button type="button" className="btn-secondary" onClick={() => setShowEvidenceModal(false)} disabled={submitting}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={submitting || !evidenceDescription.trim()}>
                  <Send size={14} aria-hidden="true" />
                  <span>{submitting ? "Submitting…" : "Submit proof of work"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Decline modal */}
      {showDeclineModal && selectedIncident && (
        <div className="modal-overlay">
          <div className="modal-content" role="dialog" aria-modal="true" aria-labelledby="decline-title">
            <h3 id="decline-title" style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "8px" }}>Decline assignment</h3>
            <p style={{ fontSize: "0.85rem", color: "var(--color-text-muted)", marginBottom: "16px" }}>
              A reason is required so moderators can reassign the case without losing accountability.
            </p>
            <form onSubmit={handleDeclineAssignment} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <label className="input-label" htmlFor="decline-reason">Decline reason</label>
                <textarea id="decline-reason" className="input-field" rows={4} required minLength={5}
                          placeholder="Jurisdiction, capacity, duplicate work order…"
                          value={declineReason} onChange={(e) => setDeclineReason(e.target.value)} />
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "8px" }}>
                <button type="button" className="btn-secondary" onClick={() => setShowDeclineModal(false)} disabled={submitting}>Cancel</button>
                <button type="submit" className="btn-danger" disabled={submitting || !declineReason.trim()}>
                  <XCircle size={14} aria-hidden="true" />
                  <span>{submitting ? "Declining…" : "Decline assignment"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Escalate modal */}
      {showEscalateModal && selectedIncident && (
        <div className="modal-overlay">
          <div className="modal-content" role="dialog" aria-modal="true" aria-labelledby="escalate-title">
            <h3 id="escalate-title" style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "8px" }}>Escalate incident</h3>
            <p style={{ fontSize: "0.85rem", color: "var(--color-text-muted)", marginBottom: "16px" }}>
              Use when the work is blocked (budget, access, safety, another institution&apos;s jurisdiction). Moderators are notified.
            </p>
            <form onSubmit={handleEscalate} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <label className="input-label" htmlFor="escalate-reason">Escalation reason</label>
                <textarea id="escalate-reason" className="input-field" rows={4} required minLength={5}
                          value={escalateReason} onChange={(e) => setEscalateReason(e.target.value)} />
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "8px" }}>
                <button type="button" className="btn-secondary" onClick={() => setShowEscalateModal(false)} disabled={submitting}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={submitting || !escalateReason.trim()}>
                  <AlertTriangle size={14} aria-hidden="true" />
                  <span>{submitting ? "Escalating…" : "Escalate"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
