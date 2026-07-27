"""Tests for farmer profile endpoints."""

import pytest
from httpx import AsyncClient


class TestFarmerProfile:
    """Test farmer profile CRUD."""

    @pytest.mark.asyncio
    async def test_get_my_profile(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/farmers/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Farmer"
        assert data["data"]["city"] == "Hyderabad"

    @pytest.mark.asyncio
    async def test_get_my_profile_no_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/farmers/me")
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_update_my_profile(self, client: AsyncClient, auth_headers: dict):
        resp = await client.put(
            "/api/v1/farmers/me",
            json={
                "city": "Warangal",
                "farm_size_acres": 5.5,
                "soil_type": "red",
                "irrigation_type": "drip",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["city"] == "Warangal"
        assert data["data"]["farm_size_acres"] == 5.5

    @pytest.mark.asyncio
    async def test_update_partial(self, client: AsyncClient, auth_headers: dict):
        resp = await client.put(
            "/api/v1/farmers/me",
            json={"preferred_language": "te"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["preferred_language"] == "te"


class TestFarmerStats:
    """Test GET /api/v1/farmers/me/stats."""

    @pytest.mark.asyncio
    async def test_get_stats(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/farmers/me/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        # Stats should be a dict with various keys
        assert isinstance(data["data"], dict)


class TestFarmerAdmin:
    """Test admin-only farmer endpoints."""

    @pytest.mark.asyncio
    async def test_list_farmers_requires_admin(self, client: AsyncClient, auth_headers: dict):
        """Regular farmer cannot list all farmers."""
        resp = await client.get("/api/v1/farmers/", headers=auth_headers)
        assert resp.status_code == 403
