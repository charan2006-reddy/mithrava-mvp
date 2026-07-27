"""Tests for disease detection endpoints."""

import pytest
from httpx import AsyncClient


class TestDiseaseDetection:
    """Test disease detection endpoints."""

    @pytest.mark.asyncio
    async def test_analyze_requires_image(self, client: AsyncClient, auth_headers: dict):
        """Disease analysis requires an image upload."""
        resp = await client.post(
            "/api/v1/disease/analyze",
            headers=auth_headers,
        )
        # Should fail — no image provided
        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_analyze_no_auth(self, client: AsyncClient):
        """Disease analysis requires authentication."""
        resp = await client.post("/api/v1/disease/analyze")
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_history_empty(self, client: AsyncClient, auth_headers: dict):
        """Get disease scan history for authenticated user."""
        resp = await client.get("/api/v1/disease/history", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
