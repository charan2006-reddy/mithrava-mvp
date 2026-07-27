"""Tests for weather endpoints (mock fallback, no real API key needed)."""

import pytest
from httpx import AsyncClient


class TestWeatherCurrent:
    """Test GET /api/v1/weather/current/{city}."""

    @pytest.mark.asyncio
    async def test_get_current_weather(self, client: AsyncClient):
        resp = await client.get("/api/v1/weather/current/Hyderabad")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        # Should contain weather data (mock or real)
        assert data["data"] is not None


class TestWeatherForecast:
    """Test GET /api/v1/weather/forecast/{city}."""

    @pytest.mark.asyncio
    async def test_get_forecast(self, client: AsyncClient):
        resp = await client.get("/api/v1/weather/forecast/Hyderabad?days=3")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["city"] == "Hyderabad"
        assert data["data"]["days"] == 3

    @pytest.mark.asyncio
    async def test_forecast_default_days(self, client: AsyncClient):
        resp = await client.get("/api/v1/weather/forecast/Hyderabad")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["days"] == 7


class TestWeatherAdvice:
    """Test GET /api/v1/weather/advice."""

    @pytest.mark.asyncio
    async def test_get_farming_advice(self, client: AsyncClient):
        resp = await client.get("/api/v1/weather/advice?city=Hyderabad")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_get_farming_advice_with_crop(self, client: AsyncClient):
        resp = await client.get("/api/v1/weather/advice?city=Hyderabad&crop_type=tomato")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_advice_requires_city(self, client: AsyncClient):
        resp = await client.get("/api/v1/weather/advice")
        assert resp.status_code == 422  # Missing required 'city' param
