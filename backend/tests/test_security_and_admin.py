import io
from PIL import Image


def _jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (60, 60), color="green").save(buf, format="JPEG")
    return buf.getvalue()


def _create_report_with_media(client, citizen_token):
    rep = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "WASTE_MANAGEMENT",
            "description": "Overflowing communal bin blocking the pavement near the market.",
            "latitude": 8.487,
            "longitude": -13.231,
        },
    ).json()
    media = client.post(
        f"/api/v1/reports/{rep['id']}/media",
        headers={"Authorization": f"Bearer {citizen_token}"},
        files={"file": ("bin.jpg", _jpeg_bytes(), "image/jpeg")},
    ).json()
    return rep, media


# --------------------------------------------------------------- private media
def test_media_requires_auth_or_signed_token(client, citizen_token, moderator_token):
    rep, media = _create_report_with_media(client, citizen_token)

    # Anonymous, no token -> refused (media is private by default)
    anon = client.get(f"/api/v1/media/{media['id']}")
    assert anon.status_code == 403
    assert anon.json()["error_code"] == "FORBIDDEN"

    # Tampered token -> refused
    bad = client.get(f"/api/v1/media/{media['id']}?token=9999999999.deadbeef")
    assert bad.status_code == 403

    # Signed URL issued by the API -> allowed (works in <img src> with no header)
    assert media["url"].startswith(f"/api/v1/media/{media['id']}?token=")
    signed = client.get(media["url"])
    assert signed.status_code == 200
    assert signed.headers["content-type"] == "image/jpeg"

    # Authenticated staff -> allowed without token
    staff = client.get(f"/api/v1/media/{media['id']}", headers={"Authorization": f"Bearer {moderator_token}"})
    assert staff.status_code == 200


def test_media_upload_idempotency_key(client, citizen_token):
    rep = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "DRAINAGE_FLOODING",
            "description": "Blocked culvert flooding the road after every rain.",
            "latitude": 8.47,
            "longitude": -13.24,
        },
    ).json()
    headers = {"Authorization": f"Bearer {citizen_token}", "Idempotency-Key": "photo-abc"}
    first = client.post(f"/api/v1/reports/{rep['id']}/media", headers=headers,
                        files={"file": ("a.jpg", _jpeg_bytes(), "image/jpeg")})
    second = client.post(f"/api/v1/reports/{rep['id']}/media", headers=headers,
                         files={"file": ("a.jpg", _jpeg_bytes(), "image/jpeg")})
    assert first.status_code == second.status_code == 200
    assert first.json()["id"] == second.json()["id"]

    detail = client.get(f"/api/v1/reports/{rep['id']}", headers={"Authorization": f"Bearer {citizen_token}"}).json()
    assert len(detail["media_assets"]) == 1


# ------------------------------------------------------- registration lockdown
def test_public_registration_cannot_choose_role(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "name_or_alias": "Sneaky",
            "contact": "sneaky@example.sl",
            "password": "TryToBeAdmin1!",
            "role": "ADMIN",
            "institution_id": None,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["user"]["role"] == "CITIZEN"

    # ...and the token really is a citizen token
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {resp.json()['access_token']}"})
    assert me.json()["role"] == "CITIZEN"
    forbidden = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {resp.json()['access_token']}"})
    assert forbidden.status_code == 403


# ---------------------------------------------------------------------- admin
def test_admin_provisions_staff_and_deactivates(client, admin_token, moderator_token):
    institutions = client.get("/api/v1/institutions").json()
    fcc = next(i for i in institutions if "FCC" in i["name"])

    # Officer without institution is rejected with an actionable error
    bad = client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name_or_alias": "New Officer", "contact": "new.officer@fcc.sl",
              "password": "OfficerPass123!", "role": "OFFICER"},
    )
    assert bad.status_code == 422
    assert bad.json()["error_code"] == "VALIDATION_ERROR"

    created = client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name_or_alias": "New Officer", "contact": "new.officer@fcc.sl",
              "password": "OfficerPass123!", "role": "OFFICER", "institution_id": fcc["id"]},
    )
    assert created.status_code == 201
    new_user = created.json()
    assert new_user["role"] == "OFFICER"
    assert new_user["institution_name"] == fcc["name"]

    # Moderators must not reach admin endpoints
    denied = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {moderator_token}"})
    assert denied.status_code == 403

    # Deactivate with a reason -> login now fails
    updated = client.patch(
        f"/api/v1/admin/users/{new_user['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False, "reason": "Officer left the institution."},
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False
    login = client.post("/api/v1/auth/login", json={"contact": "new.officer@fcc.sl", "password": "OfficerPass123!"})
    assert login.status_code == 401

    # Audit trail recorded both actions
    events = client.get("/api/v1/events?entity_type=USER", headers={"Authorization": f"Bearer {admin_token}"}).json()
    actions = {e["action"] for e in events if e["entity_id"] == new_user["id"]}
    assert {"USER_PROVISIONED", "USER_UPDATED"} <= actions


def test_admin_cannot_deactivate_self(client, admin_token):
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"}).json()
    resp = client.patch(
        f"/api/v1/admin/users/{me['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False, "reason": "Oops"},
    )
    assert resp.status_code == 409


def test_admin_manages_institutions(client, admin_token):
    created = client.post(
        "/api/v1/admin/institutions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Electricity Distribution and Supply Authority (EDSA)",
              "service_area": "Freetown", "contact_channel": "ops@edsa.sl"},
    )
    assert created.status_code == 201
    inst = created.json()
    assert inst["is_active"] is True

    # Deactivate -> disappears from the public list
    resp = client.patch(
        f"/api/v1/admin/institutions/{inst['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False},
    )
    assert resp.status_code == 200
    names = [i["name"] for i in client.get("/api/v1/institutions").json()]
    assert inst["name"] not in names


# ----------------------------------------------------------------- pagination
def test_list_endpoints_paginate_with_total_header(client, citizen_token):
    for i in range(3):
        client.post(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {citizen_token}"},
            json={
                "category_code": "ROAD_POTHOLE",
                "description": f"Pothole number {i} on Wilkinson Road causing traffic delays.",
                "latitude": 8.47 + i * 0.01,
                "longitude": -13.26,
            },
        )
    page1 = client.get("/api/v1/reports?limit=2&offset=0", headers={"Authorization": f"Bearer {citizen_token}"})
    page2 = client.get("/api/v1/reports?limit=2&offset=2", headers={"Authorization": f"Bearer {citizen_token}"})
    assert page1.status_code == 200
    assert page1.headers["x-total-count"] == "3"
    assert len(page1.json()) == 2
    assert len(page2.json()) == 1
    ids = {r["id"] for r in page1.json()} | {r["id"] for r in page2.json()}
    assert len(ids) == 3

    too_big = client.get("/api/v1/reports?limit=500", headers={"Authorization": f"Bearer {citizen_token}"})
    assert too_big.status_code == 422


# ----------------------------------------------------------------- error codes
def test_rate_limit_returns_429_with_stable_code(client):
    from app.core.dependencies import _rate_limit_cache
    _rate_limit_cache.clear()
    responses = [
        client.post("/api/v1/auth/login", json={"contact": "nobody@example.sl", "password": "wrong"})
        for _ in range(25)
    ]
    limited = [r for r in responses if r.status_code == 429]
    assert limited, "expected the login rate limiter to trip"
    body = limited[0].json()
    assert body["error_code"] == "RATE_LIMITED"
    assert body["details"]["retry_after_seconds"] > 0
    _rate_limit_cache.clear()


# ------------------------------------------------------------ incident IDOR
def test_citizen_sees_only_own_incidents_and_redacted_detail(client, citizen_token, moderator_token):
    """A citizen must not read other citizens' reports, disputes or exact locations via /incidents."""
    # Second citizen, registered through the public endpoint
    other = client.post(
        "/api/v1/auth/register",
        json={"name_or_alias": "Other Citizen", "contact": "other@freetown.sl", "password": "OtherPass123!"},
    ).json()
    other_token = other["access_token"]

    def make_report(token, desc, lat, lon):
        return client.post(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {token}"},
            json={"category_code": "ROAD_POTHOLE", "description": desc, "latitude": lat, "longitude": lon,
                  "location_precision": "EXACT"},
        ).json()

    mine = make_report(citizen_token, "Deep pothole outside my house on Wilkinson Road, dangerous.", 8.48371, -13.26412)
    theirs = make_report(other_token, "Same pothole, my car was damaged, private details inside.", 8.48375, -13.26418)
    unrelated = make_report(other_token, "Blocked drain at Lumley beach road causing flooding daily.", 8.45, -13.29)

    mod = {"Authorization": f"Bearer {moderator_token}"}
    for rep in (mine, theirs, unrelated):
        client.post(f"/api/v1/moderation/reports/{rep['id']}/decision", headers=mod,
                    json={"decision": "VERIFY", "reason": "Verified for test."})
    cats = client.get("/api/v1/categories").json()
    road = next(c for c in cats if c["code"] == "ROAD_POTHOLE")
    shared = client.post("/api/v1/incidents", headers=mod, json={
        "category_id": road["id"], "title": "Wilkinson Road pothole", "summary": "Shared case",
        "priority": "HIGH", "report_id": mine["id"]}).json()
    client.post(f"/api/v1/incidents/{shared['id']}/reports", headers=mod, json={"report_id": theirs["id"]})
    private = client.post("/api/v1/incidents", headers=mod, json={
        "category_id": road["id"], "title": "Lumley drain", "summary": "Other citizen only",
        "priority": "MEDIUM", "report_id": unrelated["id"]}).json()

    me = {"Authorization": f"Bearer {citizen_token}"}

    # List: only the incident linked to my report
    listing = client.get("/api/v1/incidents", headers=me)
    assert listing.status_code == 200
    ids = {i["id"] for i in listing.json()}
    assert shared["id"] in ids and private["id"] not in ids
    assert listing.headers["x-total-count"] == "1"

    # Detail of an incident I am not linked to: forbidden
    denied = client.get(f"/api/v1/incidents/{private['id']}", headers=me)
    assert denied.status_code == 403

    # Detail of the shared incident: only my report, coarse coordinates, no other-citizen data
    detail = client.get(f"/api/v1/incidents/{shared['id']}", headers=me).json()
    linked_ids = {lr["report"]["id"] for lr in detail["linked_reports"]}
    assert linked_ids == {mine["id"]}
    assert detail["linked_reports_count"] == 2  # count is not secret; contents are
    assert "private details" not in str(detail)
    assert detail["centroid_latitude"] == round(detail["centroid_latitude"], 2)
    assert detail["centroid_longitude"] == round(detail["centroid_longitude"], 2)

    # Staff still get the full picture
    full = client.get(f"/api/v1/incidents/{shared['id']}", headers=mod).json()
    assert {lr["report"]["id"] for lr in full["linked_reports"]} == {mine["id"], theirs["id"]}
    assert abs(full["centroid_latitude"] - 8.48373) < 0.0005
