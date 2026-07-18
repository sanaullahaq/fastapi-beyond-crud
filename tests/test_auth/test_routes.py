import uuid
import pytest
from datetime import timedelta
from src.auth.utils import create_url_safe_token, create_access_token
from src.auth.service import UserService
from src.auth.schemas import UserCreate


class TestAuthRoutes:
    signup_payload = {
        "first_name": "New",
        "last_name": "User",
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "testpass123",
    }

    @pytest.mark.asyncio
    async def test_signup_success(self, client):
        resp = await client.post("/api/v1/auth/signup", json=self.signup_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["message"] == "Account Created!, Check email to verify your account"
        assert data["user"]["email"] == "newuser@example.com"

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client):
        await client.post("/api/v1/auth/signup", json=self.signup_payload)
        resp = await client.post("/api/v1/auth/signup", json=self.signup_payload)
        assert resp.status_code == 403
        assert "user" in resp.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_verify_valid_token(self, client, session):
        service = UserService()
        user_data = UserCreate(
            first_name="Verify",
            last_name="Me",
            username="verifyme",
            email="verify@example.com",
            password="testpass123",
        )
        user = await service.create_user(user_data=user_data, session=session)
        token = create_url_safe_token({"email": user.email})
        resp = await client.get(f"/api/v1/auth/verify/{token}")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Account verified successfully"

    @pytest.mark.asyncio
    async def test_verify_invalid_token(self, client):
        resp = await client.get("/api/v1/auth/verify/invalid-token")
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_login_success(self, client, session):
        service = UserService()
        user_data = UserCreate(
            first_name="Login",
            last_name="Test",
            username="logint",
            email="login@example.com",
            password="testpass123",
        )
        await service.create_user(user_data=user_data, session=session)
        resp = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "testpass123",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, session):
        service = UserService()
        user_data = UserCreate(
            first_name="Wrong",
            last_name="Pass",
            username="wrongpw",
            email="wrong@example.com",
            password="testpass123",
        )
        await service.create_user(user_data=user_data, session=session)
        resp = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword",
            },
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_login_nonexistent_email(self, client):
        resp = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "noone@example.com",
                "password": "testpass123",
            },
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_refresh_token(self, client, verified_user):
        refresh_token = create_access_token(
            user_data={
                "email": verified_user.email,
                "user_uid": str(verified_user.uid),
            },
            refresh=True,
            expiry=timedelta(days=30),
        )
        resp = await client.get(
            "/api/v1/auth/refresh_token",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    @pytest.mark.asyncio
    async def test_logout(self, client, auth_headers):
        resp = await client.get("/api/v1/auth/logout", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Logged out successfully"

    @pytest.mark.asyncio
    async def test_me(self, client, auth_headers):
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "verified@example.com"

    @pytest.mark.asyncio
    async def test_me_unauthenticated(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_send_mail(self, client):
        resp = await client.post(
            "/api/v1/auth/send_mail",
            json={"addresses": ["test@example.com"]},
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Email sent successfully"

    @pytest.mark.asyncio
    async def test_password_reset_request(self, client, session, test_user):
        resp = await client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": test_user.email},
        )
        assert resp.status_code == 200
        assert "password reset link" in resp.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_password_reset_request_nonexistent(self, client):
        resp = await client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": "noone@example.com"},
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_password_reset_confirm_valid(self, client, session):
        service = UserService()
        user_data = UserCreate(
            first_name="Reset",
            last_name="Me",
            username="resetme",
            email="reset@example.com",
            password="oldpass123",
        )
        user = await service.create_user(user_data=user_data, session=session)
        token = create_url_safe_token({"email": user.email})
        resp = await client.post(
            f"/api/v1/auth/password-reset-confirm/{token}",
            json={"new_password": "newpass123", "confirm_new_password": "newpass123"},
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Password reset successfully"
