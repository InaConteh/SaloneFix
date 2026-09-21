def test_tc_005_moderator_queue_and_verify(client, citizen_token, moderator_token):
    # 1. Citizen creates report
    rep = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Substantial pothole near Lumley police post.",
            "latitude": 8.465,
            "longitude": -13.275,
        },
    ).json()

    # 2. Moderator checks queue
    queue_resp = client.get(
        "/api/v1/moderation/queue",
        headers={"Authorization": f"Bearer {moderator_token}"},
    )
    assert queue_resp.status_code == 200
    queue = queue_resp.json()
    assert any(item["report"]["id"] == rep["id"] for item in queue)

    # 3. Moderator verifies report with explicit reason
    decision_resp = client.post(
        f"/api/v1/moderation/reports/{rep['id']}/decision",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "decision": "VERIFY",
            "reason": "Road defect verified by moderator based on clear visual description and coordinates.",
        },
    )
    assert decision_resp.status_code == 200
    updated_rep = decision_resp.json()
    assert updated_rep["current_status"] == "VERIFIED"


def test_tc_006_moderator_creates_incident_and_merges_duplicate(client, citizen_token, moderator_token):
    # 1. First report
    rep1 = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "DRAINAGE_FLOODING",
            "description": "Drainage canal overflowing at Kroo Bay bridge.",
            "latitude": 8.489,
            "longitude": -13.238,
        },
    ).json()

    # 2. Second duplicate report from nearby
    rep2 = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "DRAINAGE_FLOODING",
            "description": "Heavy flood waters backing up into Kroo Bay community.",
            "latitude": 8.4892,
            "longitude": -13.2381,
        },
    ).json()

    # Get category ID
    cats = client.get("/api/v1/categories").json()
    drainage_cat = next(c for c in cats if c["code"] == "DRAINAGE_FLOODING")

    # 3. Moderator creates incident linking report 1
    incident_resp = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "category_id": drainage_cat["id"],
            "title": "Kroo Bay Flood Channel Blockage",
            "summary": "Severe culvert clogging causing overflow into coastal settlement.",
            "priority": "HIGH",
            "report_id": rep1["id"],
        },
    )
    assert incident_resp.status_code == 200
    incident = incident_resp.json()
    assert incident["linked_reports_count"] == 1

    # 4. Moderator merges report 2 into the incident
    merge_resp = client.post(
        f"/api/v1/moderation/reports/{rep2['id']}/decision",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "decision": "MERGE",
            "reason": "Duplicate report describing the same flood event at Kroo Bay.",
            "target_incident_id": incident["id"],
        },
    )
    assert merge_resp.status_code == 200
    assert merge_resp.json()["current_status"] == "MERGED"

    # 5. Check incident now has both linked reports preserved
    inc_detail = client.get(
        f"/api/v1/incidents/{incident['id']}",
        headers={"Authorization": f"Bearer {moderator_token}"},
    ).json()
    assert inc_detail["linked_reports_count"] == 2
