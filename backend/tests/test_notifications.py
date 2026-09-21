def test_material_events_create_user_notifications(
    client,
    citizen_token,
    moderator_token,
    officer_token,
):
    report_resp = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "WASTE_MANAGEMENT",
            "description": "Overflowing public bins beside the market entrance.",
            "latitude": 8.486,
            "longitude": -13.235,
            "location_precision": "APPROXIMATE",
        },
    )
    assert report_resp.status_code == 200
    report = report_resp.json()

    citizen_notifications = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert citizen_notifications.status_code == 200
    assert any(n["title"] == "Report received" for n in citizen_notifications.json())

    verify_resp = client.post(
        f"/api/v1/moderation/reports/{report['id']}/decision",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "decision": "VERIFY",
            "reason": "Verified waste hazard needing municipal collection.",
        },
    )
    assert verify_resp.status_code == 200

    cat = next(c for c in client.get("/api/v1/categories").json() if c["code"] == "WASTE_MANAGEMENT")
    incident_resp = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={
            "category_id": cat["id"],
            "title": "Market Entrance Overflowing Public Bins",
            "summary": "Waste overflow requiring municipal collection and cleanup.",
            "priority": "MEDIUM",
            "report_id": report["id"],
        },
    )
    assert incident_resp.status_code == 200
    incident = incident_resp.json()

    fcc = next(i for i in client.get("/api/v1/institutions").json() if "Freetown City Council" in i["name"])
    assignment_resp = client.post(
        f"/api/v1/incidents/{incident['id']}/assignments",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={"institution_id": fcc["id"]},
    )
    assert assignment_resp.status_code == 200

    officer_notifications = client.get(
        "/api/v1/notifications?unread_only=true",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert officer_notifications.status_code == 200
    assert any(n["title"] == "New incident assignment" for n in officer_notifications.json())


def test_user_can_only_mark_own_notifications_read(client, citizen_token, officer_token):
    report_resp = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "PUBLIC_FACILITIES",
            "description": "Broken street light near a busy crossing.",
            "latitude": 8.49,
            "longitude": -13.22,
        },
    )
    assert report_resp.status_code == 200

    notifications = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {citizen_token}"},
    ).json()
    notification_id = notifications[0]["id"]

    forbidden = client.patch(
        f"/api/v1/notifications/{notification_id}/read",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert forbidden.status_code == 404

    read_resp = client.patch(
        f"/api/v1/notifications/{notification_id}/read",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert read_resp.status_code == 200
    assert read_resp.json()["is_read"] is True
