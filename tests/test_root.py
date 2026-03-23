"""
Tests for root endpoint following AAA (Arrange-Act-Assert) pattern
"""


class TestRoot:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_index(self, client):
        """
        Arrange: Client is ready
        Act: Request root endpoint (with follow_redirects=False to see redirect)
        Assert: Response is 307 (temporary redirect) to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
