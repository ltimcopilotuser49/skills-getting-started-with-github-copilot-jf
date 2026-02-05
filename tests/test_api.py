"""
Test suite for the Mergington High School API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original data
    original_activities = {
        "Chess Club": {
            "Soccer Team": {
                "description": "Join our varsity soccer team and compete against other schools",
                "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
                "max_participants": 25,
                "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
            },
            "Swimming Club": {
                "description": "Improve your swimming techniques and participate in swim meets",
                "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                "max_participants": 15,
                "participants": ["james@mergington.edu"]
            },
            "Drama Club": {
                "description": "Perform in school plays and develop your acting skills",
                "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
                "max_participants": 25,
                "participants": ["emily@mergington.edu", "lucas@mergington.edu"]
            },
            "Art Studio": {
                "description": "Explore painting, drawing, and sculpture techniques",
                "schedule": "Thursdays, 3:30 PM - 5:00 PM",
                "max_participants": 18,
                "participants": ["mia@mergington.edu"]
            },
            "Debate Team": {
                "description": "Develop public speaking and argumentation skills through competitive debates",
                "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
                "max_participants": 16,
                "participants": ["william@mergington.edu", "ava@mergington.edu"]
            },
            "Science Olympiad": {
                "description": "Compete in science and engineering challenges at regional competitions",
                "schedule": "Saturdays, 10:00 AM - 12:00 PM",
                "max_participants": 20,
                "participants": ["ethan@mergington.edu"]
            },
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that getting activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_structure(self, client):
        """Test that activity data has correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Chess Club structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Programming Class/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Programming Class"]["participants"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signup is rejected"""
        # First signup should succeed
        response1 = client.post(
            "/activities/Programming Class/signup?email=test@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Programming Class/signup?email=test@mergington.edu"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test that signup for non-existent activity fails"""
        response = client.post(
            "/activities/NonExistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=encoded@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        # First, sign up a participant
        client.post(
            "/activities/Gym Class/signup?email=temporary@mergington.edu"
        )
        
        # Then unregister them
        response = client.delete(
            "/activities/Gym Class/unregister?email=temporary@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "temporary@mergington.edu" not in activities_data["Gym Class"]["participants"]
    
    def test_unregister_non_participant(self, client):
        """Test that unregistering a non-participant fails"""
        response = client.delete(
            "/activities/Programming Class/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/NonExistent/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_preexisting_participant(self, client):
        """Test unregistering a participant that was already in the system"""
        # Unregister emma who is already in Programming Class
        response = client.delete(
            "/activities/Programming Class/unregister?email=emma@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "emma@mergington.edu" not in activities_data["Programming Class"]["participants"]


class TestSignupUnregisterFlow:
    """Integration tests for signup and unregister flow"""
    
    def test_signup_then_unregister(self, client):
        """Test complete flow of signing up and then unregistering"""
        email = "flowtest@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]
    
    def test_multiple_signups_different_activities(self, client):
        """Test signing up the same student for multiple activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for multiple activities
        client.post(f"/activities/Chess Club/signup?email={email}")
        client.post(f"/activities/Programming Class/signup?email={email}")
        client.post(f"/activities/Gym Class/signup?email={email}")
        
        # Verify all signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]
        assert email in activities_data["Gym Class"]["participants"]
