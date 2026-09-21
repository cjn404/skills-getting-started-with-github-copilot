import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    """Provide a fresh FastAPI test client and reset app state each test."""
    original = {
        name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": list(activity["participants"]),
        }
        for name, activity in activities.items()
    }

    try:
        yield TestClient(app)
    finally:
        activities.clear()
        activities.update(original)


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"Chess Club", "Programming Class", "Gym Class"}
    assert payload["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_email(client):
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_unregister_for_activity_removes_email(client):
    email = "michael@mergington.edu"

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_signup_missing_activity_returns_404(client):
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_missing_email_returns_404(client):
    email = "notregistered@mergington.edu"

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 404
    assert response.json() == {"detail": f"{email} is not registered for Chess Club"}
