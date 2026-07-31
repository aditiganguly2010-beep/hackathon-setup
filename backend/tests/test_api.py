import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test cases for the health check endpoint."""
    
    def test_health_check_success(self):
        """Test that health check returns 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
