import React, { useState, useEffect, useCallback } from "react";
import { CheckCircle, XCircle, RotateCcw, Link2, Building2, Lock, AlertTriangle, Clock } from "lucide-react";
import type { Incident, IncidentStatus, Institution, Report } from "../types";
import {
  getIncidents,
  getInstitutions,
  listReports,
  reviewResolutionEvidence,
  reopenIncident,
  linkReportToIncident,
  assignIncident,
  updateIncidentStatus,
  mediaUrl,
  ApiError,
} from "../api/client";
import { StatusBadge } from "../components/StatusBadge";

type Filter = "ALL" | "NEEDS_REVIEW" | IncidentStatus;

const FILTERS: { value: Filter; label: string }[] = [
  { value: "NEEDS_REVIEW", label: "Needs my decision" },
  { value: "ALL", label: "All open" },
  { value: "RESOLUTION_UNDER_REVIEW", label: "Evidence review" },
  { value: "DISPUTED", label: "Disputed" },
  { value: "ESCALATED", label: "Escalated" },
  { value: "RESOLVED", label: "Resolved" },
  { value: "CLOSED", label: "Closed" },
];

const NEEDS_REVIEW: IncidentStatus[] = ["RESOLUTION_UNDER_REVIEW", "DISPUTED", "ESCALATED", "VERIFIED"];

const describeError = (err: unknown, fallback: string) =>
  err instanceof ApiError ? err.message : err instanceof Error ? err.message : fallback;

export const IncidentCasesPanel: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [verifiedReports, setVerifiedReports] = useState<Report[]>([]);
  const [filter, setFilter] = useState<Filter>("NEEDS_REVIEW");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [reason, setReason] = useState("");
  const [linkReportId, setLinkReportId] = useState("");
  const [assignInstitutionId, setAssignInstitutionId] = useState("");
  const [assignDueAt, setAssignDueAt] = useState("");

  const load = useCallback(async () => {
    try {
      const [incs, insts, reps] = await Promise.all([
        getIncidents({ limit: 100 }),
        getInstitutions(),
        listReports({ status: "VERIFIED", limit: 100 }),
      ]);
      setIncidents(incs.items);
      setInstitutions(insts);
      setVerifiedReports(reps.items);
      setAssignInstitutionId((cur) => cur || insts[0]?.id || "");
      setError(null);
    } catch (err) {
      setError(describeError(err, "Could not load incident cases."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const visible = incidents.filter((i) => {
    if (filter === "ALL") return i.lifecycle_status !== "CLOSED";
    if (filter === "NEEDS_REVIEW") return NEEDS_REVIEW.includes(i.lifecycle_status);
    return i.lifecycle_status === filter;
  });
  const selected = visible.find((i) => i.id === selectedId) ?? visible[0] ?? null;

  const flash = (msg: string) => {
    setMessage(msg);
    setTimeout(() => setMessage(null), 4000);
  };

  const run = async (label: string, fn: () => Promise<unknown>) => {
    setBusy(true);
    setError(null);
    try {
      await fn();
      setReason("");
      flash(label);
      await load();
    } catch (err) {
      setError(describeError(err, `${label} failed.`));
    } finally {
      setBusy(false);
    }
  };

  const requireReason = (): boolean => {
    if (!reason.trim() || reason.trim().length < 3) {
      setError("A written reason is required for every human decision.");
      return false;
    }
    return true;
  };

  const pendingEvidence = selected?.resolution_evidence?.filter((e) => e.review_status === "PENDING") ?? [];
  const latestPending = pendingEvidence[pendingEvidence.length - 1];
  const photoMissing = selected?.requires_resolution_evidence !== false && latestPending && latestPending.media_assets.length === 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <div role="group" aria-label="Filter incident cases" style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {FILTERS.map((f) => (
            <button
              key={f.value} type="button"
              className={`btn-sm ${filter === f.value ? "btn-primary" : "btn-secondary"}`}
              aria-pressed={filter === f.value}
              onClick={() => { setFilter(f.value); setSelectedId(null); }}
            >
              {f.label}
            </button>
          ))}
        </div>
        <button type="button" className="btn-sm btn-secondary" style={{ marginLeft: "auto" }} disabled={loading}
                onClick={() => { setLoading(true); void load(); }}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {message && (
        <div role="status" style={{ backgroundColor: "var(--color-success-bg)", color: "var(--color-success)", padding: "10px 16px", borderRadius: "var(--radius-md)", fontWeight: 600, display: "flex", gap: 8, alignItems: "center" }}>
          <CheckCircle size={16} aria-hidden="true" /> {message}
        </div>
      )}
      {error && (
        <div role="alert" style={{ backgroundColor: "var(--color-danger-bg)", color: "var(--color-danger)", padding: "10px 16px", borderRadius: "var(--radius-md)", fontWeight: 600, display: "flex", gap: 8, alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ display: "flex", gap: 8, alignItems: "center" }}><AlertTriangle size={16} aria-hidden="true" /> {error}</span>
          <button type="button" className="btn-sm btn-secondary" onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "minmax(280px, 1fr) 2fr", gap: 20 }}>
        {/* List */}
        <div className="card" style={{ padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ fontWeight: 700, fontSize: "0.9rem", color: "var(--color-text-muted)" }}>
            CASES ({visible.length})
          </div>
          {visible.length === 0 ? (
            <div style={{ padding: "24px 12px", textAlign: "center", color: "var(--color-text-muted)", fontSize: "0.85rem" }}>
              {loading ? "Loading…" : "Nothing in this view."}
            </div>
          ) : visible.map((inc) => (
            <button
              type="button" key={inc.id} onClick={() => setSelectedId(inc.id)} aria-pressed={selected?.id === inc.id}
              style={{
                textAlign: "left", width: "100%", padding: 12, borderRadius: "var(--radius-md)", font: "inherit", cursor: "pointer",
                border: selected?.id === inc.id ? "2px solid var(--color-primary)" : "1px solid var(--color-border)",
                backgroundColor: selected?.id === inc.id ? "var(--color-primary-light)" : "#fff",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8, marginBottom: 4 }}>
                <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--color-text-muted)" }}>{inc.priority}</span>
                <StatusBadge status={inc.lifecycle_status} />
              </div>
              <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>{inc.title}</div>
              <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: 4, display: "flex", gap: 8, flexWrap: "wrap" }}>
                <span>{inc.assigned_institution_name ?? "Unassigned"}</span>
                <span>· {inc.linked_reports_count} report(s)</span>
                {inc.active_assignment?.is_overdue && <span style={{ color: "var(--color-danger)", fontWeight: 700 }}>OVERDUE</span>}
              </div>
            </button>
          ))}
        </div>

        {/* Detail */}
        {selected ? (
          <div className="card" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10, flexWrap: "wrap" }}>
              <div>
                <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>{selected.category_name} · {selected.id}</span>
                <h3 style={{ fontSize: "1.3rem", fontWeight: 800, marginTop: 2 }}>{selected.title}</h3>
              </div>
              <StatusBadge status={selected.lifecycle_status} />
            </div>

            <p style={{ fontSize: "0.875rem", lineHeight: 1.5, backgroundColor: "var(--color-surface)", padding: 12, borderRadius: "var(--radius-md)", border: "1px solid var(--color-border)" }}>
              {selected.summary}
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, fontSize: "0.85rem" }}>
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Assignment</span>
                <div style={{ display: "flex", gap: 6, alignItems: "center", marginTop: 2 }}>
                  <Building2 size={14} aria-hidden="true" />
                  {selected.active_assignment
                    ? `${selected.active_assignment.institution_name} — ${selected.active_assignment.status}`
                    : "Not assigned"}
                </div>
              </div>
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Due</span>
                <div style={{ display: "flex", gap: 6, alignItems: "center", marginTop: 2, color: selected.active_assignment?.is_overdue ? "var(--color-danger)" : undefined }}>
                  <Clock size={14} aria-hidden="true" />
                  {selected.active_assignment?.due_at ? new Date(selected.active_assignment.due_at).toLocaleString() : "No due date"}
                  {selected.active_assignment?.is_overdue && " (overdue)"}
                </div>
              </div>
            </div>

            {/* Linked reports */}
            <div>
              <span style={{ fontSize: "0.8rem", fontWeight: 700 }}>Linked reports ({selected.linked_reports?.length ?? 0})</span>
              <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 6 }}>
                {selected.linked_reports?.map((lr) => (
                  <div key={lr.link_id} style={{ fontSize: "0.85rem", padding: 8, border: "1px solid var(--color-border)", borderRadius: "var(--radius-md)", backgroundColor: "var(--color-surface)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                      <strong>{lr.report.tracking_reference}</strong>
                      <StatusBadge status={lr.report.current_status} />
                    </div>
                    <div style={{ marginTop: 2 }}>{lr.report.description}</div>
                    {lr.report.media_assets?.length > 0 && (
                      <div style={{ display: "flex", gap: 6, marginTop: 6, flexWrap: "wrap" }}>
                        {lr.report.media_assets.map((m) => (
                          <img key={m.id} src={mediaUrl(m)} alt={`Citizen photo ${m.original_filename}`}
                               style={{ width: 80, height: 60, objectFit: "cover", borderRadius: 4, border: "1px solid var(--color-border)" }} />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Evidence */}
            <div>
              <span style={{ fontSize: "0.8rem", fontWeight: 700 }}>Resolution evidence ({selected.resolution_evidence?.length ?? 0})</span>
              <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 6 }}>
                {(selected.resolution_evidence ?? []).map((ev) => (
                  <div key={ev.id} style={{ fontSize: "0.85rem", padding: 10, border: "1px solid var(--color-border)", borderRadius: "var(--radius-md)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
                      <span style={{ color: "var(--color-text-muted)", fontSize: "0.75rem" }}>
                        {new Date(ev.submitted_at).toLocaleString()} · {ev.uploader_name ?? "Officer"}
                      </span>
                      <strong style={{ fontSize: "0.75rem" }}>{ev.review_status}</strong>
                    </div>
                    <p style={{ margin: "6px 0" }}>{ev.description}</p>
                    {ev.review_reason && <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>Review: {ev.review_reason}</p>}
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 4 }}>
                      {ev.media_assets.map((m) => (
                        <a key={m.id} href={mediaUrl(m)} target="_blank" rel="noopener noreferrer">
                          <img src={mediaUrl(m)} alt={`Evidence photo ${m.original_filename}`}
                               style={{ width: 120, height: 90, objectFit: "cover", borderRadius: 4, border: "1px solid var(--color-border)" }} />
                        </a>
                      ))}
                      {ev.media_assets.length === 0 && (
                        <span style={{ fontSize: "0.75rem", color: "var(--color-warning)", fontWeight: 600 }}>No photo attached</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Disputes */}
            {(selected.disputes?.length ?? 0) > 0 && (
              <div>
                <span style={{ fontSize: "0.8rem", fontWeight: 700 }}>Citizen disputes</span>
                {selected.disputes!.map((d) => (
                  <div key={d.id} style={{ fontSize: "0.85rem", padding: 10, marginTop: 6, borderRadius: "var(--radius-md)", backgroundColor: "var(--status-disputed-bg)", border: "1px solid var(--status-disputed)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                      <span style={{ color: "var(--color-text-muted)", fontSize: "0.75rem" }}>{new Date(d.created_at).toLocaleString()}</span>
                      <strong style={{ fontSize: "0.75rem" }}>{d.status}</strong>
                    </div>
                    <p style={{ marginTop: 4 }}>{d.reason}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Decision panel */}
            <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: 16, display: "flex", flexDirection: "column", gap: 12 }}>
              <div>
                <label className="input-label" htmlFor="case-reason">
                  Decision reason <span style={{ color: "var(--color-danger)" }}>*</span>
                </label>
                <textarea id="case-reason" className="input-field" rows={2} value={reason} onChange={(e) => setReason(e.target.value)}
                          placeholder="Recorded verbatim in the audit trail." />
              </div>

              {selected.lifecycle_status === "RESOLUTION_UNDER_REVIEW" && (
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                  <button type="button" className="btn-primary" disabled={busy || !!photoMissing}
                          title={photoMissing ? "This category requires photo evidence before approval" : undefined}
                          onClick={() => requireReason() && run("Resolution approved — incident RESOLVED.", () => reviewResolutionEvidence(selected.id, "APPROVED", reason.trim()))}>
                    <CheckCircle size={16} aria-hidden="true" /> Approve resolution
                  </button>
                  <button type="button" className="btn-danger" disabled={busy}
                          onClick={() => requireReason() && run("Evidence rejected — returned to officer as IN_PROGRESS.", () => reviewResolutionEvidence(selected.id, "REJECTED", reason.trim()))}>
                    <XCircle size={16} aria-hidden="true" /> Reject evidence
                  </button>
                  {photoMissing && (
                    <span style={{ fontSize: "0.8rem", color: "var(--color-warning)", fontWeight: 600 }}>
                      Approval blocked: no photo attached to the pending evidence.
                    </span>
                  )}
                </div>
              )}

              {(selected.lifecycle_status === "DISPUTED" || selected.lifecycle_status === "RESOLVED" || selected.lifecycle_status === "CLOSED") && (
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <button type="button" className="btn-secondary" disabled={busy}
                          onClick={() => requireReason() && run("Incident reopened for review.", () => reopenIncident(selected.id, reason.trim()))}>
                    <RotateCcw size={16} aria-hidden="true" /> Reopen
                  </button>
                  {selected.lifecycle_status === "DISPUTED" && (
                    <button type="button" className="btn-secondary" disabled={busy}
                            onClick={() => requireReason() && run("Dispute reviewed — case returned to IN_PROGRESS.", () => updateIncidentStatus(selected.id, "IN_PROGRESS", reason.trim()))}>
                      Send back to officer
                    </button>
                  )}
                  {selected.lifecycle_status === "RESOLVED" && (
                    <button type="button" className="btn-primary" disabled={busy}
                            onClick={() => requireReason() && run("Incident closed.", () => updateIncidentStatus(selected.id, "CLOSED", reason.trim()))}>
                      <Lock size={16} aria-hidden="true" /> Close case
                    </button>
                  )}
                </div>
              )}

              {(selected.lifecycle_status === "VERIFIED" || selected.lifecycle_status === "ESCALATED" ||
                (selected.lifecycle_status === "ASSIGNED" && selected.active_assignment?.status === "DECLINED")) && (
                <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr auto", gap: 8, alignItems: "end" }}>
                  <div>
                    <label className="input-label" htmlFor="assign-inst">{selected.active_assignment ? "Reassign to" : "Assign to"} institution</label>
                    <select id="assign-inst" className="input-field" value={assignInstitutionId} onChange={(e) => setAssignInstitutionId(e.target.value)}>
                      {institutions.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="input-label" htmlFor="assign-due">Due date</label>
                    <input id="assign-due" type="date" className="input-field" value={assignDueAt} onChange={(e) => setAssignDueAt(e.target.value)} />
                  </div>
                  <button type="button" className="btn-primary" disabled={busy || !assignInstitutionId}
                          onClick={() => run("Incident assigned.", () =>
                            assignIncident(selected.id, assignInstitutionId, undefined, assignDueAt ? new Date(`${assignDueAt}T17:00:00`).toISOString() : undefined))}>
                    <Building2 size={16} aria-hidden="true" /> Assign
                  </button>
                </div>
              )}

              {selected.lifecycle_status !== "CLOSED" && (
                <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 8, alignItems: "end" }}>
                  <div>
                    <label className="input-label" htmlFor="link-report">Link a verified report to this case</label>
                    <select id="link-report" className="input-field" value={linkReportId} onChange={(e) => setLinkReportId(e.target.value)}>
                      <option value="">Select a VERIFIED report…</option>
                      {verifiedReports
                        .filter((r) => !selected.linked_reports?.some((lr) => lr.report.id === r.id))
                        .map((r) => <option key={r.id} value={r.id}>{r.tracking_reference} — {r.description.slice(0, 60)}</option>)}
                    </select>
                  </div>
                  <button type="button" className="btn-secondary" disabled={busy || !linkReportId}
                          onClick={() => run("Report linked to incident.", async () => {
                            await linkReportToIncident(selected.id, linkReportId, reason.trim() || undefined);
                            setLinkReportId("");
                          })}>
                    <Link2 size={16} aria-hidden="true" /> Link
                  </button>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="card" style={{ textAlign: "center", padding: "48px 24px", color: "var(--color-text-muted)" }}>
            Select a case to review evidence, disputes and assignments.
          </div>
        )}
      </div>
    </div>
  );
};
