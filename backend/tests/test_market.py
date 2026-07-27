"""Tests for market price endpoints (no auth required)."""

import pytest
from httpx import AsyncClient


class TestMarketCrops:
    """Test GET /api/v1/market/crops."""

    @pytest.mark.asyncio
    async def test_list_crops(self, client: AsyncClient):
        resp = await client.get("/api/v1/market/crops")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        crops = data["data"]
        assert isinstance(crops, list)
        assert len(crops) > 0
        assert "key" in crops[0]
        assert "name" in crops[0]


class TestMarketPrices:
    """Test GET /api/v1/market/prices."""

    @pytest.mark.asyncio
    async def test_list_all_prices(self, client: AsyncClient):
        resp = await client.get("/api/v1/market/prices")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "crops" in data["data"]
        assert len(data["data"]["crops"]) > 0

    @pytest.mark.asyncio
    async def test_get_single_crop_price(self, client: AsyncClient):
        resp = await client.get("/api/v1/market/prices?crop=rice")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        crops = data["data"]["crops"]
        assert len(crops) == 1
        assert crops[0]["name"] == "Rice (Paddy)"

    @pytest.mark.asyncio
    async def test_get_unknown_crop(self, client: AsyncClient):
        resp = await client.get("/api/v1/market/prices?crop=bananas")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False


class TestMarketTrend:
    """Test GET /api/v1/market/trend."""

    @pytest.mark.asyncio
    async def test_get_trend(self, client: AsyncClient):
        resp = await client.get("/api/v1/market/trend?crop=rice&days=14")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["crop"] == "rice"
        assert len(data["data"]["trend"]) == 14
        assert "summary" in data["data"]
        assert "best_day_to_sell" in data["data"]["summary"]

    @pytest.mark.asyncio
    async def test_trend_requires_crop(self, client: AsyncClient):
        resp = await client.get("/api/v1/market/trend")
        assert resp.status_code == 422  # Missing required 'crop' param


class TestMarketMarkets:
    """Test GET /api/v1/market/markets."""

    @pytest.mark.asyncio
    async def test_list_markets(self, client: AsyncClient):
        resp = await client.get("/api/v1/market/markets")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert "Hyderabad" in data["data"]
