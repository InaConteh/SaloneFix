import io
from PIL import Image
def test_tc_007_unauthorized_status_change_rejected(client, citizen_token, moderator_token):
    # Create an incident as moderator
    cats = client.get("/api/v1/categories").json()
    cat = cats[0]

    incident = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "category_id": cat["id"],
            "title": "Unauthorized Status Change Test Incident",
            "summary": "Testing RBAC protection on lifecycle status.",
            "priority": "LOW",
        },
    ).json()

    # Citizen attempts to force incident status to CLOSED (unauthorized!)
    citizen_attack = client.patch(
        f"/api/v1/incidents/{incident['id']}/status",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={"status": "CLOSED", "reason": "Citizen trying to force closure"},
    )
    assert citizen_attack.status_code == 403


def test_officer_cannot_mutate_incident_assigned_to_another_institution(
    client,
    citizen_token,
    moderator_token,
    slra_officer_token,
):
    rep = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Large pothole near Wilkinson Road blocking one lane.",
            "latitude": 8.462,
            "longitude": -13.267,
            "location_precision": "EXACT",
        },
    ).json()
    cat = next(c for c in client.get("/api/v1/categories").json() if c["code"] == "ROAD_POTHOLE")
    incident = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "category_id": cat["id"],
            "title": "Wilkinson Road Lane Blocking Pothole",
            "summary": "Road hazard requiring municipal assessment and repair.",
            "priority": "HIGH",
            "report_id": rep["id"],
        },
    ).json()
    fcc = next(i for i in client.get("/api/v1/institutions").json() if "Freetown City Council" in i["name"])
    client.post(
        f"/api/v1/incidents/{incident['id']}/assignments",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={"institution_id": fcc["id"]},
    )

    status_resp = client.patch(
        f"/api/v1/incidents/{incident['id']}/status",
        headers={"Authorization": f"Bearer {slra_officer_token}"},
        json={"status": "IN_PROGRESS", "reason": "Wrong institution attempting work."},
    )
    assert status_resp.status_code == 403

    evidence_resp = client.post(
        f"/api/v1/incidents/{incident['id']}/resolution-evidence",
        headers={"Authorization": f"Bearer {slra_officer_token}"},
        json={"description": "Attempted evidence from a non-assigned institution."},
    )
    assert evidence_resp.status_code == 403


def test_complete_demonstration_lifecycle_with_dispute_and_audit(
    client,
    citizen_token,
    moderator_token,
    officer_token,
    auditor_token,
):
    """
    Demonstrates the complete end-to-end lifecycle specified in PRD Section 13:
    1. Citizen submits report.
    2. Moderator reviews and verifies it.
    3. Moderator links/merges second report into single incident case.
    4. Incident is assigned to institution (FCC).
    5. Officer accepts assignment and updates status to IN_PROGRESS.
    6. Officer submits resolution evidence (repairs completed).
    7. Moderator reviews and approves resolution evidence -> incident becomes RESOLVED.
    8. Citizen inspects and files a dispute -> incident enters DISPUTED.
    9. Moderator reopens the case for reinvestigation.
    10. Auditor inspects the complete append-only audit trail.
    """
    # 1. Citizen submits report 1
    rep1_resp = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Large deep pothole on Kissy Road opposite UMC Primary School.",
            "latitude": 8.4851,
            "longitude": -13.2285,
            "location_precision": "EXACT",
        },
    )
    assert rep1_resp.status_code == 200
    rep1 = rep1_resp.json()

    # 2. Citizen submits report 2 (duplicate report on same pothole)
    rep2_resp = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Road surface crater near Kissy Road school slowing all traffic.",
            "latitude": 8.4853,
            "longitude": -13.2287,
            "location_precision": "APPROXIMATE",
        },
    )
    assert rep2_resp.status_code == 200
    rep2 = rep2_resp.json()

    # 3. Moderator verifies report 1
    mod_verify = client.post(
        f"/api/v1/moderation/reports/{rep1['id']}/decision",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "decision": "VERIFY",
            "reason": "Verified as genuine public road hazard requiring institutional response.",
        },
    )
    assert mod_verify.status_code == 200

    # 4. Moderator creates incident case seeded with report 1
    cats = client.get("/api/v1/categories").json()
    road_cat = next(c for c in cats if c["code"] == "ROAD_POTHOLE")

    incident_resp = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "category_id": road_cat["id"],
            "title": "Kissy Road Deep Asphalt Pothole Hazard",
            "summary": "Dangerous road depression requiring urgent asphalt patch and resurfacing.",
            "priority": "HIGH",
            "report_id": rep1["id"],
        },
    )
    assert incident_resp.status_code == 200
    incident = incident_resp.json()

    # 5. Moderator links report 2 as duplicate
    merge_resp = client.post(
        f"/api/v1/moderation/reports/{rep2['id']}/decision",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "decision": "MERGE",
            "reason": "Duplicate report of same Kissy Road pothole.",
            "target_incident_id": incident["id"],
        },
    )
    assert merge_resp.status_code == 200

    # 6. Assign to Freetown City Council
    institutions = client.get("/api/v1/institutions").json()
    fcc = next(i for i in institutions if "Freetown City Council" in i["name"])

    assign_resp = client.post(
        f"/api/v1/incidents/{incident['id']}/assignments",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={"institution_id": fcc["id"]},
    )
    assert assign_resp.status_code == 200
    assignment = assign_resp.json()

    # 7. FCC Officer accepts assignment -> Incident transitions to IN_PROGRESS
    accept_resp = client.patch(
        f"/api/v1/assignments/{assignment['id']}/status",
        headers={"Authorization": f"Bearer {officer_token}"},
        json={"status": "ACCEPTED"},
    )
    assert accept_resp.status_code == 200

    inc_check = client.get(
        f"/api/v1/incidents/{incident['id']}",
        headers={"Authorization": f"Bearer {officer_token}"},
    ).json()
    assert inc_check["lifecycle_status"] == "IN_PROGRESS"

    # 8. FCC Officer submits resolution evidence
    evidence_resp = client.post(
        f"/api/v1/incidents/{incident['id']}/resolution-evidence",
        headers={"Authorization": f"Bearer {officer_token}"},
        json={
            "description": "Asphalt leveling and compaction completed by FCC maintenance crew. Road fully restored.",
        },
    )
    assert evidence_resp.status_code == 200
    evidence = evidence_resp.json()
    assert evidence["media_assets"] == []

    # 8b. ROAD_POTHOLE requires photo evidence: approval without media is refused
    premature = client.post(
        f"/api/v1/incidents/{incident['id']}/resolution-review",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={"decision": "APPROVED", "reason": "Trying to approve without proof."},
    )
    assert premature.status_code == 409
    assert premature.json()["error_code"] == "STATE_CONFLICT"

    # 8c. Officer attaches a sanitized photo to the evidence record (idempotent)
    img = Image.new("RGB", (120, 80), color="gray")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    for _ in range(2):
        media_resp = client.post(
            f"/api/v1/incidents/{incident['id']}/resolution-evidence/{evidence['id']}/media",
            headers={"Authorization": f"Bearer {officer_token}", "Idempotency-Key": "evidence-photo-1"},
            files={"file": ("after_repair.jpg", buf.getvalue(), "image/jpeg")},
        )
        assert media_resp.status_code == 200
    inc_with_evidence = client.get(
        f"/api/v1/incidents/{incident['id']}",
        headers={"Authorization": f"Bearer {moderator_token}"},
    ).json()
    assert len(inc_with_evidence["resolution_evidence"]) == 1
    assert len(inc_with_evidence["resolution_evidence"][0]["media_assets"]) == 1  # retry did not duplicate
    assert "token=" in inc_with_evidence["resolution_evidence"][0]["media_assets"][0]["url"]

    # 9. Moderator reviews and approves resolution evidence -> Incident becomes RESOLVED
    review_resp = client.post(
        f"/api/v1/incidents/{incident['id']}/resolution-review",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "decision": "APPROVED",
            "reason": "Clear maintenance proof provided. Road reopened safely.",
        },
    )
    assert review_resp.status_code == 200
    resolved_inc = review_resp.json()
    assert resolved_inc["lifecycle_status"] == "RESOLVED"

    # 10. Citizen checks public status -> sees RESOLVED and can dispute
    tracking = client.get(f"/api/v1/reports/{rep1['tracking_reference']}/status").json()
    assert tracking["can_dispute"] is True

    # 11. Citizen disputes resolution
    dispute_resp = client.post(
        f"/api/v1/incidents/{incident['id']}/disputes",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "reason": "The asphalt patch broke open again after heavy rainfall. Pothole is still present.",
        },
    )
    assert dispute_resp.status_code == 200
    dispute = dispute_resp.json()
    assert dispute["status"] == "SUBMITTED"

    # 12. Moderator reopens the incident
    reopen_resp = client.post(
        f"/api/v1/incidents/{incident['id']}/reopen",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "reason": "Reopening incident following citizen dispute. Re-dispatching engineering team.",
        },
    )
    assert reopen_resp.status_code == 200
    reopened_inc = reopen_resp.json()
    assert reopened_inc["lifecycle_status"] == "RESOLUTION_UNDER_REVIEW"

    # 13. Auditor inspects the complete audit trail
    audit_resp = client.get(
        f"/api/v1/incidents/{incident['id']}/audit",
        headers={"Authorization": f"Bearer {auditor_token}"},
    )
    assert audit_resp.status_code == 200
    audit_events = audit_resp.json()
    assert len(audit_events) >= 6

    actions = [ev["action"] for ev in audit_events]
    assert "INCIDENT_CREATED" in actions
    assert "MODERATION_MERGE" in actions or "REPORT_LINKED" in actions
    assert "INCIDENT_ASSIGNED" in actions
    assert "ASSIGNMENT_ACCEPTED" in actions
    assert "RESOLUTION_EVIDENCE_SUBMITTED" in actions
    assert "RESOLUTION_APPROVED" in actions
    assert "RESOLUTION_DISPUTED" in actions
    assert "INCIDENT_REOPENED" in actions

    # Citizen trying to read audit logs is forbidden
    forbidden_audit = client.get(
        f"/api/v1/incidents/{incident['id']}/audit",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert forbidden_audit.status_code == 403
