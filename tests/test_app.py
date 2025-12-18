import sys
import pathlib
from urllib.parse import quote

# Ensure `src` is on sys.path so we can import app
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_list_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert len(data) >= 1


def test_signup_and_unregister_cycle():
    # Pick an existing activity
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    assert activities, "No activities found"

    activity_name = next(iter(activities.keys()))
    email = "tester@example.com"

    # Sign up
    signup = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")
    assert signup.status_code == 200
    assert "Signed up" in signup.json().get("message", "")

    # Confirm participant appears
    after = client.get("/activities").json()
    participants = [p.lower() for p in after[activity_name]["participants"]]
    assert email in participants

    # Unregister
    delete = client.delete(f"/activities/{quote(activity_name)}/participants?email={quote(email)}")
    assert delete.status_code == 200
    assert "Unregistered" in delete.json().get("message", "")

    # Confirm removed
    final = client.get("/activities").json()
    participants_final = [p.lower() for p in final[activity_name]["participants"]]
    assert email not in participants_final
