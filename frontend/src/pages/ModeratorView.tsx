import React, { useState, useEffect, useCallback } from "react";
import {
  CheckCircle,
  GitMerge,
  HelpCircle,
  XCircle,
  ShieldAlert,
  MapPin,
  Layers,
  Inbox,
  FolderKanban,
} from "lucide-react";
import type { ModerationQueueItem, Incident, Institution } from "../types";
import {
  getModerationQueue,
  submitModerationDecision,
  getIncidents,
  createIncident,
  getInstitutions,
  assignIncident,
  mediaUrl,
  ApiError,
} from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import { IncidentCasesPanel } from "../components/IncidentCasesPanel";

const describeError = (err: unknown, fallback: string) =>
  err instanceof ApiError ? err.message : err instanceof Error ? err.message : fallback;

export const ModeratorView: React.FC = () => {
  const [tab, setTab] = useState<"queue" | "cases">("queue");
  const [queue, setQueue] = useState<ModerationQueueItem[]>([]);
  const [queueTotal, setQueueTotal] = useState(0);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Decision State
  const [decisionReason, setDecisionReason] = useState("");
  const [selectedIncidentForMerge, setSelectedIncidentForMerge] = useState("");
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);

  // Create & Assign Incident Modal
  const [showCreateIncidentModal, setShowCreateIncidentModal] = useState(false);
  const [newIncidentTitle, setNewIncidentTitle] = useState("");
  const [newIncidentSummary, setNewIncidentSummary] = useState("");
  const [newIncidentPriority, setNewIncidentPriority] = useState<"LOW" | "MEDIUM" | "HIGH" | "URGENT">("HIGH");
  const [assignInstitutionId, setAssignInstitutionId] = useState("");

  const refreshData = useCallback(async () => {
    try {
      const [q, incs, insts] = await Promise.all([
        getModerationQueue(undefined, { limit: 100 }),
        getIncidents({ limit: 100 }),
        getInstitutions(),
      ]);
      setQueue(q.items);
      setQueueTotal(q.total);
      const open = incs.items.filter((i) => i.lifecycle_status !== "CLOSED");
      setIncidents(open);
      setInstitutions(insts);
      setAssignInstitutionId((cur) => cur || insts[0]?.id || "");
      setSelectedIncidentForMerge((cur) => (cur && open.some((i) => i.id === cur) ? cur : open[0]?.id || ""));
      setError(null);
    } catch (err) {
      setError(describeError(err, "Could not load the moderation queue."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshData();
  }, [refreshData]);

  const refresh = () => {
    setLoading(true);
    void refreshData();
  };

  const activeItem = queue[selectedIndex] || null;
  const activeReport = activeItem?.report || null;

  const handleDecision = async (decisionType: "VERIFY" | "MERGE" | "NEEDS_CLARIFICATION" | "REJECT" | "ESCALATE") => {
    if (!activeReport) return;
    if (!decisionReason.trim()) {
      setError("A human decision reason is mandatory for all moderation actions.");
      return;
    }

    if (decisionType === "MERGE" && !selectedIncidentForMerge) {
      setError("Please select a target incident to merge into.");
      return;
    }

    setLoading(true);
    try {
      await submitModerationDecision(
        activeReport.id,
        decisionType,
        decisionReason.trim(),
        decisionType === "MERGE" ? selectedIncidentForMerge : undefined
      );

      setActionSuccessMessage(`Decision ${decisionType} recorded successfully.`);
      setDecisionReason("");
      setTimeout(() => setActionSuccessMessage(null), 3000);
      await refreshData();
      if (selectedIndex >= queue.length - 1) {
        setSelectedIndex(Math.max(0, queue.length - 2));
      }
    } catch (err) {
      setError(describeError(err, "Failed to record decision."));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAndAssignIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeReport || !newIncidentTitle || !newIncidentSummary) return;

    setLoading(true);
    try {
      const inc = await createIncident({
        category_id: activeReport.category_id,
        title: newIncidentTitle,
        summary: newIncidentSummary,
        priority: newIncidentPriority,
        report_id: activeReport.id,
      });

      if (assignInstitutionId) {
        await assignIncident(inc.id, assignInstitutionId);
      }

      setShowCreateIncidentModal(false);
      setNewIncidentTitle("");
      setNewIncidentSummary("");
      setActionSuccessMessage(`Incident case created and assigned to institution.`);
      setTimeout(() => setActionSuccessMessage(null), 3000);
      await refreshData();
    } catch (err) {
      setError(describeError(err, "Failed to create and assign incident."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Header & tabs */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: 700, color: "var(--color-text)" }}>
            Moderation Workspace
          </h2>
          <p style={{ fontSize: "0.85rem", color: "var(--color-text-muted)" }}>
            Human review of citizen reports, incident cases, resolution evidence and disputes
          </p>
        </div>
        <div role="tablist" aria-label="Moderator workspace" style={{ display: "flex", gap: 6 }}>
          <button type="button" role="tab" aria-selected={tab === "queue"} className={`btn-sm ${tab === "queue" ? "btn-primary" : "btn-secondary"}`}
                  onClick={() => setTab("queue")} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <Inbox size={14} aria-hidden="true" /> Report queue ({queueTotal})
          </button>
          <button type="button" role="tab" aria-selected={tab === "cases"} className={`btn-sm ${tab === "cases" ? "btn-primary" : "btn-secondary"}`}
                  onClick={() => setTab("cases")} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <FolderKanban size={14} aria-hidden="true" /> Incident cases
          </button>
        </div>
      </div>

      {error && (
        <div role="alert" style={{
          backgroundColor: "var(--color-danger-bg)", color: "var(--color-danger)", padding: "10px 16px",
          borderRadius: "var(--radius-md)", fontWeight: 600, display: "flex", justifyContent: "space-between", gap: 8,
        }}>
          <span>{error}</span>
          <button type="button" className="btn-sm btn-secondary" onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      {tab === "cases" && <IncidentCasesPanel />}

      {tab === "queue" && (
      <>
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <button type="button" className="btn-secondary btn-sm" onClick={refresh} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh queue"}
        </button>
      </div>

      {actionSuccessMessage && (
        <div style={{
          backgroundColor: "var(--color-success-bg)",
          color: "var(--color-success)",
          padding: "10px 16px",
          borderRadius: "var(--radius-md)",
          fontWeight: 600,
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}>
          <CheckCircle size={16} />
          <span>{actionSuccessMessage}</span>
        </div>
      )}

      {/* Queue Item Selector Pills */}
      {queue.length > 0 && (
        <div style={{ display: "flex", gap: "8px", overflowX: "auto", paddingBottom: "6px" }}>
          {queue.map((item, idx) => (
            <button
              type="button"
              key={item.report.id}
              onClick={() => {
                setSelectedIndex(idx);
                setNewIncidentTitle(`${item.report.category_name || "Civic Hazard"}: ${item.report.description.slice(0, 40)}...`);
                setNewIncidentSummary(item.report.description);
              }}
              style={{
                backgroundColor: selectedIndex === idx ? "var(--color-primary)" : "#ffffff",
                color: selectedIndex === idx ? "#ffffff" : "var(--color-text)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-md)",
                padding: "8px 14px",
                whiteSpace: "nowrap",
                fontSize: "0.85rem",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <span>{item.report.tracking_reference}</span>
              <span style={{ fontSize: "0.75rem", opacity: 0.8 }}>({item.report.category_name})</span>
            </button>
          ))}
        </div>
      )}

      {!activeReport ? (
        <div className="card" style={{ textAlign: "center", padding: "48px 24px" }}>
          <CheckCircle size={40} color="var(--color-success)" style={{ margin: "0 auto 12px" }} />
          <h3 style={{ fontSize: "1.2rem", fontWeight: 700 }}>Moderation Queue Is Clear</h3>
          <p style={{ color: "var(--color-text-muted)", marginTop: "4px" }}>
            All citizen reports have been verified or resolved.
          </p>
        </div>
      ) : (
        /* Three-Column Moderator Workspace */
        <div className="moderator-grid">
          {/* Column 1: Original Evidence & Report Details */}
          <div className="card" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--color-text-muted)" }}>
                  COL 1: ORIGINAL CITIZEN EVIDENCE
                </span>
                <h3 style={{ fontSize: "1.2rem", fontWeight: 800, color: "var(--color-text)", marginTop: "2px" }}>
                  {activeReport.tracking_reference}
                </h3>
              </div>
              <StatusBadge status={activeReport.current_status} />
            </div>

            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Category</span>
              <div style={{ fontWeight: 600 }}>{activeReport.category_name}</div>
            </div>

            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Raw Description</span>
              <div style={{
                backgroundColor: "var(--color-surface)",
                padding: "12px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--color-border)",
                fontSize: "0.875rem",
                marginTop: "4px",
                lineHeight: 1.5,
              }}>
                {activeReport.description}
              </div>
            </div>

            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Location Details</span>
              <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", marginTop: "4px" }}>
                <MapPin size={16} color="var(--color-primary)" />
                <span>
                  {activeReport.latitude && activeReport.longitude
                    ? `Lat: ${activeReport.latitude.toFixed(4)}, Lon: ${activeReport.longitude.toFixed(4)} (${activeReport.location_precision})`
                    : "Landmark/Text description only"}
                </span>
              </div>
            </div>

            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Submission Metadata</span>
              <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", marginTop: "2px" }}>
                Channel: {activeReport.source_channel} • Submitted: {new Date(activeReport.submitted_at).toLocaleString()}
              </div>
            </div>

            {/* Photo Evidence Preview if present */}
            {activeReport.media_assets.length > 0 && (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Attached Media Asset</span>
                <div style={{
                  marginTop: "6px",
                  borderRadius: "var(--radius-md)",
                  overflow: "hidden",
                  border: "1px solid var(--color-border)",
                  maxHeight: "180px",
                  backgroundColor: "#000",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}>
                  <img
                    src={mediaUrl(activeReport.media_assets[0])}
                    alt={`Citizen evidence ${activeReport.media_assets[0].original_filename}`}
                    style={{ maxWidth: "100%", maxHeight: "180px", objectFit: "contain" }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Column 2: Context, Nearby Reports & Potential Duplicates */}
          <div className="card" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--color-text-muted)" }}>
                COL 2: OPERATIONAL CONTEXT & NEARBY REPORTS
              </span>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--color-text)", marginTop: "2px" }}>
                Cluster & Duplicate Detection
              </h3>
            </div>

            <div>
              <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--color-text)", marginBottom: "6px" }}>
                Nearby Reports in Freetown ({activeItem.nearby_reports.length} found)
              </div>
              {activeItem.nearby_reports.length === 0 ? (
                <div style={{
                  backgroundColor: "var(--color-surface)",
                  padding: "16px",
                  borderRadius: "var(--radius-md)",
                  fontSize: "0.85rem",
                  color: "var(--color-text-muted)",
                  textAlign: "center",
                }}>
                  No other reports within 2km radius.
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {activeItem.nearby_reports.map((nearby) => (
                    <div
                      key={nearby.id}
                      style={{
                        backgroundColor: "var(--color-surface)",
                        padding: "10px",
                        borderRadius: "var(--radius-md)",
                        border: "1px solid var(--color-border)",
                        fontSize: "0.8rem",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                        <strong>{nearby.tracking_reference}</strong>
                        <StatusBadge status={nearby.current_status} />
                      </div>
                      <p style={{ color: "var(--color-text)", margin: "4px 0" }}>
                        {nearby.description.slice(0, 80)}...
                      </p>
                      <span style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>
                        {nearby.latitude && nearby.longitude
                          ? `Lat: ${nearby.latitude.toFixed(4)}, Lon: ${nearby.longitude.toFixed(4)}`
                          : "User entered location"}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Existing Active Incidents for Merge Target */}
            <div>
              <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--color-text)", marginBottom: "6px" }}>
                Active Incident Cases ({incidents.length} open)
              </div>
              <select
                className="input-field"
                value={selectedIncidentForMerge}
                onChange={(e) => setSelectedIncidentForMerge(e.target.value)}
                style={{ fontSize: "0.85rem" }}
              >
                {incidents.map((inc) => (
                  <option key={inc.id} value={inc.id}>
                    [{inc.lifecycle_status}] {inc.title} ({inc.linked_reports_count} reports linked)
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Column 3: Decision Controls & Required Reason */}
          <div className="card" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--color-text-muted)" }}>
                COL 3: HUMAN DECISION & ACTIONS
              </span>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--color-text)", marginTop: "2px" }}>
                Moderator Decision Authority
              </h3>
            </div>

            <div>
              <label className="input-label">
                Decision Justification / Reason <span style={{ color: "var(--color-danger)" }}>*</span>
              </label>
              <textarea
                className="input-field"
                rows={3}
                required
                placeholder="Explicit human reason explaining verification, merge justification, or clarification note..."
                value={decisionReason}
                onChange={(e) => setDecisionReason(e.target.value)}
              />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <button
                className="btn-primary"
                onClick={() => handleDecision("VERIFY")}
                disabled={loading || !decisionReason.trim()}
              >
                <CheckCircle size={16} />
                <span>Verify Report</span>
              </button>

              <button
                className="btn-secondary"
                onClick={() => {
                  setNewIncidentTitle(`${activeReport.category_name || "Civic Hazard"}: ${activeReport.description.slice(0, 40)}...`);
                  setNewIncidentSummary(activeReport.description);
                  setShowCreateIncidentModal(true);
                }}
                disabled={loading}
              >
                <Layers size={16} />
                <span>Create Incident & Assign</span>
              </button>

              <button
                className="btn-secondary"
                onClick={() => handleDecision("MERGE")}
                disabled={loading || !decisionReason.trim() || !selectedIncidentForMerge}
              >
                <GitMerge size={16} />
                <span>Merge Into Selected Incident</span>
              </button>

              <button
                className="btn-secondary"
                onClick={() => handleDecision("NEEDS_CLARIFICATION")}
                disabled={loading || !decisionReason.trim()}
              >
                <HelpCircle size={16} />
                <span>Request Clarification</span>
              </button>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                <button
                  className="btn-secondary btn-sm"
                  onClick={() => handleDecision("ESCALATE")}
                  disabled={loading || !decisionReason.trim()}
                >
                  <ShieldAlert size={14} />
                  <span>Escalate</span>
                </button>
                <button
                  className="btn-danger btn-sm"
                  onClick={() => handleDecision("REJECT")}
                  disabled={loading || !decisionReason.trim()}
                >
                  <XCircle size={14} />
                  <span>Reject</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      </>
      )}

      {/* Create & Assign Incident Modal */}
      {showCreateIncidentModal && activeReport && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "8px" }}>
              Create Incident Case & Assign
            </h3>
            <p style={{ fontSize: "0.85rem", color: "var(--color-text-muted)", marginBottom: "16px" }}>
              Creates an actionable municipal work order linked to Report {activeReport.tracking_reference}.
            </p>

            <form onSubmit={handleCreateAndAssignIncident} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <label className="input-label">Incident Title</label>
                <input
                  type="text"
                  className="input-field"
                  required
                  value={newIncidentTitle}
                  onChange={(e) => setNewIncidentTitle(e.target.value)}
                />
              </div>

              <div>
                <label className="input-label">Operational Summary</label>
                <textarea
                  className="input-field"
                  rows={3}
                  required
                  value={newIncidentSummary}
                  onChange={(e) => setNewIncidentSummary(e.target.value)}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <div>
                  <label className="input-label">Priority</label>
                  <select
                    className="input-field"
                    value={newIncidentPriority}
                    onChange={(e) => setNewIncidentPriority(e.target.value as "LOW" | "MEDIUM" | "HIGH" | "URGENT")}
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </select>
                </div>

                <div>
                  <label className="input-label">Assign To Institution</label>
                  <select
                    className="input-field"
                    value={assignInstitutionId}
                    onChange={(e) => setAssignInstitutionId(e.target.value)}
                  >
                    {institutions.map((inst) => (
                      <option key={inst.id} value={inst.id}>
                        {inst.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "12px" }}>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowCreateIncidentModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? "Creating..." : "Create & Assign Case"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
