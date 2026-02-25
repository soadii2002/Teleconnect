from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from tests.conftest import TestingSessionLocal

client = TestClient(app)


# ─── HELPERS ──────────────────────────────────────────────

def register_and_login(email="customer@example.com", role="customer"):
    client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": email,
        "password": "password123",
        "gender": "male",
        "phone_number": "01012345678",
        "city": "Cairo"
    })
    response = client.post("/api/auth/login", json={
        "email": email,
        "password": "password123"
    })
    return response.json()["access_token"]


def register_and_login_admin():
    client.post("/api/auth/register", json={
        "full_name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpass123",
        "gender": "male",
        "phone_number": "01112345678",
        "city": "Alexandria"
    })
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "admin@example.com").first()
    user.role = "admin"
    db.commit()
    db.close()
    response = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpass123"
    })
    return response.json()["access_token"]


def valid_plan():
    return {
        "name": "Mobile Basic",
        "category": "mobile",
        "description": "Entry level mobile plan",
        "price": 10.99,
        "data_limit_gb": 5,
        "speed_mbps": None
    }


# ─── TEST CASES ───────────────────────────────────────────

class TestPlansPublic:

    def test_list_plans_returns_empty_initially(self):
        response = client.get("/api/plans")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_plans_returns_active_plans(self):
        admin_token = register_and_login_admin()
        client.post("/api/plans", json=valid_plan(),
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        response = client.get("/api/plans")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Mobile Basic"

    def test_get_single_plan_success(self):
        admin_token = register_and_login_admin()
        created = client.post("/api/plans", json=valid_plan(),
            headers={"Authorization": f"Bearer {admin_token}"}
        ).json()
        response = client.get(f"/api/plans/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_nonexistent_plan_fails(self):
        response = client.get("/api/plans/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


class TestPlansAdmin:

    def test_admin_can_create_mobile_plan(self):
        admin_token = register_and_login_admin()
        response = client.post("/api/plans", json=valid_plan(),
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Mobile Basic"
        assert data["category"] == "mobile"
        assert data["is_active"] is True

    def test_admin_can_create_internet_plan(self):
        admin_token = register_and_login_admin()
        response = client.post("/api/plans", json={
            "name": "Fiber 100",
            "category": "internet",
            "description": "100 Mbps fiber plan",
            "price": 29.99,
            "data_limit_gb": None,
            "speed_mbps": 100
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 201
        assert response.json()["category"] == "internet"

    def test_admin_can_update_plan(self):
        admin_token = register_and_login_admin()
        created = client.post("/api/plans", json=valid_plan(),
            headers={"Authorization": f"Bearer {admin_token}"}
        ).json()
        response = client.put(f"/api/plans/{created['id']}",
            json={"price": 14.99},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["price"] == 14.99

    def test_admin_can_deactivate_plan(self):
        admin_token = register_and_login_admin()
        created = client.post("/api/plans", json=valid_plan(),
            headers={"Authorization": f"Bearer {admin_token}"}
        ).json()
        response = client.delete(f"/api/plans/{created['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_deactivated_plan_hidden_from_public(self):
        admin_token = register_and_login_admin()
        created = client.post("/api/plans", json=valid_plan(),
            headers={"Authorization": f"Bearer {admin_token}"}
        ).json()
        client.delete(f"/api/plans/{created['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        response = client.get("/api/plans")
        assert response.json() == []

    def test_customer_cannot_create_plan(self):
        customer_token = register_and_login()
        response = client.post("/api/plans", json=valid_plan(),
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 403

    def test_customer_cannot_delete_plan(self):
        admin_token = register_and_login_admin()
        customer_token = register_and_login()
        created = client.post("/api/plans", json=valid_plan(),
            headers={"Authorization": f"Bearer {admin_token}"}
        ).json()
        response = client.delete(f"/api/plans/{created['id']}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 403

    def test_unauthenticated_cannot_create_plan(self):
        response = client.post("/api/plans", json=valid_plan())
        assert response.status_code == 401