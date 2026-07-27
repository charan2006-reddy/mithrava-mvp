"""Tests for notification endpoints and device token management."""

import pytest
from httpx import AsyncClient
from sqlalchemy import text

from tests.conftest import test_session_factory


class TestNotifications:
    """Test notification endpoints."""

    @pytest.mark.asyncio
    async def test_list_notifications_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/notifications/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["notifications"] == []

    @pytest.mark.asyncio
    async def test_unread_count_zero(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["count"] == 0

    @pytest.mark.asyncio
    async def test_unread_count_with_notifications(self, client: AsyncClient, auth_headers: dict, db_session):
        """Insert notifications directly into DB and verify unread count."""
        from app.core.security import verify_token
        token = auth_headers["Authorization"].replace("Bearer ", "")
        payload = verify_token(token)
        farmer_id = payload.sub

        await db_session.execute(
            text(
                "INSERT INTO notifications (id, farmer_id, title, message, notification_type, is_read, created_at) "
                "VALUES (:id, :farmer_id, :title, :message, :type, :is_read, datetime('now'))"
            ),
            {
                "id": "test-notif-1",
                "farmer_id": farmer_id,
                "title": "Weather Alert",
                "message": "Heavy rain expected tomorrow",
                "type": "weather",
                "is_read": False,
            },
        )
        await db_session.execute(
            text(
                "INSERT INTO notifications (id, farmer_id, title, message, notification_type, is_read, created_at) "
                "VALUES (:id, :farmer_id, :title, :message, :type, :is_read, datetime('now'))"
            ),
            {
                "id": "test-notif-2",
                "farmer_id": farmer_id,
                "title": "Price Alert",
                "message": "Tomato prices up 15%",
                "type": "price",
                "is_read": True,
            },
        )
        await db_session.commit()

        resp = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_list_notifications_filter_by_type(self, client: AsyncClient, auth_headers: dict, db_session):
        """Insert multiple notification types and filter."""
        from app.core.security import verify_token
        token = auth_headers["Authorization"].replace("Bearer ", "")
        farmer_id = verify_token(token).sub

        for i, ntype in enumerate(["weather", "price", "weather"]):
            await db_session.execute(
                text(
                    "INSERT INTO notifications (id, farmer_id, title, message, notification_type, is_read, created_at) "
                    "VALUES (:id, :farmer_id, :title, :message, :type, 0, datetime('now'))"
                ),
                {
                    "id": f"test-notif-filter-{i}",
                    "farmer_id": farmer_id,
                    "title": f"Notification {i}",
                    "message": f"Message {i}",
                    "type": ntype,
                },
            )
        await db_session.commit()

        resp = await client.get("/api/v1/notifications/?type=price", headers=auth_headers)
        data = resp.json()
        for n in data["data"]["notifications"]:
            assert n["notification_type"] == "price"

    @pytest.mark.asyncio
    async def test_no_auth_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/notifications/")
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_mark_as_read(self, client: AsyncClient, auth_headers: dict, db_session):
        """Insert a notification, mark it read, verify."""
        from app.core.security import verify_token
        token = auth_headers["Authorization"].replace("Bearer ", "")
        farmer_id = verify_token(token).sub

        await db_session.execute(
            text(
                "INSERT INTO notifications (id, farmer_id, title, message, notification_type, is_read, created_at) "
                "VALUES (:id, :farmer_id, :title, :message, :type, 0, datetime('now'))"
            ),
            {
                "id": "test-mark-read",
                "farmer_id": farmer_id,
                "title": "Test",
                "message": "Test message",
                "type": "system",
            },
        )
        await db_session.commit()

        resp = await client.put(
            "/api/v1/notifications/test-mark-read/read", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_read"] is True

    @pytest.mark.asyncio
    async def test_mark_all_read(self, client: AsyncClient, auth_headers: dict, db_session):
        """Insert multiple unread notifications and mark all read."""
        from app.core.security import verify_token
        token = auth_headers["Authorization"].replace("Bearer ", "")
        farmer_id = verify_token(token).sub

        for i in range(3):
            await db_session.execute(
                text(
                    "INSERT INTO notifications (id, farmer_id, title, message, notification_type, is_read, created_at) "
                    "VALUES (:id, :farmer_id, :title, :message, :type, 0, datetime('now'))"
                ),
                {
                    "id": f"test-mark-all-{i}",
                    "farmer_id": farmer_id,
                    "title": f"Title {i}",
                    "message": f"Message {i}",
                    "type": "system",
                },
            )
        await db_session.commit()

        resp = await client.put("/api/v1/notifications/read-all", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["updated_count"] == 3


class TestDeviceTokens:
    """Test FCM device token registration endpoints."""

    @pytest.mark.asyncio
    async def test_register_device_token(self, client: AsyncClient, auth_headers: dict):
        """Register a new device token."""
        resp = await client.post(
            "/api/v1/notifications/device-token",
            json={
                "token": "dVz4R8kF7x:APA91bHexampletoken1234567890abcdefghijklmnop",
                "platform": "android",
                "device_info": "Samsung Galaxy S24",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["is_new"] is True

    @pytest.mark.asyncio
    async def test_register_device_token_update(self, client: AsyncClient, auth_headers: dict):
        """Register the same token twice — should update, not duplicate."""
        token_value = "dVz4R8kF7x:APA91bDupTest1234567890abcdefghijklmnop"

        resp1 = await client.post(
            "/api/v1/notifications/device-token",
            json={"token": token_value, "platform": "android"},
            headers=auth_headers,
        )
        assert resp1.status_code == 201
        assert resp1.json()["data"]["is_new"] is True

        resp2 = await client.post(
            "/api/v1/notifications/device-token",
            json={"token": token_value, "platform": "ios", "device_info": "iPhone 15"},
            headers=auth_headers,
        )
        assert resp2.status_code == 201
        assert resp2.json()["data"]["is_new"] is False

    @pytest.mark.asyncio
    async def test_remove_device_token(self, client: AsyncClient, auth_headers: dict):
        """Register then remove a device token."""
        token_value = "dVz4R8kF7x:APA91bRemoveTest1234567890abcdefghijklmnop"

        await client.post(
            "/api/v1/notifications/device-token",
            json={"token": token_value, "platform": "android"},
            headers=auth_headers,
        )

        resp = await client.delete(
            f"/api/v1/notifications/device-token?token={token_value}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    @pytest.mark.asyncio
    async def test_register_device_token_no_auth(self, client: AsyncClient):
        """Device token registration requires authentication."""
        resp = await client.post(
            "/api/v1/notifications/device-token",
            json={"token": "test-token-12345", "platform": "android"},
        )
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_register_device_token_validation(self, client: AsyncClient, auth_headers: dict):
        """Token must be at least 10 characters."""
        resp = await client.post(
            "/api/v1/notifications/device-token",
            json={"token": "short", "platform": "android"},
            headers=auth_headers,
        )
        assert resp.status_code == 422  # Pydantic validation error
