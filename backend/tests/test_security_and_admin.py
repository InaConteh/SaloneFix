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
