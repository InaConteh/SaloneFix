"""Baseline metrics export (docs/specs/09-research/evaluation-protocol.md section 4).

The export feeds the Phase 2 human-only baseline that Phase 3 is compared
against, so these tests care as much about honesty as about arithmetic: an empty
window must not read as a rate of zero, and metrics that need ground truth must
stay declared-unavailable rather than guessed.
"""
import io

from PIL import Image

BASELINE = "/api/v1/metrics/baseline"


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def metric(payload, key):
    return next(m for m in payload["metrics"] if m["key"] == key)


def run_full_lifecycle(client, citizen_token, moderator_token, officer_token):
    """Report x2 -> verify + merge -> incident -> assign -> accept -> evidence -> approve -> dispute."""
    rep1 = client.post(
        "/api/v1/reports",
        headers=auth(citizen_token),
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Deep pothole on Kissy Road opposite the primary school.",
            "latitude": 8.4851,
            "longitude": -13.2285,
            "location_precision": "EXACT",
        },
    ).json()
    rep2 = client.post(
        "/api/v1/reports",
        headers=auth(citizen_token),
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Road crater near the Kissy Road school slowing all traffic.",
            "latitude": 8.4853,
            "longitude": -13.2287,
            "location_precision": "APPROXIMATE",
        },
    ).json()

    client.post(
        f"/api/v1/moderation/reports/{rep1['id']}/decision",
        headers=auth(moderator_token),
        json={"decision": "VERIFY", "reason": "Genuine public road hazard needing an institutional response."},
    )

    road_cat = next(c for c in client.get("/api/v1/categories").json() if c["code"] == "ROAD_POTHOLE")
    incident = client.post(
        "/api/v1/incidents",
        headers=auth(moderator_token),
        json={
            "category_id": road_cat["id"],
            "title": "Kissy Road Deep Asphalt Pothole Hazard",
            "summary": "Dangerous road depression requiring an urgent asphalt patch.",
            "priority": "HIGH",
            "report_id": rep1["id"],
        },
    ).json()

    client.post(
        f"/api/v1/moderation/reports/{rep2['id']}/decision",
        headers=auth(moderator_token),
        json={
            "decision": "MERGE",
            "reason": "Duplicate report of the same Kissy Road pothole.",
            "target_incident_id": incident["id"],
        },
    )

    fcc = next(i for i in client.get("/api/v1/institutions").json() if "Freetown City Council" in i["name"])
    assignment = client.post(
        f"/api/v1/incidents/{incident['id']}/assignments",
        headers=auth(moderator_token),
        json={"institution_id": fcc["id"]},
    ).json()
    client.patch(
        f"/api/v1/assignments/{assignment['id']}/status",
        headers=auth(officer_token),
        json={"status": "ACCEPTED"},
    )

    evidence = client.post(
        f"/api/v1/incidents/{incident['id']}/resolution-evidence",
        headers=auth(officer_token),
        json={"description": "Asphalt levelling and compaction completed by the FCC maintenance crew."},
    ).json()

    buf = io.BytesIO()
    Image.new("RGB", (120, 80), color="gray").save(buf, format="JPEG")
    client.post(
        f"/api/v1/incidents/{incident['id']}/resolution-evidence/{evidence['id']}/media",
        headers={**auth(officer_token), "Idempotency-Key": "baseline-metrics-photo"},
        files={"file": ("after_repair.jpg", buf.getvalue(), "image/jpeg")},
    )

    client.post(
        f"/api/v1/incidents/{incident['id']}/resolution-review",
        headers=auth(moderator_token),
        json={"decision": "APPROVED", "reason": "Clear maintenance proof provided."},
    )
    client.post(
        f"/api/v1/incidents/{incident['id']}/disputes",
        headers=auth(citizen_token),
        json={"reason": "The patch broke open again after heavy rainfall."},
    )
    return {"report_ids": [rep1["id"], rep2["id"]], "incident_id": incident["id"]}


# ----------------------------------------------------------------- authorization
def test_baseline_metrics_readable_by_admin_and_auditor(client, admin_token, auditor_token):
    for token in (admin_token, auditor_token):
        resp = client.get(BASELINE, headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["interpretation_note"]


def test_baseline_metrics_forbidden_for_other_roles(client, citizen_token, moderator_token, officer_token):
    """Cross-case aggregates are programme data. A moderator must not be able to
    read their own scorecard next to a colleague's."""
    for token in (citizen_token, moderator_token, officer_token):
        resp = client.get(BASELINE, headers=auth(token))
        assert resp.status_code == 403
        assert resp.json()["error_code"] == "FORBIDDEN"


def test_baseline_metrics_requires_authentication(client):
    resp = client.get(BASELINE)
    assert resp.status_code == 401


# ----------------------------------------------------------------------- honesty
def test_empty_window_reports_no_value_rather_than_zero(client, admin_token):
    """A window with no activity has no rate. Returning 0.0 would read as
    'nothing was ever merged', which is a different and false claim."""
    resp = client.get(BASELINE, params={"from": "2000-01-01T00:00:00", "to": "2000-01-02T00:00:00"}, headers=auth(admin_token))
    assert resp.status_code == 200
    payload = resp.json()

    assert payload["volumes"]["reports_submitted"] == 0
    for key in ("report_completion_rate", "duplicate_identification_rate", "median_review_seconds", "audit_completeness"):
        m = metric(payload, key)
        assert m["value"] is None, f"{key} should be null on an empty window, got {m['value']}"
        assert m["sample_size"] == 0


def test_ground_truth_metrics_are_declared_unavailable_not_guessed(client, admin_token):
    payload = client.get(BASELINE, headers=auth(admin_token)).json()

    unavailable = {u["key"]: u for u in payload["unavailable_metrics"]}
    assert set(unavailable) == {"correct_category_rate", "correct_routing_rate", "usability_score"}
    for entry in unavailable.values():
        assert entry["reason"]
        assert entry["how_to_collect"]

    # They must not also appear as computed metrics.
    computed = {m["key"] for m in payload["metrics"]}
    assert computed.isdisjoint(unavailable)


def test_every_metric_carries_its_own_definition(client, admin_token):
    """A frozen baseline is read long after this code changes."""
    payload = client.get(BASELINE, headers=auth(admin_token)).json()
    assert payload["metrics"]
    for m in payload["metrics"]:
        assert m["definition"].strip(), f"{m['key']} has no definition"
        assert m["unit"] in {"ratio", "seconds", "count"}


def test_export_records_the_phase_flags_that_make_it_a_human_only_baseline(client, admin_token):
    payload = client.get(BASELINE, headers=auth(admin_token)).json()
    assert payload["ai_enabled"] is False
    assert payload["whatsapp_enabled"] is False
    assert payload["phase"] == "Human-First Foundation Launch"


# ---------------------------------------------------------------------- accuracy
def test_metrics_reflect_a_complete_human_lifecycle(
    client, citizen_token, moderator_token, officer_token, admin_token
):
    run_full_lifecycle(client, citizen_token, moderator_token, officer_token)
    payload = client.get(BASELINE, headers=auth(admin_token)).json()

    assert payload["volumes"] == {
        "reports_submitted": 2,
        "moderation_decisions": 2,
        "incidents_created": 1,
        "assignments_made": 1,
        "resolution_evidence_submitted": 1,
        "disputes_filed": 1,
    }

    # Both reports reached a terminal outcome (VERIFIED and MERGED).
    assert metric(payload, "report_completion_rate")["value"] == 1.0
    # One of the two decisions was a merge.
    assert metric(payload, "duplicate_identification_rate")["value"] == 0.5
    assert metric(payload, "clarification_rate")["value"] == 0.0
    # The single piece of evidence was approved; the resolution was then disputed.
    assert metric(payload, "resolution_evidence_agreement")["value"] == 1.0
    assert metric(payload, "dispute_rate")["value"] == 1.0
    # The assignment was accepted, not declined.
    assert metric(payload, "assignment_decline_rate")["value"] == 0.0
    # Every material action in a clean run left an audit event.
    assert metric(payload, "audit_completeness")["value"] == 1.0

    review = metric(payload, "median_review_seconds")
    assert review["sample_size"] == 2
    assert review["value"] >= 0


def test_moderator_workload_attributes_decisions_to_the_acting_moderator(
    client, citizen_token, moderator_token, officer_token, admin_token
):
    run_full_lifecycle(client, citizen_token, moderator_token, officer_token)
    payload = client.get(BASELINE, headers=auth(admin_token)).json()

    assert len(payload["moderator_workload"]) == 1
    entry = payload["moderator_workload"][0]
    assert entry["decisions"] == 2
    assert entry["name_or_alias"]


def test_audit_completeness_falls_below_one_when_an_event_is_missing(
    client, db_session, citizen_token, moderator_token, officer_token, admin_token
):
    """The metric exists to catch a broken audit trail, so prove it can fail."""
    run_full_lifecycle(client, citizen_token, moderator_token, officer_token)
    assert metric(client.get(BASELINE, headers=auth(admin_token)).json(), "audit_completeness")["value"] == 1.0

    from app.models.entities import AuditEvent

    orphaned = db_session.query(AuditEvent).filter(AuditEvent.action == "INCIDENT_ASSIGNED").first()
    assert orphaned is not None
    db_session.delete(orphaned)
    db_session.commit()

    degraded = metric(client.get(BASELINE, headers=auth(admin_token)).json(), "audit_completeness")
    assert degraded["value"] < 1.0


def test_window_bounds_filter_activity_out(client, citizen_token, moderator_token, officer_token, admin_token):
    run_full_lifecycle(client, citizen_token, moderator_token, officer_token)
    past = client.get(
        BASELINE,
        params={"from": "2000-01-01T00:00:00", "to": "2000-12-31T00:00:00"},
        headers=auth(admin_token),
    ).json()
    assert past["volumes"]["reports_submitted"] == 0

    everything = client.get(BASELINE, headers=auth(admin_token)).json()
    assert everything["volumes"]["reports_submitted"] == 2


def test_inverted_window_is_rejected(client, admin_token):
    resp = client.get(
        BASELINE,
        params={"from": "2026-01-02T00:00:00", "to": "2026-01-01T00:00:00"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 422
    assert resp.json()["error_code"] == "VALIDATION_ERROR"


# ------------------------------------------------------------ reviewer agreement
def test_reviewer_agreement_counts_only_independently_double_reviewed_reports(
    client, db_session, citizen_token, moderator_token, admin_token
):
    """The normal workflow records one decision per report, so the sample is
    empty until a deliberate double-review exercise is run. It must report an
    empty sample rather than a flattering 100%."""
    report = client.post(
        "/api/v1/reports",
        headers=auth(citizen_token),
        json={
            "category_code": "DRAINAGE_FLOODING",
            "description": "Blocked drain flooding the lane after every rainfall.",
            "latitude": 8.4800,
            "longitude": -13.2400,
            "location_precision": "APPROXIMATE",
        },
    ).json()

    client.post(
        f"/api/v1/moderation/reports/{report['id']}/decision",
        headers=auth(moderator_token),
        json={"decision": "VERIFY", "reason": "Confirmed drainage blockage affecting residents."},
    )

    single = metric(client.get(BASELINE, headers=auth(admin_token)).json(), "reviewer_agreement")
    assert single["sample_size"] == 0
    assert single["value"] is None

    # A second moderator independently reviews the same report and agrees.
    second = client.post(
        "/api/v1/admin/users",
        headers=auth(admin_token),
        json={
            "name_or_alias": "Second Reviewer",
            "contact": "moderator2@salonefix.gov.sl",
            "password": "ModPass456!",
            "role": "MODERATOR",
        },
    )
    assert second.status_code == 201

    from app.core.security import create_access_token

    second_token = create_access_token({"sub": second.json()["id"], "role": "MODERATOR"})
    client.post(
        f"/api/v1/moderation/reports/{report['id']}/decision",
        headers=auth(second_token),
        json={"decision": "VERIFY", "reason": "Independent second review reaches the same conclusion."},
    )

    agreed = metric(client.get(BASELINE, headers=auth(admin_token)).json(), "reviewer_agreement")
    assert agreed["sample_size"] == 1
    assert agreed["value"] == 1.0


# ------------------------------------------------------------------------- audit
def test_exporting_the_baseline_is_itself_audited(client, db_session, admin_token):
    from app.models.entities import AuditEvent

    before = db_session.query(AuditEvent).filter(AuditEvent.action == "BASELINE_METRICS_EXPORTED").count()
    assert client.get(BASELINE, headers=auth(admin_token)).status_code == 200
    after = db_session.query(AuditEvent).filter(AuditEvent.action == "BASELINE_METRICS_EXPORTED").count()
    assert after == before + 1


def test_metrics_export_audit_events_do_not_inflate_audit_completeness(
    client, citizen_token, moderator_token, officer_token, admin_token
):
    """Reading the metrics writes an audit event; that event must not be counted
    as coverage of a material workflow action."""
    run_full_lifecycle(client, citizen_token, moderator_token, officer_token)
    first = metric(client.get(BASELINE, headers=auth(admin_token)).json(), "audit_completeness")
    second = metric(client.get(BASELINE, headers=auth(admin_token)).json(), "audit_completeness")
    assert first["sample_size"] == second["sample_size"]
    assert first["value"] == second["value"] == 1.0
