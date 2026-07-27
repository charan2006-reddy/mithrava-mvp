"""Tests for admin dashboard endpoints."""

import pytest
from httpx import AsyncClient


async def _create_admin_user(client: AsyncClient) -> dict:
    """Helper: create an admin user directly in DB and return tokens."""
    import uuid
    from app.core.security import create_access_token, create_refresh_token
    from app.models.farmer import Farmer
    from tests.conftest import test_session_factory

    farmer_id = str(uuid.uuid4())

    async with test_session_factory() as session:
        farmer = Farmer(
            id=farmer_id,
            name="Test Admin",
            phone="+919999999999",
            email="admin@mithrava.com",
            city="Hyderabad",
            state="Telangana",
            preferred_language="en",
            is_active=True,
            is_verified=True,
            role="admin",
        )
        session.add(farmer)
        await session.commit()

    access_token = create_access_token({"sub": farmer_id})
    refresh_token = create_refresh_token({"sub": farmer_id})

    return {
        "farmer": {"id": farmer_id, "name": "Test Admin", "phone": "+919999999999"},
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    }


class TestAdminStats:
    """Test GET /api/v1/admin/stats."""

    @pytest.mark.asyncio
    async def test_admin_stats_requires_admin(self, client: AsyncClient, auth_headers: dict):
        """Regular farmer cannot access admin stats."""
        resp = await client.get("/api/v1/admin/stats", headers=auth_headers)
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_stats_success(self, client: AsyncClient):
        """Admin can access dashboard stats."""
        admin = await _create_admin_user(client)
        headers = {"Authorization": f"Bearer {admin['tokens']['access_token']}"}
        resp = await client.get("/api/v1/admin/stats", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "total_farmers" in data["data"]
        assert "active_crops" in data["data"]
        assert "total_vendors" in data["data"]

    @pytest.mark.asyncio
    async def test_admin_stats_no_auth(self, client: AsyncClient):
        """Unauthenticated request is rejected."""
        resp = await client.get("/api/v1/admin/stats")
        assert resp.status_code in (401, 403)


class TestAdminFarmers:
    """Test admin farmer management endpoints."""

    @pytest.mark.asyncio
    async def test_list_farmers_requires_admin(self, client: AsyncClient, auth_headers: dict):
        """Regular farmer cannot list all farmers."""
        resp = await client.get("/api/v1/admin/farmers", headers=auth_headers)
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_list_farmers_success(self, client: AsyncClient):
        """Admin can list all farmers."""
        admin = await _create_admin_user(client)
        headers = {"Authorization": f"Bearer {admin['tokens']['access_token']}"}
        resp = await client.get("/api/v1/admin/farmers", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "farmers" in data["data"]
        assert isinstance(data["data"]["farmers"], list)
        assert "total" in data["data"]

    @pytest.mark.asyncio
    async def test_create_farmer_requires_admin(self, client: AsyncClient, auth_headers: dict):
        """Regular farmer cannot create farmers."""
        resp = await client.post(
            "/api/v1/admin/farmers",
            params={"name": "New Farmer", "phone": "+918888888888"},
            headers=auth_headers,
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_create_farmer_success(self, client: AsyncClient):
        """Admin can create a new farmer."""
        admin = await _create_admin_user(client)
        headers = {"Authorization": f"Bearer {admin['tokens']['access_token']}"}
        resp = await client.post(
            "/api/v1/admin/farmers",
            params={"name": "New Farmer", "phone": "+918888888888", "city": "Warangal"},
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "New Farmer"

    @pytest.mark.asyncio
    async def test_delete_farmer_success(self, client: AsyncClient):
        """Admin can soft-delete (deactivate) a farmer."""
        admin = await _create_admin_user(client)
        headers = {"Authorization": f"Bearer {admin['tokens']['access_token']}"}

        # First create a farmer to delete
        create_resp = await client.post(
            "/api/v1/admin/farmers",
            params={"name": "To Delete", "phone": "+918777777777"},
            headers=headers,
        )
        farmer_id = create_resp.json()["data"]["id"]

        # Now delete
        resp = await client.delete(f"/api/v1/admin/farmers/{farmer_id}", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True


class TestAdminVendors:
    """Test admin vendor management endpoints."""

    @pytest.mark.asyncio
    async def test_list_vendors_requires_admin(self, client: AsyncClient, auth_headers: dict):
        """Regular farmer cannot list all vendors."""
        resp = await client.get("/api/v1/admin/vendors", headers=auth_headers)
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_list_vendors_success(self, client: AsyncClient):
        """Admin can list all vendors."""
        admin = await _create_admin_user(client)
        headers = {"Authorization": f"Bearer {admin['tokens']['access_token']}"}
        resp = await client.get("/api/v1/admin/vendors", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "vendors" in data["data"]
        assert isinstance(data["data"]["vendors"], list)


class TestAdminTokenRefresh:
    """Test POST /api/v1/auth/refresh (token rotation)."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient):
        """Valid refresh token should return new token pair."""
        # Create a user to get tokens
        from tests.conftest import _create_test_user
        user = await _create_test_user(client, "Refresh User", "+919876500001")
        refresh_token = user["tokens"]["refresh_token"]

        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        # New refresh token should be different (rotation)
        assert data["data"]["refresh_token"] != refresh_token

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Invalid refresh token should return 401."""
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token-12345"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_revoked(self, client: AsyncClient):
        """Using an old refresh token after rotation should fail."""
        from tests.conftest import _create_test_user
        user = await _create_test_user(client, "Revoke User", "+919876500002")
        refresh_token = user["tokens"]["refresh_token"]

        # First refresh — should succeed
        resp1 = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp1.status_code == 200

        # Second refresh with OLD token — should fail (revoked)
        resp2 = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp2.status_code == 401
