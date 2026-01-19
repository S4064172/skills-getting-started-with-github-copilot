"""Tests for the FastAPI application"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivities:
    """Test activity endpoints"""

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Test signup endpoints"""

    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_already_registered(self):
        """Test signing up when already registered"""
        email = "duplicate@mergington.edu"
        # First signup
        client.post(f"/activities/Basketball%20Team/signup?email={email}")
        # Second signup should fail
        response = client.post(
            f"/activities/Basketball%20Team/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_updates_activity(self):
        """Test that signup updates the activity participants"""
        email = "newstudent@mergington.edu"
        activity_name = "Tennis%20Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()["Tennis Club"]["participants"])
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Check updated participant count
        response = client.get("/activities")
        updated_count = len(response.json()["Tennis Club"]["participants"])
        
        assert updated_count == initial_count + 1


class TestUnregister:
    """Test unregister endpoints"""

    def test_unregister_from_activity(self):
        """Test unregistering from an activity"""
        email = "student@mergington.edu"
        activity_name = "Drama%20Club"
        
        # Sign up first
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Unregister
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_not_registered(self):
        """Test unregistering when not registered"""
        response = client.post(
            "/activities/Art%20Studio/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_removes_participant(self):
        """Test that unregister removes the participant"""
        email = "removeme@mergington.edu"
        activity_name = "Debate%20Team"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Get participant count after signup
        response = client.get("/activities")
        count_after_signup = len(response.json()["Debate Team"]["participants"])
        
        # Unregister
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        
        # Check participant count after unregister
        response = client.get("/activities")
        count_after_unregister = len(response.json()["Debate Team"]["participants"])
        
        assert count_after_unregister == count_after_signup - 1


class TestRoot:
    """Test root endpoint"""

    def test_root_redirect(self):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
