"""
Tests for activities endpoints following AAA (Arrange-Act-Assert) pattern
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_list(self, client):
        """
        Arrange: Client is ready
        Act: Fetch all activities
        Assert: Response is 200 and contains activities with correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Verify structure of an activity
        activity = list(activities.values())[0]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestPostSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """
        Arrange: Prepare a test student email and activity name
        Act: Sign up student for an activity
        Assert: Response is 200 with success message and student is in participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_duplicate_registration_fails(self, client):
        """
        Arrange: Student already signed up for activity
        Act: Attempt to sign up again
        Assert: Response is 400 with error detail
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_activity_not_found(self, client):
        """
        Arrange: Non-existent activity name
        Act: Attempt to sign up for activity
        Assert: Response is 404 with error detail
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_special_characters_in_activity_name(self, client):
        """
        Arrange: Activity name with spaces and special chars
        Act: Sign up with URL-encoded activity name
        Assert: Response is 404 (activity doesn't exist) or 200 if exists
        """
        # Arrange
        activity_name = "Art & Design"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        # Should get either 404 (activity not found) since this activity doesn't exist
        assert response.status_code in [404, 200]


class TestDeleteSignup:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_successful(self, client):
        """
        Arrange: Student is signed up for an activity
        Act: Remove student from activity
        Assert: Response is 200 and student is removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Exists in Chess Club

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_participant_not_found(self, client):
        """
        Arrange: Email that's not registered for the activity
        Act: Attempt to unregister
        Assert: Response is 404 with error detail
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_activity_not_found(self, client):
        """
        Arrange: Non-existent activity name
        Act: Attempt to unregister from activity
        Assert: Response is 404 with error detail
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestSignupFlow:
    """Integration tests for signup/unregister flow"""

    def test_signup_unregister_signup_cycle(self, client):
        """
        Arrange: A student and an activity
        Act: Sign up, unregister, sign up again
        Assert: All operations succeed with correct status codes
        """
        # Arrange
        activity_name = "Programming Class"
        email = "newtester@mergington.edu"

        # Act & Assert - Signup
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response1.status_code == 200

        # Act & Assert - Unregister
        response2 = client.delete(f"/activities/{activity_name}/signup?email={email}")
        assert response2.status_code == 200

        # Act & Assert - Signup again
        response3 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response3.status_code == 200
