import pytest
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
