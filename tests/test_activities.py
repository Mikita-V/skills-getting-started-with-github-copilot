import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Chess Club" in data

    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_includes_initial_participants(self, client):
        """Test that initial participants are included"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "student@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds participant to the activity"""
        response = client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Soccer Club"]["participants"]

    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up twice fails"""
        email = "duplicate@mergington.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Art%20Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup - should fail
        response2 = client.post(
            "/activities/Art%20Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for a nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_existing_participant_in_activity(self, client, reset_activities):
        """Test that existing participants can be retrieved"""
        response = client.get("/activities")
        chess_participants = response.json()["Chess Club"]["participants"]
        assert len(chess_participants) == 2


class TestUnregister:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregistration"""
        email = "testuser@mergington.edu"
        
        # First signup
        client.post(
            "/activities/Drama%20Club/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.post(
            "/activities/Drama%20Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes participant from activity"""
        email = "remove@mergington.edu"
        
        # Signup
        client.post(
            "/activities/Debate%20Team/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Debate Team"]["participants"]
        
        # Unregister
        client.post(
            "/activities/Debate%20Team/unregister",
            params={"email": email}
        )
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Debate Team"]["participants"]

    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from nonexistent activity fails"""
        response = client.post(
            "/activities/Fake%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_participant_not_signed_up_fails(self, client, reset_activities):
        """Test that unregistering someone not signed up fails"""
        response = client.post(
            "/activities/Math%20Club/unregister",
            params={"email": "notsignup@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant"""
        response = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        assert "michael@mergington.edu" not in activities_response.json()["Chess Club"]["participants"]


class TestRoot:
    """Tests for the GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
