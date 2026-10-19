import io

import pytest
from PIL import Image

from app.core.config import settings


def test_tc_011_audit_read_access_restricted_and_logged(
    client,
    citizen_token,
    officer_token,
    auditor_token,
    moderator_token,
):
    """
    TC-011: Audit read access.
    1. Unauthorized roles (CITIZEN, unassigned roles) must be rejected with 403.
    2. Authorized roles (AUDITOR, ADMIN) can read audit trail.
    3. Every audit access must itself be logged as AUDIT_ACCESSED.
    """
    # 1. Create a test incident as moderator
    cats = client.get("/api/v1/categories").json()
    cat = cats[0]
    incident = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "category_id": cat["id"],
            "title": "Audit Access Verification Incident",
            "summary": "Verifying that audit trail reading is permission-controlled and logged.",
            "priority": "LOW",
        },
    ).json()

    # 2. Citizen attempts to view incident audit -> 403 Forbidden
    resp_citizen = client.get(
        f"/api/v1/incidents/{incident['id']}/audit",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert resp_citizen.status_code == 403

    # 3. Citizen attempts to view global audit events -> 403 Forbidden
    resp_citizen_all = client.get(
        "/api/v1/events",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert resp_citizen_all.status_code == 403

    # 4. Officer attempts to view global audit events -> 403 Forbidden
    resp_officer_all = client.get(
        "/api/v1/events",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp_officer_all.status_code == 403

    # 5. Auditor views incident audit -> 200 OK
    resp_auditor = client.get(
        f"/api/v1/incidents/{incident['id']}/audit",
        headers={"Authorization": f"Bearer {auditor_token}"},
    )
    assert resp_auditor.status_code == 200
    events = resp_auditor.json()
    assert len(events) >= 1

    # 6. Verify that accessing the audit trail logged an AUDIT_ACCESSED action
    resp_global = client.get(
        "/api/v1/events",
        headers={"Authorization": f"Bearer {auditor_token}"},
    )
    assert resp_global.status_code == 200
    global_events = resp_global.json()
    audit_access_actions = [e for e in global_events if e["action"] == "AUDIT_ACCESSED"]
    assert len(audit_access_actions) >= 1


def test_tc_012_ai_disabled_complete_human_workflow_succeeds(client, citizen_token, moderator_token):
    """
    TC-012: System operates 100% reliably with AI disabled.
    Verifies that default config has AI disabled and core lifecycle works completely
    with human-accountable decisions only.
    """
    assert settings.AI_ENABLED is False

    # Citizen submits report
    rep = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Hazardous road crater on Main Motor Road.",
            "latitude": 8.472,
            "longitude": -13.250,
        },
    ).json()
    assert rep["status"] == "SUBMITTED"

    # Human moderator verifies report without AI recommendation requirement
    mod_resp = client.post(
        f"/api/v1/moderation/reports/{rep['id']}/decision",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "decision": "VERIFY",
            "reason": "Human verified road defect based on citizen submitted details.",
        },
    )
    assert mod_resp.status_code == 200
    assert mod_resp.json()["current_status"] == "VERIFIED"


def test_tc_013_future_ai_provider_unavailable_human_fallback(client, citizen_token, moderator_token):
    """
    TC-013: Future AI provider unavailable or throwing error does not impede human reporting.
    Simulates environment where AI credentials are absent/unavailable.
    """
    assert settings.AI_API_KEY is None or settings.AI_API_KEY == ""

    # Submission must succeed cleanly
    rep = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "DRAINAGE_FLOODING",
            "description": "Drain blocked by storm debris near Congo Cross.",
            "latitude": 8.479,
            "longitude": -13.255,
        },
    )
    assert rep.status_code == 200
    data = rep.json()
    assert data["status"] == "SUBMITTED"
    assert "A moderator will review" in data["next_step"]


def test_tc_014_repeated_submit_request_idempotency(client, citizen_token):
    """
    TC-014: Repeated submit request.
    Idempotency key prevents duplicate reports and duplicate audit log generation.
    """
    idemp_key = "IDEMP-KEY-TEST-FREETOWN-001"
    headers = {
        "Authorization": f"Bearer {citizen_token}",
        "Idempotency-Key": idemp_key,
    }
    payload = {
        "category_code": "PUBLIC_FACILITIES",
        "description": "Broken municipal light pole leaning near market stall.",
        "latitude": 8.481,
        "longitude": -13.231,
    }

    # First submission
    resp1 = client.post("/api/v1/reports", headers=headers, json=payload)
    assert resp1.status_code == 200
    data1 = resp1.json()

    # Second submission with identical Idempotency-Key
    resp2 = client.post("/api/v1/reports", headers=headers, json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()

    # Must return the identical report entity
    assert data1["id"] == data2["id"]
    assert data1["tracking_reference"] == data2["tracking_reference"]

    # Debounce verification: second submit without key within 5 seconds returns existing
    resp_quick = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json=payload,
    )
    assert resp_quick.status_code == 200
    assert resp_quick.json()["id"] == data1["id"]


def test_tc_015_public_map_access_exact_restricted_location_not_exposed(
    client,
    citizen_token,
    moderator_token,
):
    """
    TC-015: Public map access.
    Exact high-precision coordinates are not exposed in public map or tracking views.
    Coordinates on public map are generalized to 2 decimal places (~1.1 km).
    """
    exact_lat = 8.484987654
    exact_lon = -13.229876543

    # 1. Citizen submits report with high-precision GPS
    rep = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Critical road crater requiring coordinates check.",
            "latitude": exact_lat,
            "longitude": exact_lon,
            "location_precision": "EXACT",
        },
    ).json()

    # 2. Moderator verifies and creates incident
    cats = client.get("/api/v1/categories").json()
    cat = next(c for c in cats if c["code"] == "ROAD_POTHOLE")
    incident = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "category_id": cat["id"],
            "title": "Road Defect Precision Protection Test",
            "summary": "Verifying coordinates generalization on public endpoints.",
            "priority": "MEDIUM",
            "report_id": rep["id"],
        },
    ).json()

    # 3. Query public tracking status: exact coordinates must NOT be present in public schema
    tracking_resp = client.get(f"/api/v1/reports/{rep['tracking_reference']}/status")
    assert tracking_resp.status_code == 200
    tracking_data = tracking_resp.json()
    assert "latitude" not in tracking_data
    assert "longitude" not in tracking_data

    # 4. Query public map: coordinates must be generalized (approx 2 decimals)
    pub_map_resp = client.get("/api/v1/incidents/public/map")
    assert pub_map_resp.status_code == 200
    map_items = pub_map_resp.json()
    inc_item = next((item for item in map_items if item["id"] == incident["id"]), None)
    assert inc_item is not None

    # Verify coordinates are generalized and do NOT match exact 9-decimal floating point
    assert inc_item["approx_latitude"] == round(exact_lat, 2)
    assert inc_item["approx_longitude"] == round(exact_lon, 2)
    assert inc_item["approx_latitude"] != exact_lat
    assert inc_item["approx_longitude"] != exact_lon


# ---------------------------------------------------------------------------
# Helpers for TC-008 / TC-009 / TC-010.
#
# Each of those cases needs an incident at a particular point in the lifecycle.
# Driving it through the real HTTP endpoints (rather than writing rows) is the
# point: it is the transitions and their guards that the acceptance cases are
# about.
# ---------------------------------------------------------------------------

def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _jpeg_bytes():
    img = Image.new("RGB", (120, 80), color="gray")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _incident_assigned_to_fcc(client, citizen_token, moderator_token):
    """Citizen report -> verified -> incident -> assigned to FCC (not yet accepted)."""
    report = client.post(
        "/api/v1/reports",
        headers=_auth(citizen_token),
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Collapsed road edge on Circular Road forcing traffic into oncoming lane.",
            "latitude": 8.4790,
            "longitude": -13.2460,
            "location_precision": "EXACT",
        },
    ).json()

    client.post(
        f"/api/v1/moderation/reports/{report['id']}/decision",
        headers=_auth(moderator_token),
        json={"decision": "VERIFY", "reason": "Confirmed road hazard requiring an institutional response."},
    )

    category = next(c for c in client.get("/api/v1/categories").json() if c["code"] == "ROAD_POTHOLE")
    incident = client.post(
        "/api/v1/incidents",
        headers=_auth(moderator_token),
        json={
            "category_id": category["id"],
            "title": "Circular Road Collapsed Carriageway Edge",
            "summary": "Road edge failure requiring municipal repair before the next rains.",
            "priority": "HIGH",
            "report_id": report["id"],
        },
    ).json()

    institution = next(i for i in client.get("/api/v1/institutions").json() if "Freetown City Council" in i["name"])
    assignment = client.post(
        f"/api/v1/incidents/{incident['id']}/assignments",
        headers=_auth(moderator_token),
        json={"institution_id": institution["id"]},
    ).json()

    return {"report": report, "incident": incident, "assignment": assignment}


def _incident_resolved(client, citizen_token, moderator_token, officer_token):
    """Carry on to RESOLVED: officer accepts, submits evidence with a photo, moderator approves."""
    ctx = _incident_assigned_to_fcc(client, citizen_token, moderator_token)
    incident_id = ctx["incident"]["id"]

    client.patch(
        f"/api/v1/assignments/{ctx['assignment']['id']}/status",
        headers=_auth(officer_token),
        json={"status": "ACCEPTED"},
    )
    evidence = client.post(
        f"/api/v1/incidents/{incident_id}/resolution-evidence",
        headers=_auth(officer_token),
        json={"description": "Carriageway edge rebuilt and compacted by the FCC works crew."},
    ).json()
    client.post(
        f"/api/v1/incidents/{incident_id}/resolution-evidence/{evidence['id']}/media",
        headers={**_auth(officer_token), "Idempotency-Key": "tc-evidence-photo"},
        files={"file": ("repaired.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    client.post(
        f"/api/v1/incidents/{incident_id}/resolution-review",
        headers=_auth(moderator_token),
        json={"decision": "APPROVED", "reason": "Repair evidence matches the reported defect."},
    )
    ctx["evidence"] = evidence
    return ctx


def _audit_actions(client, incident_id, auditor_token):
    events = client.get(f"/api/v1/incidents/{incident_id}/audit", headers=_auth(auditor_token)).json()
    return [e["action"] for e in events]


def test_tc_008_officer_submits_evidence(
    client, citizen_token, moderator_token, officer_token, slra_officer_token, auditor_token
):
    """
    TC-008: Officer submits evidence.
    Expected: evidence stored and a review state created.

    1. A citizen cannot submit resolution evidence.
    2. An officer from an institution the case is not assigned to cannot.
    3. Evidence cannot be submitted before the assignment is accepted (invalid state).
    4. The assigned officer can; the evidence is stored PENDING and the incident
       moves to RESOLUTION_UNDER_REVIEW.
    5. The submission is recorded in the audit trail.
    """
    ctx = _incident_assigned_to_fcc(client, citizen_token, moderator_token)
    incident_id = ctx["incident"]["id"]
    body = {"description": "Resolution evidence description for the Circular Road repair."}

    # 1. Wrong role entirely.
    assert client.post(
        f"/api/v1/incidents/{incident_id}/resolution-evidence", headers=_auth(citizen_token), json=body
    ).status_code == 403

    # 2. Right role, wrong institution.
    other_institution = client.post(
        f"/api/v1/incidents/{incident_id}/resolution-evidence", headers=_auth(slra_officer_token), json=body
    )
    assert other_institution.status_code == 403
    assert other_institution.json()["error_code"] == "FORBIDDEN"

    # 3. Assigned officer, but the assignment has not been accepted yet.
    too_early = client.post(
        f"/api/v1/incidents/{incident_id}/resolution-evidence", headers=_auth(officer_token), json=body
    )
    assert too_early.status_code == 409
    assert too_early.json()["error_code"] == "STATE_CONFLICT"

    # 4. Accept the assignment, then submit.
    client.patch(
        f"/api/v1/assignments/{ctx['assignment']['id']}/status",
        headers=_auth(officer_token),
        json={"status": "ACCEPTED"},
    )
    submitted = client.post(
        f"/api/v1/incidents/{incident_id}/resolution-evidence",
        headers=_auth(officer_token),
        json={"description": "Carriageway edge rebuilt and compacted by the FCC works crew."},
    )
    assert submitted.status_code == 200
    evidence = submitted.json()

    # Evidence is stored awaiting a human review decision - never auto-approved.
    assert evidence["review_status"] == "PENDING"
    assert evidence["media_assets"] == []

    incident = client.get(f"/api/v1/incidents/{incident_id}", headers=_auth(moderator_token)).json()
    assert incident["lifecycle_status"] == "RESOLUTION_UNDER_REVIEW"
    assert len(incident["resolution_evidence"]) == 1

    # 5. Audit trail records the submission.
    assert "RESOLUTION_EVIDENCE_SUBMITTED" in _audit_actions(client, incident_id, auditor_token)


def test_tc_009_citizen_disputes_resolution(
    client, citizen_token, moderator_token, officer_token, auditor_token
):
    """
    TC-009: Citizen disputes resolution.
    Expected: incident enters the disputed/review state.

    1. A resolution cannot be disputed before it exists (invalid state).
    2. A citizen with no report linked to the case cannot dispute it.
    3. The reporting citizen can; the incident moves to DISPUTED and the dispute
       is recorded with their reason.
    4. The dispute is recorded in the audit trail.
    """
    # 1. Dispute an incident that is still under review, not resolved.
    unresolved = _incident_assigned_to_fcc(client, citizen_token, moderator_token)
    premature = client.post(
        f"/api/v1/incidents/{unresolved['incident']['id']}/disputes",
        headers=_auth(citizen_token),
        json={"reason": "Trying to dispute before any resolution was proposed."},
    )
    assert premature.status_code == 409
    assert premature.json()["error_code"] == "STATE_CONFLICT"

    ctx = _incident_resolved(client, citizen_token, moderator_token, officer_token)
    incident_id = ctx["incident"]["id"]
    assert client.get(f"/api/v1/incidents/{incident_id}", headers=_auth(moderator_token)).json()[
        "lifecycle_status"
    ] == "RESOLVED"

    # 2. An unrelated citizen must not be able to dispute someone else's case.
    outsider = client.post(
        "/api/v1/auth/register",
        json={
            "name_or_alias": "Unrelated Resident",
            "contact": "outsider@freetown.sl",
            "password": "OutsiderPass123!",
            "consent_status": True,
        },
    ).json()
    stranger = client.post(
        f"/api/v1/incidents/{incident_id}/disputes",
        headers=_auth(outsider["access_token"]),
        json={"reason": "I have nothing to do with this case but want it reopened."},
    )
    assert stranger.status_code == 403
    assert stranger.json()["error_code"] == "FORBIDDEN"

    # 3. The reporting citizen disputes the resolution.
    reason = "The patch broke open again after the first heavy rainfall; the hazard is still there."
    disputed = client.post(
        f"/api/v1/incidents/{incident_id}/disputes",
        headers=_auth(citizen_token),
        json={"reason": reason},
    )
    assert disputed.status_code == 200
    assert disputed.json()["status"] == "SUBMITTED"
    assert disputed.json()["reason"] == reason

    incident = client.get(f"/api/v1/incidents/{incident_id}", headers=_auth(moderator_token)).json()
    assert incident["lifecycle_status"] == "DISPUTED"

    # 4. Audit trail records the dispute and preserves the citizen's reason.
    events = client.get(f"/api/v1/incidents/{incident_id}/audit", headers=_auth(auditor_token)).json()
    dispute_events = [e for e in events if e["action"] == "RESOLUTION_DISPUTED"]
    assert len(dispute_events) == 1
    assert dispute_events[0]["reason"] == reason


def test_tc_010_reviewer_reopens_case(
    client, citizen_token, moderator_token, officer_token, auditor_token
):
    """
    TC-010: Reviewer reopens case.
    Expected: valid transition and an audit event.

    1. An incident still being worked on cannot be reopened (invalid state).
    2. Citizens and officers cannot reopen a case.
    3. A moderator can; the incident returns to RESOLUTION_UNDER_REVIEW and the
       open dispute is marked ACCEPTED.
    4. The reopening is recorded in the audit trail with the reviewer's reason.
    """
    # 1. Reopening something that was never resolved is not a valid transition.
    in_progress = _incident_assigned_to_fcc(client, citizen_token, moderator_token)
    client.patch(
        f"/api/v1/assignments/{in_progress['assignment']['id']}/status",
        headers=_auth(officer_token),
        json={"status": "ACCEPTED"},
    )
    invalid = client.post(
        f"/api/v1/incidents/{in_progress['incident']['id']}/reopen",
        headers=_auth(moderator_token),
        json={"reason": "Attempting to reopen a case that is still being worked on."},
    )
    assert invalid.status_code == 409
    assert invalid.json()["error_code"] == "STATE_CONFLICT"

    # Drive a second case all the way to DISPUTED.
    ctx = _incident_resolved(client, citizen_token, moderator_token, officer_token)
    incident_id = ctx["incident"]["id"]
    client.post(
        f"/api/v1/incidents/{incident_id}/disputes",
        headers=_auth(citizen_token),
        json={"reason": "The repair did not hold; the defect has reappeared."},
    )

    # 2. Reopening is a reviewer decision, not something the parties can force.
    for token in (citizen_token, officer_token):
        refused = client.post(
            f"/api/v1/incidents/{incident_id}/reopen",
            headers=_auth(token),
            json={"reason": "Forcing a reopen without review authority."},
        )
        assert refused.status_code == 403

    # 3. Moderator reopens the case.
    reason = "Citizen dispute is credible; sending the case back for a second inspection."
    reopened = client.post(
        f"/api/v1/incidents/{incident_id}/reopen",
        headers=_auth(moderator_token),
        json={"reason": reason},
    )
    assert reopened.status_code == 200
    assert reopened.json()["lifecycle_status"] == "RESOLUTION_UNDER_REVIEW"

    incident = client.get(f"/api/v1/incidents/{incident_id}", headers=_auth(moderator_token)).json()
    assert incident["disputes"][0]["status"] == "ACCEPTED"

    # 4. Audit trail records the reopen, with the reason and the previous state.
    events = client.get(f"/api/v1/incidents/{incident_id}/audit", headers=_auth(auditor_token)).json()
    reopen_events = [e for e in events if e["action"] == "INCIDENT_REOPENED"]
    assert len(reopen_events) == 1
    assert reopen_events[0]["reason"] == reason
    assert "DISPUTED" in reopen_events[0]["previous_value"]

    # The earlier evidence is still on the record: reopening reviews history, never erases it.
    assert len(incident["resolution_evidence"]) == 1
