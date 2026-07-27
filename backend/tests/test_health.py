"""Tests for health check and root endpoints."""

import pytest
from httpx import AsyncClient


class TestHealthCheck:
    """Test /health endpoint."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mithrava-api"
        assert data["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_root_returns_200(self, client: AsyncClient):
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "Mithrava" in data["service"]
        assert data["version"] == "1.0.0"
