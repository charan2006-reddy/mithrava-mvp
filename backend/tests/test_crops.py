"""Tests for crop management endpoints."""

import pytest
from httpx import AsyncClient


class TestCropCRUD:
    """Test crop create, read, update, delete."""

    @pytest.mark.asyncio
    async def test_list_crops_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/crops/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["crops"] == []

    @pytest.mark.asyncio
    async def test_create_crop(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/crops/",
            json={
                "name": "Tomato",
                "variety": "Roma",
                "area_acres": 2.5,
                "planting_date": "2025-01-10",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Tomato"
        assert data["data"]["variety"] == "Roma"
        assert "id" in data["data"]

    @pytest.mark.asyncio
    async def test_list_crops_after_create(self, client: AsyncClient, auth_headers: dict):
        await client.post(
            "/api/v1/crops/",
            json={"name": "Rice", "variety": "Sona Masuri", "area_acres": 3.0},
            headers=auth_headers,
        )
        resp = await client.get("/api/v1/crops/", headers=auth_headers)
        data = resp.json()
        assert len(data["data"]["crops"]) >= 1

    @pytest.mark.asyncio
    async def test_get_crop_detail(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/crops/",
            json={"name": "Potato", "variety": "Kufri", "area_acres": 1.0},
            headers=auth_headers,
        )
        crop_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/crops/{crop_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["name"] == "Potato"

    @pytest.mark.asyncio
    async def test_update_crop(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/crops/",
            json={"name": "Cotton", "area_acres": 4.0},
            headers=auth_headers,
        )
        crop_id = create_resp.json()["data"]["id"]

        resp = await client.put(
            f"/api/v1/crops/{crop_id}",
            json={"area_acres": 5.0, "status": "growing"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["area_acres"] == 5.0

    @pytest.mark.asyncio
    async def test_delete_crop(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/crops/",
            json={"name": "Onion", "area_acres": 1.5},
            headers=auth_headers,
        )
        crop_id = create_resp.json()["data"]["id"]

        resp = await client.delete(f"/api/v1/crops/{crop_id}", headers=auth_headers)
        assert resp.status_code == 200

        # Verify deleted
        get_resp = await client.get(f"/api/v1/crops/{crop_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_nonexistent_crop(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/crops/nonexistent-id", headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_no_auth_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/crops/")
        assert resp.status_code in (401, 403)


class TestCropCalendar:
    """Test crop calendar endpoints."""

    @pytest.mark.asyncio
    async def test_daily_actions_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/crops/daily-actions", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["actions"] == []

    @pytest.mark.asyncio
    async def test_crop_calendar_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/crops/calendar", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
