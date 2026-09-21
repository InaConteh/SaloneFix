import io
from PIL import Image


def test_tc_001_valid_report_submission(client, citizen_token):
    response = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Severe pothole at Kissy Road junction damaging vehicle tires.",
            "latitude": 8.484,
            "longitude": -13.229,
            "location_precision": "APPROXIMATE",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "tracking_reference" in data
    assert data["tracking_reference"].startswith("SF-")
    assert data["status"] == "SUBMITTED"
    assert "A moderator will review" in data["next_step"]


def test_tc_002_missing_description_validation_error(client, citizen_token):
    response = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Short",  # Min length 10 required
            "latitude": 8.484,
            "longitude": -13.229,
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"


def test_tc_003_location_fallback(client, citizen_token):
    response = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "WASTE_MANAGEMENT",
            "description": "Refuse overflow near Kingtom cemetery road without exact GPS.",
            "latitude": None,
            "longitude": None,
            "location_precision": "USER_ENTERED",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUBMITTED"


def test_tc_004_invalid_media_upload_rejected(client, citizen_token):
    # 1. Create report
    rep = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "DRAINAGE_FLOODING",
            "description": "Gutter blocked on Pademba Road causing localized flooding.",
            "latitude": 8.475,
            "longitude": -13.235,
        },
    ).json()

    # 2. Upload fake corrupt binary disguised as jpeg
    corrupt_file = io.BytesIO(b"Not An Actual Image File Content Just Plain Text")
    response = client.post(
        f"/api/v1/reports/{rep['id']}/media",
        headers={"Authorization": f"Bearer {citizen_token}"},
        files={"file": ("fake_image.jpg", corrupt_file, "image/jpeg")},
    )
    assert response.status_code in [400, 422]
    assert response.json()["error_code"] == "MEDIA_INVALID"


def test_tc_004_valid_media_upload_sanitized(client, citizen_token):
    # 1. Create report
    rep = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "PUBLIC_FACILITIES",
            "description": "Broken street lighting post near Victoria Park.",
            "latitude": 8.488,
            "longitude": -13.234,
        },
    ).json()

    # 2. Create valid in-memory image
    img = Image.new("RGB", (100, 100), color="blue")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    response = client.post(
        f"/api/v1/reports/{rep['id']}/media",
        headers={"Authorization": f"Bearer {citizen_token}"},
        files={"file": ("lamp_post.jpg", img_bytes, "image/jpeg")},
    )
    assert response.status_code == 200
    media_data = response.json()
    assert media_data["mime_type"] == "image/jpeg"
    assert media_data["original_filename"] == "lamp_post.jpg"


def test_tc_005_safe_public_tracking(client, citizen_token):
    rep = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={
            "category_code": "ROAD_POTHOLE",
            "description": "Craters on Wilkinson Road near the roundabout.",
            "latitude": 8.472,
            "longitude": -13.262,
        },
    ).json()

    # Query public tracking
    status_resp = client.get(f"/api/v1/reports/{rep['tracking_reference']}/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["tracking_reference"] == rep["tracking_reference"]
    assert status_data["current_status"] == "SUBMITTED"
    assert "moderator" in status_data["next_step"].lower()
