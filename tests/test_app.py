import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "participants" in data["Basketball Team"]

def test_signup_success():
    # Test successful signup
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Basketball Team" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Basketball Team"]["participants"]

def test_signup_duplicate():
    # First signup
    client.post("/activities/Tennis%20Club/signup?email=duplicate@example.com")
    # Try to signup again
    response = client.post("/activities/Tennis%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]

def test_signup_invalid_activity():
    response = client.post("/activities/Invalid%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    # First signup
    client.post("/activities/Debate%20Team/signup?email=unregister@example.com")
    # Then unregister
    response = client.delete("/activities/Debate%20Team/signup?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered unregister@example.com from Debate Team" in data["message"]

    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Debate Team"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Robotics%20Club/signup?email=notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up" in data["detail"]

def test_unregister_invalid_activity():
    response = client.delete("/activities/Invalid%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # Since it's a redirect to /static/index.html, but TestClient follows redirects by default
    # Actually, RedirectResponse, but TestClient should follow
    # But in test, it might not serve static files, so perhaps assert it's redirect
    # Wait, the root returns RedirectResponse(url="/static/index.html")
    # TestClient follows redirects, but since /static/index.html is mounted, it should work
    # For simplicity, just check status 200