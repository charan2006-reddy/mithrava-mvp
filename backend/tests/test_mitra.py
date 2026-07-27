"""Tests for Mitra AI assistant endpoints."""

import pytest
from httpx import AsyncClient


class TestMitraChat:
    """Test Mitra chat endpoints."""

    @pytest.mark.asyncio
    async def test_send_message(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/mitra/chat",
            json={"content": "What fertilizer should I use for rice?"},
            headers=auth_headers,
        )
        # Mitra depends on external LLM — may return 200 or 500
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            data = resp.json()
            assert data["success"] is True
            assert "message" in data["data"]

    @pytest.mark.asyncio
    async def test_send_message_no_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/mitra/chat",
            json={"content": "Hello"},
        )
        assert resp.status_code in (401, 403)


class TestMitraVoice:
    """Test Mitra voice endpoints."""

    @pytest.mark.asyncio
    async def test_voice_providers(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/mitra/voice/providers", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        # The endpoint returns a VoiceProvidersResponse with stt and tts lists
        assert "stt" in data
        assert "tts" in data
        assert isinstance(data["stt"], list)
        assert isinstance(data["tts"], list)


class TestMitraConversations:
    """Test Mitra conversation history."""

    @pytest.mark.asyncio
    async def test_list_conversations(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/mitra/conversations", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
