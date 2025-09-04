from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_register_and_login():
    r = client.post("/register", json={"email": "unit@example.com", "password": "pw", "role": "lawyer"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token
    r2 = client.post("/login", json={"email": "unit@example.com", "password": "pw"})
    assert r2.status_code == 200
    assert r2.json()["access_token"]
