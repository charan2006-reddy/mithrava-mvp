"""Tests for forum endpoints: posts, comments, likes."""

import pytest
from httpx import AsyncClient


class TestForumPosts:
    """Test forum post CRUD."""

    @pytest.mark.asyncio
    async def test_list_posts_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/forum/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["posts"] == []

    @pytest.mark.asyncio
    async def test_create_post(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/forum/",
            json={
                "title": "Best fertilizer for tomato?",
                "content": "I have been using Urea but my tomato plants look yellow. Any suggestions?",
                "category": "crop_care",
                "tags": ["tomato", "fertilizer"],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["title"] == "Best fertilizer for tomato?"

    @pytest.mark.asyncio
    async def test_list_posts_after_create(self, client: AsyncClient, auth_headers: dict):
        # Create a post
        await client.post(
            "/api/v1/forum/",
            json={"title": "Test Post", "content": "Test content", "category": "tips"},
            headers=auth_headers,
        )

        # List
        resp = await client.get("/api/v1/forum/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]["posts"]) >= 1

    @pytest.mark.asyncio
    async def test_list_posts_filter_by_category(self, client: AsyncClient, auth_headers: dict):
        await client.post(
            "/api/v1/forum/",
            json={"title": "Weather Question", "content": "Is rain expected?", "category": "weather"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/forum/",
            json={"title": "Pest Problem", "content": "Aphids on cotton", "category": "pest_control"},
            headers=auth_headers,
        )

        resp = await client.get("/api/v1/forum/?category=weather")
        data = resp.json()
        for post in data["data"]["posts"]:
            assert post["category"] == "weather"


class TestForumComments:
    """Test forum comments."""

    @pytest.mark.asyncio
    async def test_add_comment(self, client: AsyncClient, auth_headers: dict):
        # Create a post (content must be >= 10 chars per schema)
        post_resp = await client.post(
            "/api/v1/forum/",
            json={"title": "Comment Test Post", "content": "This is a test post for comments.", "category": "tips"},
            headers=auth_headers,
        )
        post_id = post_resp.json()["data"]["id"]

        # Add comment
        resp = await client.post(
            f"/api/v1/forum/{post_id}/comment",
            json={"content": "Great post! I agree."},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["content"] == "Great post! I agree."

    @pytest.mark.asyncio
    async def test_comment_nonexistent_post(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/forum/nonexistent/comment",
            json={"content": "test"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestForumLikes:
    """Test forum like toggle."""

    @pytest.mark.asyncio
    async def test_like_post(self, client: AsyncClient, auth_headers: dict):
        post_resp = await client.post(
            "/api/v1/forum/",
            json={"title": "Like Test Post", "content": "This is a test post for likes.", "category": "tips"},
            headers=auth_headers,
        )
        post_id = post_resp.json()["data"]["id"]

        # Like
        resp = await client.post(f"/api/v1/forum/{post_id}/like", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["liked"] is True
        assert data["data"]["likes_count"] == 1

    @pytest.mark.asyncio
    async def test_toggle_like_off(self, client: AsyncClient, auth_headers: dict):
        post_resp = await client.post(
            "/api/v1/forum/",
            json={"title": "Toggle Test Post", "content": "This is a test post for toggling likes.", "category": "tips"},
            headers=auth_headers,
        )
        post_id = post_resp.json()["data"]["id"]

        # Like
        await client.post(f"/api/v1/forum/{post_id}/like", headers=auth_headers)
        # Unlike
        resp = await client.post(f"/api/v1/forum/{post_id}/like", headers=auth_headers)
        data = resp.json()
        assert data["data"]["liked"] is False
        assert data["data"]["likes_count"] == 0

    @pytest.mark.asyncio
    async def test_like_nonexistent_post(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/v1/forum/nonexistent/like", headers=auth_headers)
        assert resp.status_code == 404
