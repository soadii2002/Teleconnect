from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ─── HELPERS ──────────────────────────────────────────────

def valid_payload(**overrides):
    base = {
        "full_name": "Sara Ahmed",
        "email": "sara@example.com",
        "password": "securepassword123",
        "gender": "female",
        "phone_number": "01012345678",
        "city": "Cairo"
    }
    base.update(overrides)
    return base


# ─── TEST CASES ───────────────────────────────────────────

class TestUserRegistration:

    def test_register_customer_success(self):
        response = client.post("/api/auth/register", json=valid_payload())
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "sara@example.com"
        assert data["full_name"] == "Sara Ahmed"
        assert data["gender"] == "female"
        assert data["phone_number"] == "01012345678"
        assert data["city"] == "Cairo"
        assert data["role"] == "customer"
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_email_fails(self):
        client.post("/api/auth/register", json=valid_payload())
        response = client.post("/api/auth/register", json=valid_payload())
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_register_missing_fields_fails(self):
        response = client.post("/api/auth/register", json={
            "email": "incomplete@example.com"
        })
        assert response.status_code == 422

    def test_register_invalid_phone_prefix_fails(self):
        response = client.post("/api/auth/register", json=valid_payload(
            phone_number="01312345678"
        ))
        assert response.status_code == 422
        assert "phone_number" in response.text

    def test_register_phone_too_short_fails(self):
        response = client.post("/api/auth/register", json=valid_payload(
            phone_number="0101234"
        ))
        assert response.status_code == 422
        assert "phone_number" in response.text

    def test_register_phone_too_long_fails(self):
        response = client.post("/api/auth/register", json=valid_payload(
            phone_number="010123456789"
        ))
        assert response.status_code == 422
        assert "phone_number" in response.text

    def test_register_invalid_gender_fails(self):
        response = client.post("/api/auth/register", json=valid_payload(
            gender="unknown"
        ))
        assert response.status_code == 422
        assert "gender" in response.text

    def test_register_empty_city_fails(self):
        response = client.post("/api/auth/register", json=valid_payload(
            city=""
        ))
        assert response.status_code == 422
        assert "city" in response.text

    def test_register_duplicate_phone_fails(self):
        client.post("/api/auth/register", json=valid_payload())
        response = client.post("/api/auth/register", json=valid_payload(
            email="another@example.com"
        ))
        assert response.status_code == 400
        assert response.json()["detail"] == "Phone number already registered"


class TestUserLogin:

    def register_sara(self):
        client.post("/api/auth/register", json=valid_payload())

    def test_login_success(self):
        self.register_sara()
        response = client.post("/api/auth/login", json={
            "email": "sara@example.com",
            "password": "securepassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "sara@example.com"
        assert data["user"]["role"] == "customer"

    def test_login_wrong_password_fails(self):
        self.register_sara()
        response = client.post("/api/auth/login", json={
            "email": "sara@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_login_nonexistent_email_fails(self):
        response = client.post("/api/auth/login", json={
            "email": "ghost@example.com",
            "password": "securepassword123"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_login_missing_fields_fails(self):
        response = client.post("/api/auth/login", json={
            "email": "sara@example.com"
        })
        assert response.status_code == 422

    def test_login_returns_valid_token_for_me_endpoint(self):
        self.register_sara()
        login_response = client.post("/api/auth/login", json={
            "email": "sara@example.com",
            "password": "securepassword123"
        })
        token = login_response.json()["access_token"]
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "sara@example.com"

    def test_me_endpoint_without_token_fails(self):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_me_endpoint_with_invalid_token_fails(self):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer faketoken123"}
        )
        assert response.status_code == 401