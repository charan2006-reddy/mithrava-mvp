"""Tests for knowledge base endpoints."""

import pytest
from httpx import AsyncClient


class TestKnowledgeCategories:
    """Test GET /api/v1/knowledge — lists categories."""

    @pytest.mark.asyncio
    async def test_list_categories_empty(self, client: AsyncClient):
        """Categories list should return 200 even with empty DB."""
        resp = await client.get("/api/v1/knowledge")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)


class TestKnowledgeSearch:
    """Test POST /api/v1/knowledge/search."""

    @pytest.mark.asyncio
    async def test_search_requires_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/knowledge/search",
            json={"query": "tomato disease"},
        )
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_search_empty_results(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/knowledge/search",
            json={"query": "tomato disease", "k": 5},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)


class TestKnowledgeAsk:
    """Test POST /api/v1/knowledge/ask (RAG Q&A)."""

    @pytest.mark.asyncio
    async def test_ask_requires_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/knowledge/ask",
            json={"question": "How to treat blight in tomatoes?"},
        )
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_ask_empty_kb(self, client: AsyncClient, auth_headers: dict):
        """Ask a question when knowledge base is empty — should still return."""
        resp = await client.post(
            "/api/v1/knowledge/ask",
            json={"question": "How to treat blight in tomatoes?"},
            headers=auth_headers,
        )
        # May return 200 with a fallback answer or 500 if LLM is unavailable
        assert resp.status_code in (200, 500)


class TestKnowledgeSeed:
    """Test POST /api/v1/knowledge/seed."""

    @pytest.mark.asyncio
    async def test_seed_requires_auth(self, client: AsyncClient):
        resp = await client.post("/api/v1/knowledge/seed")
        assert resp.status_code in (401, 403)
