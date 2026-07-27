"""Tests for support call endpoints."""

import pytest
from httpx import AsyncClient


class TestSupportCalls:
    """Test support endpoints."""

    @pytest.mark.asyncio
    async def test_request_expert_call(self, client: AsyncClient, auth_headers: dict):
        """Any authenticated farmer can request an expert callback."""
        resp = await client.post(
            "/api/v1/support/request-call",
            params={"topic": "pest_control", "description": "Aphids on cotton"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["topic"] == "pest_control"
        assert data["data"]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_support_calls_requires_admin(self, client: AsyncClient, auth_headers: dict):
        """GET /support/calls requires admin role."""
        resp = await client.get("/api/v1/support/calls", headers=auth_headers)
        assert resp.status_code == 403
