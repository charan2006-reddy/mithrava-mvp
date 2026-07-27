"""Tests for authentication endpoints: OTP, register, login, refresh, me."""

import pytest
from httpx import AsyncClient


class TestSendOTP:
    """Test POST /api/v1/auth/send-otp."""

    @pytest.mark.asyncio
    async def test_send_otp_success(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/send-otp", json={"phone": "+919000000001"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "demo_otp" in data["data"]
        assert len(data["data"]["demo_otp"]) == 6

    @pytest.mark.asyncio
    async def test_send_otp_invalid_phone(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/send-otp", json={"phone": "123"})
        assert resp.status_code == 422  # Validation error


class TestVerifyOTP:
    """Test POST /api/v1/auth/verify-otp."""

    @pytest.mark.asyncio
    async def test_verify_otp_unregistered_returns_needs_registration(self, client: AsyncClient):
        phone = "+919000000002"
        otp_resp = await client.post("/api/v1/auth/send-otp", json={"phone": phone})
        code = otp_resp.json()["data"]["demo_otp"]

        resp = await client.post(
            "/api/v1/auth/verify-otp",
            json={"phone": phone, "code": code},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["needs_registration"] is True
        assert data["data"]["phone"] == phone

    @pytest.mark.asyncio
    async def test_verify_otp_wrong_code(self, client: AsyncClient):
        phone = "+919000000003"
        await client.post("/api/v1/auth/send-otp", json={"phone": phone})
        resp = await client.post(
            "/api/v1/auth/verify-otp",
            json={"phone": phone, "code": "000000"},
        )
        assert resp.status_code in (200, 401)


class TestRegister:
    """Test POST /api/v1/auth/register."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        phone = "+919000000004"
        otp_resp = await client.post("/api/v1/auth/send-otp", json={"phone": phone})
        code = otp_resp.json()["data"]["demo_otp"]
        await client.post(
            "/api/v1/auth/verify-otp",
            json={"phone": phone, "code": code},
        )

        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "Test Farmer",
                "phone": phone,
                "email": "test@mithrava.com",
                "city": "Hyderabad",
                "state": "Telangana",
                "preferred_language": "en",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["farmer"]["name"] == "Test Farmer"
        assert "tokens" in data["data"]
        assert "access_token" in data["data"]["tokens"]

    @pytest.mark.asyncio
    async def test_register_duplicate_phone(self, client: AsyncClient):
        phone = "+919000000005"
        # Register first user
        otp_resp = await client.post("/api/v1/auth/send-otp", json={"phone": phone})
        code = otp_resp.json()["data"]["demo_otp"]
        await client.post("/api/v1/auth/verify-otp", json={"phone": phone, "code": code})
        await client.post(
            "/api/v1/auth/register",
            json={"name": "User 1", "phone": phone},
        )

        # Try registering with same phone — need new OTP
        otp_resp2 = await client.post("/api/v1/auth/send-otp", json={"phone": phone})
        code2 = otp_resp2.json()["data"]["demo_otp"]
        await client.post("/api/v1/auth/verify-otp", json={"phone": phone, "code": code2})
        resp = await client.post(
            "/api/v1/auth/register",
            json={"name": "User 2", "phone": phone},
        )
        assert resp.status_code == 409


class TestGetMe:
    """Test GET /api/v1/auth/me."""

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Farmer"
        assert data["data"]["phone"] == "+919876543210"

    @pytest.mark.asyncio
    async def test_get_me_no_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 403)
