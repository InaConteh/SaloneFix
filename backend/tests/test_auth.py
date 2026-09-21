def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"contact": "citizen@freetown.sl", "password": "CitizenPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["contact"] == "citizen@freetown.sl"
    assert data["user"]["role"] == "CITIZEN"


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"contact": "citizen@freetown.sl", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert response.json()["error_code"] == "UNAUTHORIZED"


def test_register_new_citizen(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "contact": "newcitizen@freetown.sl",
            "name_or_alias": "Mohamed Sesay",
            "password": "SecurePassword123!",
            "role": "CITIZEN",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["contact"] == "newcitizen@freetown.sl"
    assert data["user"]["name_or_alias"] == "Mohamed Sesay"


def test_get_current_user_profile(client, citizen_token):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 200
    assert response.json()["contact"] == "citizen@freetown.sl"
