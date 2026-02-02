"""
Integration tests for /health endpoint

Tests cover the health check endpoint functionality for service monitoring
and keep-alive pings.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


class TestHealthEndpoint:
    """Test suite for /health endpoint"""

    @pytest.fixture
    def client(self):
        """Provide a test client for the FastAPI app"""
        return TestClient(app)

    def test_health_check_returns_ok_status(self, client):
        """Test that health check endpoint returns 200 OK status"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_correct_json_structure(self, client):
        """Test that health check endpoint returns correct JSON structure"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()

        # Verify response has expected keys
        assert "status" in data
        assert "message" in data

    def test_health_check_status_value(self, client):
        """Test that health check endpoint returns 'ok' status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"

    def test_health_check_message_content(self, client):
        """Test that health check endpoint returns correct message"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Service is running"

    def test_health_check_response_headers(self, client):
        """Test that health check endpoint has correct content type"""
        response = client.get("/health")
        assert response.status_code == 200

        # Verify content type is JSON
        assert response.headers["content-type"] == "application/json"

    def test_health_check_cors_headers(self, client):
        """Test that health check endpoint includes CORS headers"""
        response = client.get("/health")
        assert response.status_code == 200

        # Verify CORS headers are present
        assert "access-control-allow-origin" in response.headers

    def test_health_check_no_auth_required(self, client):
        """Test that health check endpoint does not require authentication"""
        # Should return 200 without any auth headers
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_speed(self, client):
        """Test that health check endpoint responds quickly"""
        import time

        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        assert response.status_code == 200
        # Health check should complete in under 100ms
        response_time = (end_time - start_time) * 1000  # Convert to ms
        assert response_time < 100

    def test_health_check_handles_concurrent_requests(self, client):
        """Test that health check endpoint can handle concurrent requests"""
        import concurrent.futures

        def make_request():
            return client.get("/health")

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [
                future.result()
                for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        assert all(response.status_code == 200 for response in results)
        assert len(results) == 10

    def test_health_check_get_method_only(self, client):
        """Test that health check endpoint only accepts GET requests"""
        # Test POST method (should fail)
        post_response = client.post("/health")
        assert post_response.status_code == 405  # Method Not Allowed

        # Test PUT method (should fail)
        put_response = client.put("/health")
        assert put_response.status_code == 405  # Method Not Allowed

        # Test DELETE method (should fail)
        delete_response = client.delete("/health")
        assert delete_response.status_code == 405  # Method Not Allowed

        # GET method should work
        get_response = client.get("/health")
        assert get_response.status_code == 200
