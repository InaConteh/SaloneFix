import React, { useState, useEffect, useCallback } from "react";
import { Shield, RefreshCw, ChevronLeft, ChevronRight } from "lucide-react";
import type { AuditEvent, Incident } from "../types";
import { getAllAuditEvents, getIncidents, getIncidentAudit, ApiError } from "../api/client";

const PAGE_SIZE = 50;

const ENTITY_TYPES = ["", "REPORT", "INCIDENT", "ASSIGNMENT", "USER", "INSTITUTION", "AUDIT"];

const describeError = (err: unknown, fallback: string) =>
  err instanceof ApiError ? err.message : err instanceof Error ? err.message : fallback;

export const AuditorView: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>("");
  const [entityType, setEntityType] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [eventsResult, incsPage] = await Promise.all([
        selectedIncidentId
          ? getIncidentAudit(selectedIncidentId)
          : getAllAuditEvents({ entity_type: entityType || undefined, limit: PAGE_SIZE, offset }),
        getIncidents({ limit: 100 }),
      ]);
      if (Array.isArray(eventsResult)) {
        setEvents(eventsResult);
        setTotal(eventsResult.length);
      } else {
        setEvents(eventsResult.items);
        setTotal(eventsResult.total);
      }
      setIncidents(incsPage.items);
      setError(null);
    } catch (err) {
      setError(describeError(err, "Could not load audit events."));
    } finally {
      setLoading(false);
    }
  }, [selectedIncidentId, entityType, offset]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const refresh = () => {
    setLoading(true);
    void loadData();
  };

  const page = Math.floor(offset / PAGE_SIZE) + 1;
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const paged = !selectedIncidentId;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Shield size={22} color="var(--color-primary)" aria-hidden="true" />
            <h2 style={{ fontSize: "1.4rem", fontWeight: 700, color: "var(--color-text)" }}>
              Independent Governance &amp; Audit Trail
            </h2>
          </div>
          <p style={{ fontSize: "0.85rem", color: "var(--color-text-muted)", marginTop: "2px" }}>
            Append-only record of every material state change and the human reason behind it. Reading this log is itself logged.
          </p>
        </div>
        <button type="button" className="btn-secondary btn-sm" onClick={refresh} disabled={loading}>
          <RefreshCw size={14} aria-hidden="true" />
          <span>{loading ? "Refreshing…" : "Refresh"}</span>
        </button>
      </div>

      {error && (
        <div role="alert" style={{ backgroundColor: "var(--color-danger-bg)", color: "var(--color-danger)", padding: "10px 16px", borderRadius: "var(--radius-md)", fontWeight: 600 }}>
          {error}
        </div>
      )}

      <div className="card" style={{ padding: "14px", display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
        <label htmlFor="audit-case" style={{ fontSize: "0.85rem", fontWeight: 600 }}>Case:</label>
        <select
          id="audit-case"
          className="input-field"
          value={selectedIncidentId}
          onChange={(e) => { setSelectedIncidentId(e.target.value); setOffset(0); }}
          style={{ maxWidth: "420px", fontSize: "0.85rem" }}
        >
          <option value="">All system events</option>
          {incidents.map((inc) => (
            <option key={inc.id} value={inc.id}>{inc.title} [{inc.lifecycle_status}]</option>
          ))}
        </select>

        <label htmlFor="audit-entity" style={{ fontSize: "0.85rem", fontWeight: 600 }}>Entity:</label>
        <select
          id="audit-entity"
          className="input-field"
          value={entityType}
          disabled={!!selectedIncidentId}
          onChange={(e) => { setEntityType(e.target.value); setOffset(0); }}
          style={{ maxWidth: "200px", fontSize: "0.85rem" }}
        >
          {ENTITY_TYPES.map((t) => <option key={t} value={t}>{t || "Any"}</option>)}
        </select>

        <span style={{ marginLeft: "auto", fontSize: "0.8rem", color: "var(--color-text-muted)" }}>
          {total} event{total === 1 ? "" : "s"}
        </span>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
            <caption style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0 0 0 0)" }}>Audit events</caption>
            <thead>
              <tr style={{ backgroundColor: "var(--color-surface)", borderBottom: "1px solid var(--color-border)", textAlign: "left" }}>
                <th scope="col" style={{ padding: "12px 16px", fontWeight: 700, color: "var(--color-text-muted)" }}>TIMESTAMP</th>
                <th scope="col" style={{ padding: "12px 16px", fontWeight: 700, color: "var(--color-text-muted)" }}>ACTOR</th>
                <th scope="col" style={{ padding: "12px 16px", fontWeight: 700, color: "var(--color-text-muted)" }}>ACTION</th>
                <th scope="col" style={{ padding: "12px 16px", fontWeight: 700, color: "var(--color-text-muted)" }}>ENTITY</th>
                <th scope="col" style={{ padding: "12px 16px", fontWeight: 700, color: "var(--color-text-muted)" }}>REASON / DECISION</th>
              </tr>
            </thead>
            <tbody>
              {events.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ padding: "32px", textAlign: "center", color: "var(--color-text-muted)" }}>
                    {loading ? "Loading…" : "No audit events recorded for this selection."}
                  </td>
                </tr>
              ) : (
                events.map((ev, index) => {
                  const negative = ev.action.includes("REJECT") || ev.action.includes("DISPUTE") || ev.action.includes("DECLINED");
                  return (
                    <tr key={ev.id || index} style={{ borderBottom: "1px solid var(--color-border)", backgroundColor: index % 2 === 0 ? "#ffffff" : "var(--color-surface)" }}>
                      <td style={{ padding: "12px 16px", whiteSpace: "nowrap", color: "var(--color-text-muted)", fontSize: "0.8rem" }}>
                        {new Date(ev.created_at).toLocaleString()}
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        <div style={{ fontWeight: 600 }}>{ev.actor_name || "System"}</div>
                        {ev.actor_role && (
                          <span style={{ fontSize: "0.7rem", color: "var(--color-primary)", fontWeight: 600 }}>{ev.actor_role}</span>
                        )}
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        <span style={{
                          backgroundColor: negative ? "var(--color-danger-bg)" : "var(--color-primary-light)",
                          color: negative ? "var(--color-danger)" : "var(--color-primary)",
                          padding: "3px 8px", borderRadius: "4px", fontWeight: 700, fontSize: "0.75rem",
                        }}>
                          {ev.action}
                        </span>
                      </td>
                      <td style={{ padding: "12px 16px", fontSize: "0.8rem", color: "var(--color-text-muted)" }} title={ev.entity_id}>
                        {ev.entity_type} ({ev.entity_id.slice(0, 8)}…)
                      </td>
                      <td style={{ padding: "12px 16px", color: "var(--color-text)", maxWidth: "320px" }}>
                        {ev.reason || "—"}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {paged && pages > 1 && (
          <nav aria-label="Audit log pages" style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 8, padding: "10px 16px", borderTop: "1px solid var(--color-border)", fontSize: "0.85rem" }}>
            <button type="button" className="btn-sm btn-secondary" disabled={offset === 0 || loading} onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))} aria-label="Previous page">
              <ChevronLeft size={14} aria-hidden="true" />
            </button>
            <span>Page {page} of {pages}</span>
            <button type="button" className="btn-sm btn-secondary" disabled={page >= pages || loading} onClick={() => setOffset(offset + PAGE_SIZE)} aria-label="Next page">
              <ChevronRight size={14} aria-hidden="true" />
            </button>
          </nav>
        )}
      </div>
    </div>
  );
};
