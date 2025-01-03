import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt
import time
import re
from main import app
from middleware import rate_limiter_reset

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """Set up test environment variables"""
    monkeypatch.setenv("SECRET_KEY", "test_secret_key")

    from config import settings
    # Update the settings instance used by the application
    settings.SECRET_KEY = "test_secret_key"
    
    rate_limiter_reset()

class TestAuth:
    def test_create_token_success(self):
        """Test successful token creation"""
        response = client.post(
            "/auth/token",
            json={"username": "testuser", "password": "secret123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"
        
        # Verify token contents
        token = data["access_token"]
        payload = jwt.decode(
            token,
            "test_secret_key",
            algorithms=["HS256"]
        )
        assert payload["sub"] == "testuser"
        assert "exp" in payload
        
        # Verify expiration time (15 seconds)
        exp_time = datetime.fromtimestamp(payload["exp"])
        issued_time = datetime.fromtimestamp(payload["iat"])
        assert (exp_time - issued_time).total_seconds() == 15

    def test_create_token_invalid_password(self):
        """Test token creation with wrong password"""
        response = client.post(
            "/auth/token",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_create_token_missing_fields(self):
        """Test token creation with missing fields"""
        response = client.post(
            "/auth/token",
            json={"username": "testuser"}
        )
        
        assert response.status_code == 422

class TestProtectedEndpoint:
    def test_protected_route_success(self):
        """Test accessing protected route with valid token"""
        # Get token first
        auth_response = client.post(
            "/auth/token",
            json={"username": "testuser", "password": "secret123"}
        )
        token = auth_response.json()["access_token"]
        
        # Access protected endpoint
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "Hi, testuser" in response.json()["message"]
        
        # Extract the number of minutes from the message
        message = response.json()["message"]
        minutes_match = re.search(r"valid for next (\d+(\.\d+)?)\s*minutes", message)
        assert minutes_match, "Expected to find 'valid for next X minutes' in the message"
        
        minutes = float(minutes_match.group(1))
        
        # Check if the number of minutes is within a reasonable range
        # Assuming the token is valid for 15 seconds, it should be close to 0.25 minutes
        assert 0 <= minutes <= 0.3, f"Expected minutes to be between 0 and 0.3, but got {minutes}"

        assert "valid for next" in response.json()["message"]

    def test_protected_route_no_token(self):
        """Test accessing protected route without token"""
        response = client.get("/api/protected")
        assert response.status_code == 401
        assert "Missing or invalid authorization header" in response.content.decode()

    def test_protected_route_invalid_token(self):
        """Test accessing protected route with invalid token"""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        assert "Invalid or expired token" in response.content.decode()

    def test_protected_route_expired_token(self):
        """Test accessing protected route with expired token"""
        # Create an expired token
        exp_time = datetime.now() - timedelta(seconds=1)
        token = jwt.encode(
            {"sub": "testuser", "exp": exp_time},
            "test_secret_key",
            algorithm="HS256"
        )
        
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert "Invalid or expired token" in response.content.decode()

class TestMiddleware:
    def test_public_paths_bypass(self):
        """Test that public paths bypass authentication"""
        public_paths = ["/docs", "/openapi.json", "/auth/token"]
        
        for path in public_paths:
            response = client.get(path)
            assert response.status_code != 401, f"Public path {path} should not require authentication"

    def test_invalid_auth_header_format(self):
        """Test invalid authorization header format"""
        invalid_headers = [
            "Token xyz",
            "Bearer",
            "xyz"
        ]
        
        for header in invalid_headers:
            response = client.get(
                "/api/protected",
                headers={"Authorization": header}
            )
            assert response.status_code == 401

    def test_token_expiration_flow(self):
        """Test complete token expiration flow"""
        # Get token
        auth_response = client.post(
            "/auth/token",
            json={"username": "testuser", "password": "secret123"}
        )
        token = auth_response.json()["access_token"]
        
        # Verify token works initially
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Wait for token to expire (16 seconds to be safe)
        time.sleep(16)
        
        # Verify token is now expired
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert "Invalid or expired token" in response.content.decode("utf-8")

class TestIntegrationScenarios:
    def test_full_auth_flow(self):
        """Test complete authentication flow with multiple requests"""
        # 1. Get token
        auth_response = client.post(
            "/auth/token",
            json={"username": "testuser", "password": "secret123"}
        )
        assert auth_response.status_code == 200
        token = auth_response.json()["access_token"]
        
        # 2. Access protected endpoint successfully
        protected_response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status_code == 200
        
        # 3. Verify token payload
        payload = jwt.decode(
            token,
            "test_secret_key",
            algorithms=["HS256"]
        )
        assert payload["sub"] == "testuser"
        
        # 4. Access public endpoint without token
        docs_response = client.get("/docs")
        assert docs_response.status_code != 401

    def test_concurrent_tokens(self):
        """Test handling multiple valid tokens for same user"""
        # Create two tokens for same user
        tokens = []
        for _ in range(2):
            auth_response = client.post(
                "/auth/token",
                json={"username": "testuser", "password": "secret123"}
            )
            tokens.append(auth_response.json()["access_token"])
        
        # Verify both tokens work
        for token in tokens:
            response = client.get(
                "/api/protected",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200

class TestRateLimiting:
    def test_rate_limit_headers(self):
        """Test rate limit headers are present"""
        response = client.post(
            "/auth/token",
            json={"username": "testuser", "password": "secret123"}
        )
        
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_rate_limit_exceeded(self):
        """Test rate limiting kicks in after too many requests"""
        # Make 6 requests in quick succession
        for i in range(6):
            response = client.post(
                "/auth/token",
                json={"username": "testuser", "password": "secret123"}
            )
            if i < 5:
                assert response.status_code == 200
            else:
                assert response.status_code == 429
                assert "Rate limit exceeded" in response.text

    def test_rate_limit_window_reset(self):
        """Test rate limit resets after window period"""
        # Make 5 requests
        for _ in range(5):
            response = client.post(
                "/auth/token",
                json={"username": "testuser", "password": "secret123"}
            )
            assert response.status_code == 200

        # Next request should fail
        response = client.post(
            "/auth/token",
            json={"username": "testuser", "password": "secret123"}
        )
        assert response.status_code == 429

        # Wait for window reset (2 seconds)
        time.sleep(2)

        # Should work again
        response = client.post(
            "/auth/token",
            json={"username": "testuser", "password": "secret123"}
        )
        assert response.status_code == 200

    def test_rate_limit_sliding_window(self):
        """Test sliding window behavior"""
        # Make 3 requests
        for _ in range(3):
            response = client.post(
                "/auth/token",
                json={"username": "testuser", "password": "secret123"}
            )
            assert response.status_code == 200

        # Wait 1 second (half window)
        time.sleep(1)

        # Make 2 more requests
        for _ in range(2):
            response = client.post(
                "/auth/token",
                json={"username": "testuser", "password": "secret123"}
            )
            assert response.status_code == 200

        # Next request should fail
        response = client.post(
            "/auth/token",
            json={"username": "testuser", "password": "secret123"}
        )
        assert response.status_code == 429