import React, { useState, useEffect } from "react";
import {
  FileText,
  Search,
  MapPin,
  Camera,
  CheckCircle,
  AlertCircle,
  ShieldCheck,
  Send,
  AlertTriangle,
} from "lucide-react";
import type { ServiceCategory, ReportPublicStatus } from "../types";
import { getCategories, submitReport, uploadReportMedia, getPublicReportStatus, disputeResolution, listReports, ApiError } from "../api/client";
import type { Report } from "../types";

const describeError = (err: unknown, fallback: string) =>
  err instanceof ApiError ? err.message : err instanceof Error ? err.message : fallback;

type GeoState =
  | { status: "idle" }
  | { status: "locating" }
  | { status: "ready"; latitude: number; longitude: number; accuracy: number }
  | { status: "denied" | "unavailable"; message: string };
import { StatusBadge } from "../components/StatusBadge";

export const CitizenView: React.FC = () => {
  const [tab, setTab] = useState<"submit" | "track" | "mine">("submit");
  const [myReports, setMyReports] = useState<Report[]>([]);
  const [myReportsLoading, setMyReportsLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [loading, setLoading] = useState(false);

  // Form State
  const [categoryCode, setCategoryCode] = useState("");
  const [description, setDescription] = useState("");
  const [locationMode, setLocationMode] = useState<"gps" | "manual">("gps");
  const [geo, setGeo] = useState<GeoState>({ status: "idle" });
  const [manualLocation, setManualLocation] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Submission Result State
  const [submitResult, setSubmitResult] = useState<{
    id: string;
    tracking_reference: string;
    status: string;
    next_step: string;
  } | null>(null);

  // Tracking State
  const [searchRef, setSearchRef] = useState("");
  const [trackedReport, setTrackedReport] = useState<ReportPublicStatus | null>(null);
  const [trackError, setTrackError] = useState<string | null>(null);

  // Dispute Modal State
  const [showDisputeModal, setShowDisputeModal] = useState(false);
  const [disputeReason, setDisputeReason] = useState("");
  const [disputeSubmitting, setDisputeSubmitting] = useState(false);
  const [disputeSuccess, setDisputeSuccess] = useState(false);

  useEffect(() => {
    getCategories()
      .then((cats) => {
        setCategories(cats);
        if (cats.length > 0) setCategoryCode(cats[0].code);
      })
      .catch((err: unknown) => setFormError(describeError(err, "Could not load service categories.")));
  }, []);

  // Real device location. Precision is derived from the reported accuracy so
  // moderators know how much to trust the pin; anything worse than 100 m is
  // APPROXIMATE. Denied/unavailable falls back to a landmark description.
  const requestLocation = () => {
    if (!("geolocation" in navigator)) {
      setGeo({ status: "unavailable", message: "This device does not provide location. Describe a nearby landmark instead." });
      setLocationMode("manual");
      return;
    }
    setGeo({ status: "locating" });
    navigator.geolocation.getCurrentPosition(
      (pos) => setGeo({
        status: "ready",
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
        accuracy: pos.coords.accuracy,
      }),
      (err) => {
        const denied = err.code === err.PERMISSION_DENIED;
        setGeo({
          status: denied ? "denied" : "unavailable",
          message: denied
            ? "Location permission was refused. You can describe a nearby landmark instead."
            : "Location could not be determined right now. Describe a nearby landmark instead.",
        });
        setLocationMode("manual");
      },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 }
    );
  };

  const loadMyReports = async () => {
    setMyReportsLoading(true);
    try {
      const { items } = await listReports({ limit: 100 });
      setMyReports(items);
    } catch (err: unknown) {
      setTrackError(describeError(err, "Could not load your reports."));
    } finally {
      setMyReportsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!categoryCode || !description) return;
    setFormError(null);

    const hasGps = locationMode === "gps" && geo.status === "ready";
    if (locationMode === "gps" && !hasGps) {
      setFormError("Capture your location first, or switch to a landmark description.");
      return;
    }
    if (locationMode === "manual" && manualLocation.trim().length < 5) {
      setFormError("Please describe where the problem is (street, junction or landmark).");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        category_code: categoryCode,
        description: locationMode === "manual" ? `${description} (Location details: ${manualLocation.trim()})` : description,
        latitude: hasGps ? geo.latitude : undefined,
        longitude: hasGps ? geo.longitude : undefined,
        location_precision: hasGps ? (geo.accuracy <= 100 ? "EXACT" : "APPROXIMATE") : "USER_ENTERED",
      };

      const res = await submitReport(payload);

      if (selectedFile) {
        try {
          await uploadReportMedia(res.id, selectedFile);
        } catch (err: unknown) {
          // The report itself is saved; tell the citizen the photo was not.
          setFormError(`Report saved, but the photo was rejected: ${describeError(err, "invalid image")}`);
        }
      }

      setSubmitResult(res);
      setDescription("");
      setSelectedFile(null);
      setManualLocation("");
    } catch (err: unknown) {
      setFormError(describeError(err, "Failed to submit report."));
    } finally {
      setLoading(false);
    }
  };

  const handleTrackSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchRef) return;
    setLoading(true);
    setTrackError(null);
    try {
      const res = await getPublicReportStatus(searchRef.trim());
      setTrackedReport(res);
    } catch (err: unknown) {
      setTrackError(describeError(err, "No report found with this reference."));
      setTrackedReport(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDisputeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!trackedReport?.incident_id || !disputeReason) return;
    setDisputeSubmitting(true);
    try {
      await disputeResolution(trackedReport.incident_id, disputeReason);
      setDisputeSuccess(true);
      setTimeout(() => {
        setShowDisputeModal(false);
        setDisputeSuccess(false);
        setDisputeReason("");
        // Re-fetch report
        getPublicReportStatus(trackedReport.tracking_reference).then(setTrackedReport);
      }, 1500);
    } catch (err: unknown) {
      setTrackError(describeError(err, "Failed to submit dispute."));
      setShowDisputeModal(false);
    } finally {
      setDisputeSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      {/* Navigation Tabs */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "24px", borderBottom: "1px solid var(--color-border)", paddingBottom: "8px" }}>
        <button
          type="button"
          onClick={() => setTab("submit")}
          className={tab === "submit" ? "btn-primary" : "btn-secondary"}
          aria-pressed={tab === "submit"}
        >
          <FileText size={16} aria-hidden="true" />
          <span>Submit Public Report</span>
        </button>
        <button
          type="button"
          onClick={() => setTab("track")}
          className={tab === "track" ? "btn-primary" : "btn-secondary"}
          aria-pressed={tab === "track"}
        >
          <Search size={16} aria-hidden="true" />
          <span>Track Safe Status</span>
        </button>
        <button
          type="button"
          onClick={() => { setTab("mine"); void loadMyReports(); }}
          className={tab === "mine" ? "btn-primary" : "btn-secondary"}
          aria-pressed={tab === "mine"}
        >
          <FileText size={16} aria-hidden="true" />
          <span>My Reports</span>
        </button>
      </div>

      {formError && (
        <div role="alert" style={{
          backgroundColor: "var(--color-danger-bg)", color: "var(--color-danger)", padding: "10px 16px",
          borderRadius: "var(--radius-md)", fontWeight: 600, marginBottom: 16, display: "flex", justifyContent: "space-between", gap: 8,
        }}>
          <span>{formError}</span>
          <button type="button" className="btn-sm btn-secondary" onClick={() => setFormError(null)}>Dismiss</button>
        </div>
      )}

      {tab === "mine" && (
        <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>Your submitted reports ({myReports.length})</h3>
            <button type="button" className="btn-sm btn-secondary" onClick={() => void loadMyReports()} disabled={myReportsLoading}>
              {myReportsLoading ? "Loading…" : "Refresh"}
            </button>
          </div>
          {myReports.length === 0 && !myReportsLoading && (
            <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>You have not submitted any reports yet.</p>
          )}
          {myReports.map((r) => (
            <div key={r.id} style={{ border: "1px solid var(--color-border)", borderRadius: "var(--radius-md)", padding: 12, display: "flex", flexDirection: "column", gap: 6 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
                <strong style={{ color: "var(--color-primary)" }}>{r.tracking_reference}</strong>
                <StatusBadge status={r.current_status} />
              </div>
              <div style={{ fontSize: "0.85rem" }}>{r.category_name} · {new Date(r.submitted_at).toLocaleString()}</div>
              <p style={{ fontSize: "0.875rem" }}>{r.description}</p>
              {r.clarification_notes && (
                <p style={{ fontSize: "0.85rem", color: "var(--color-warning)", fontWeight: 600 }}>Moderator asked: {r.clarification_notes}</p>
              )}
              <button type="button" className="btn-sm btn-secondary" style={{ alignSelf: "flex-start" }}
                      onClick={() => { setSearchRef(r.tracking_reference); setTab("track"); getPublicReportStatus(r.tracking_reference).then(setTrackedReport).catch(() => undefined); }}>
                Track status
              </button>
            </div>
          ))}
        </div>
      )}

      {tab === "submit" ? (
        <div>
          {submitResult ? (
            <div className="card" style={{ textAlign: "center", padding: "32px 24px" }}>
              <div style={{
                width: "56px",
                height: "56px",
                borderRadius: "50%",
                backgroundColor: "var(--color-success-bg)",
                color: "var(--color-success)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 16px",
              }}>
                <CheckCircle size={32} />
              </div>
              <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "8px" }}>
                Report Submitted Successfully
              </h2>
              <p style={{ color: "var(--color-text-muted)", marginBottom: "20px" }}>
                Your report has been received and queued for human verification.
              </p>

              <div style={{
                backgroundColor: "var(--color-surface)",
                padding: "16px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--color-border)",
                maxWidth: "400px",
                margin: "0 auto 24px",
              }}>
                <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", marginBottom: "4px" }}>
                  UNIQUE TRACKING REFERENCE
                </div>
                <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--color-primary)", letterSpacing: "0.05em" }}>
                  {submitResult.tracking_reference}
                </div>
                <div style={{ marginTop: "8px" }}>
                  <StatusBadge status={submitResult.status} />
                </div>
              </div>

              <p style={{ fontSize: "0.9rem", color: "var(--color-text-muted)", marginBottom: "24px" }}>
                Next Step: <strong>{submitResult.next_step}</strong>
              </p>

              <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
                <button
                  className="btn-primary"
                  onClick={() => {
                    setSearchRef(submitResult.tracking_reference);
                    setTab("track");
                    getPublicReportStatus(submitResult.tracking_reference).then(setTrackedReport);
                    setSubmitResult(null);
                  }}
                >
                  <Search size={16} />
                  <span>Track This Case</span>
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => setSubmitResult(null)}
                >
                  Submit Another Report
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="card" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div>
                <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--color-text)" }}>
                  Submit a Civic Issue in Freetown
                </h2>
                <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginTop: "4px" }}>
                  Help municipal authorities identify and repair public infrastructure defects.
                </p>
              </div>

              {/* Service Category Selection */}
              <div>
                <label className="input-label">Select Issue Category</label>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "10px" }}>
                  {categories.map((cat) => (
                    <div
                      key={cat.id}
                      onClick={() => setCategoryCode(cat.code)}
                      style={{
                        padding: "12px",
                        borderRadius: "var(--radius-md)",
                        border: categoryCode === cat.code ? "2px solid var(--color-primary)" : "1px solid var(--color-border)",
                        backgroundColor: categoryCode === cat.code ? "var(--color-primary-light)" : "#ffffff",
                        cursor: "pointer",
                      }}
                    >
                      <div style={{ fontWeight: 600, fontSize: "0.9rem", color: categoryCode === cat.code ? "var(--color-primary)" : "var(--color-text)" }}>
                        {cat.name}
                      </div>
                      <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "4px" }}>
                        {cat.description}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Problem Description */}
              <div>
                <label className="input-label">Description of Problem</label>
                <textarea
                  className="input-field"
                  rows={4}
                  required
                  minLength={10}
                  placeholder="Describe the exact hazard, how long it has been present, and immediate impact on traffic or residents..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              {/* Location Controls */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                  <label className="input-label" style={{ margin: 0 }}>Incident Location</label>
                  <div style={{ display: "flex", gap: "6px" }}>
                    <button
                      type="button"
                      className={`btn-sm ${locationMode === "gps" ? "btn-primary" : "btn-secondary"}`}
                      onClick={() => { setLocationMode("gps"); if (geo.status === "idle") requestLocation(); }}
                    >
                      Use my location
                    </button>
                    <button
                      type="button"
                      className={`btn-sm ${locationMode === "manual" ? "btn-primary" : "btn-secondary"}`}
                      onClick={() => setLocationMode("manual")}
                    >
                      Landmark Description
                    </button>
                  </div>
                </div>

                {locationMode === "gps" ? (
                  <div style={{
                    backgroundColor: "var(--color-surface)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "var(--radius-md)",
                    padding: "12px",
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                  }}>
                    <MapPin size={24} color="var(--color-primary)" aria-hidden="true" />
                    <div style={{ flex: 1 }} role="status" aria-live="polite">
                      {geo.status === "ready" && (
                        <>
                          <div style={{ fontSize: "0.85rem", fontWeight: 600 }}>
                            Location captured ({geo.accuracy <= 100 ? "precise" : "approximate"}, ±{Math.round(geo.accuracy)} m)
                          </div>
                          <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
                            Lat {geo.latitude.toFixed(4)}, Lon {geo.longitude.toFixed(4)} — exact coordinates are shown only to verified responders.
                          </div>
                        </>
                      )}
                      {geo.status === "locating" && <div style={{ fontSize: "0.85rem" }}>Finding your location…</div>}
                      {geo.status === "idle" && <div style={{ fontSize: "0.85rem" }}>Tap “Capture location” to pin this report to where you are.</div>}
                      {(geo.status === "denied" || geo.status === "unavailable") && (
                        <div style={{ fontSize: "0.85rem", color: "var(--color-warning)", fontWeight: 600 }}>{geo.message}</div>
                      )}
                    </div>
                    <button type="button" className="btn-sm btn-secondary" onClick={requestLocation} disabled={geo.status === "locating"}>
                      {geo.status === "ready" ? "Re-capture" : "Capture location"}
                    </button>
                  </div>
                ) : (
                  <input
                    type="text"
                    className="input-field"
                    placeholder="e.g. Near St. John Roundabout beside the market stalls"
                    value={manualLocation}
                    onChange={(e) => setManualLocation(e.target.value)}
                  />
                )}
              </div>

              {/* Media Photo Upload */}
              <div>
                <label className="input-label">Attach Photo Evidence (Optional)</label>
                <div style={{
                  border: "2px dashed var(--color-border)",
                  borderRadius: "var(--radius-md)",
                  padding: "16px",
                  textAlign: "center",
                  backgroundColor: "var(--color-surface)",
                  cursor: "pointer",
                }}>
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    id="photo-upload"
                    style={{ display: "none" }}
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setSelectedFile(e.target.files[0]);
                      }
                    }}
                  />
                  <label htmlFor="photo-upload" style={{ cursor: "pointer", display: "inline-block" }}>
                    <Camera size={28} color="var(--color-text-muted)" style={{ margin: "0 auto 6px" }} />
                    <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--color-primary)" }}>
                      {selectedFile ? selectedFile.name : "Click to select a photo from your device"}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "2px" }}>
                      JPEG, PNG, or WEBP up to 10MB. Sensitive location and camera metadata is stripped automatically.
                    </div>
                  </label>
                </div>
              </div>

              {/* Privacy Notice */}
              <div style={{
                display: "flex",
                alignItems: "flex-start",
                gap: "10px",
                backgroundColor: "var(--color-surface)",
                padding: "12px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--color-border)",
              }}>
                <ShieldCheck size={20} color="var(--color-primary)" style={{ flexShrink: 0, marginTop: "2px" }} />
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
                  <strong>Privacy Policy:</strong> SaloneFix protects citizen identity. Exact coordinates and original photos are accessible only to verified municipal responders and are never published on public feeds.
                </div>
              </div>

              <button
                type="submit"
                className="btn-primary"
                disabled={loading}
                style={{ width: "100%", justifyContent: "center" }}
              >
                <Send size={16} />
                <span>{loading ? "Submitting..." : "Submit Incident Report"}</span>
              </button>
            </form>
          )}
        </div>
      ) : (
        /* Track Status Tab */
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <form onSubmit={handleTrackSearch} className="card" style={{ display: "flex", gap: "12px" }}>
            <input
              type="text"
              className="input-field"
              placeholder="Enter reference number (e.g. SF-2026-000001)..."
              value={searchRef}
              onChange={(e) => setSearchRef(e.target.value)}
              style={{ flex: 1 }}
            />
            <button type="submit" className="btn-primary" disabled={loading}>
              <Search size={16} />
              <span>Track</span>
            </button>
          </form>

          {trackError && (
            <div style={{
              backgroundColor: "var(--color-danger-bg)",
              color: "var(--color-danger)",
              padding: "12px 16px",
              borderRadius: "var(--radius-md)",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              fontSize: "0.875rem",
            }}>
              <AlertCircle size={18} />
              <span>{trackError}</span>
            </div>
          )}

          {trackedReport && (
            <div className="card" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "8px" }}>
                <div>
                  <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>REFERENCE NUMBER</span>
                  <h3 style={{ fontSize: "1.3rem", fontWeight: 800, color: "var(--color-primary)" }}>
                    {trackedReport.tracking_reference}
                  </h3>
                </div>
                <StatusBadge status={trackedReport.current_status} />
              </div>

              <div style={{
                backgroundColor: "var(--color-surface)",
                padding: "12px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--color-border)",
              }}>
                <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--color-text-muted)", marginBottom: "4px" }}>
                  NEXT EXPECTED ACTION
                </div>
                <div style={{ fontSize: "0.9rem", color: "var(--color-text)", fontWeight: 500 }}>
                  {trackedReport.next_step}
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div>
                  <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Category</span>
                  <div style={{ fontWeight: 600 }}>{trackedReport.category_name}</div>
                </div>
                <div>
                  <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Responsible Institution</span>
                  <div style={{ fontWeight: 600 }}>{trackedReport.responsible_institution || "Pending Assignment"}</div>
                </div>
              </div>

              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>Description</span>
                <div style={{ fontSize: "0.9rem", color: "var(--color-text)", marginTop: "2px" }}>
                  {trackedReport.description}
                </div>
              </div>

              {trackedReport.resolution_description && (
                <div style={{
                  backgroundColor: "var(--color-success-bg)",
                  border: "1px solid rgba(24, 121, 78, 0.3)",
                  padding: "12px",
                  borderRadius: "var(--radius-md)",
                }}>
                  <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--color-success)", marginBottom: "4px" }}>
                    INSTITUTIONAL RESOLUTION REPORT
                  </div>
                  <div style={{ fontSize: "0.875rem", color: "var(--color-text)" }}>
                    {trackedReport.resolution_description}
                  </div>
                </div>
              )}

              {trackedReport.can_dispute && (
                <div style={{ marginTop: "12px", borderTop: "1px solid var(--color-border)", paddingTop: "16px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>Not satisfied with this resolution?</div>
                      <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
                        If the issue has not been properly resolved, you can dispute the closure.
                      </div>
                    </div>
                    <button
                      className="btn-danger btn-sm"
                      onClick={() => setShowDisputeModal(true)}
                    >
                      <AlertTriangle size={14} />
                      <span>Dispute Resolution</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Dispute Modal */}
      {showDisputeModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "8px" }}>
              Dispute Resolution
            </h3>
            <p style={{ fontSize: "0.85rem", color: "var(--color-text-muted)", marginBottom: "16px" }}>
              Submitting a dispute immediately returns this incident to the human moderation queue for independent reinvestigation.
            </p>

            {disputeSuccess ? (
              <div style={{
                backgroundColor: "var(--color-success-bg)",
                color: "var(--color-success)",
                padding: "16px",
                borderRadius: "var(--radius-md)",
                textAlign: "center",
                fontWeight: 600,
              }}>
                Dispute submitted. Case reopened for review.
              </div>
            ) : (
              <form onSubmit={handleDisputeSubmit}>
                <div style={{ marginBottom: "16px" }}>
                  <label className="input-label">Reason for Dispute</label>
                  <textarea
                    className="input-field"
                    rows={4}
                    required
                    minLength={5}
                    placeholder="Explain why the repair is incomplete or defect is still present..."
                    value={disputeReason}
                    onChange={(e) => setDisputeReason(e.target.value)}
                  />
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => setShowDisputeModal(false)}
                    disabled={disputeSubmitting}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-danger"
                    disabled={disputeSubmitting || !disputeReason}
                  >
                    {disputeSubmitting ? "Submitting..." : "Submit Dispute"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
