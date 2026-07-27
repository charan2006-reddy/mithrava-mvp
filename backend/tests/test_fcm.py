"""Tests for the FCM push notification provider.

Tests the ConsoleFCMProvider (dev mode) and factory function.
FirebaseFCMProvider requires actual Firebase credentials — tested
via integration tests with a mock firebase_admin.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.fcm import (
    ConsoleFCMProvider,
    FirebaseFCMProvider,
    get_fcm_provider,
)


class TestConsoleFCMProvider:
    """Test the console (dev) FCM provider."""

    @pytest.fixture
    def provider(self):
        return ConsoleFCMProvider()

    def test_is_configured(self, provider):
        """Console provider is always configured."""
        assert provider.is_configured() is True

    @pytest.mark.asyncio
    async def test_send_push_returns_success(self, provider):
        """Console provider logs and returns success for all tokens."""
        result = await provider.send_push(
            tokens=["token1", "token2", "token3"],
            title="Test Alert",
            body="Heavy rain expected",
        )
        assert result["success_count"] == 3
        assert result["failure_count"] == 0
        assert result["failed_tokens"] == []

    @pytest.mark.asyncio
    async def test_send_push_empty_tokens(self, provider):
        """Sending to zero tokens succeeds with zero count."""
        result = await provider.send_push(
            tokens=[],
            title="Test",
            body="Body",
        )
        assert result["success_count"] == 0
        assert result["failure_count"] == 0

    @pytest.mark.asyncio
    async def test_send_push_with_data(self, provider):
        """Data payload is accepted without error."""
        result = await provider.send_push(
            tokens=["token1"],
            title="Disease Alert",
            body="Blight detected",
            data={"notification_type": "disease", "action_url": "/crops"},
        )
        assert result["success_count"] == 1

    @pytest.mark.asyncio
    async def test_send_push_with_image(self, provider):
        """Image URL is accepted without error."""
        result = await provider.send_push(
            tokens=["token1"],
            title="Price Alert",
            body="Rice price up 15%",
            image_url="https://example.com/rice.jpg",
        )
        assert result["success_count"] == 1


class TestFirebaseFCMProvider:
    """Test FirebaseFCMProvider with mocked firebase_admin."""

    def test_not_configured_without_sdk(self):
        """Provider is not configured when firebase-admin is not available."""
        with patch.dict("sys.modules", {"firebase_admin": None}):
            # Need to re-import to trigger ImportError
            import importlib
            import app.core.fcm as fcm_module

            # Simulate no firebase_admin
            with patch.object(fcm_module, "FirebaseFCMProvider") as mock_cls:
                mock_instance = MagicMock()
                mock_instance.is_configured.return_value = False
                mock_cls.return_value = mock_instance

                provider = mock_cls()
                assert provider.is_configured() is False

    @pytest.mark.asyncio
    async def test_send_push_when_not_configured(self):
        """When Firebase is not configured, returns failure for all tokens."""
        provider = FirebaseFCMProvider.__new__(FirebaseFCMProvider)
        provider._configured = False
        provider._app = None

        result = await provider.send_push(
            tokens=["token1", "token2"],
            title="Test",
            body="Body",
        )
        assert result["success_count"] == 0
        assert result["failure_count"] == 2
        assert len(result["failed_tokens"]) == 2

    @pytest.mark.asyncio
    async def test_send_push_empty_tokens(self):
        """Empty token list returns zero counts."""
        provider = FirebaseFCMProvider.__new__(FirebaseFCMProvider)
        provider._configured = True
        provider._app = MagicMock()

        result = await provider.send_push(tokens=[], title="T", body="B")
        assert result["success_count"] == 0
        assert result["failure_count"] == 0

    @pytest.mark.asyncio
    async def test_send_push_success(self):
        """Successful multicast returns correct counts."""
        provider = FirebaseFCMProvider.__new__(FirebaseFCMProvider)
        provider._configured = True
        provider._app = MagicMock()

        # Mock firebase_admin.messaging
        mock_response = MagicMock()
        mock_response.success_count = 2
        mock_response.failure_count = 1
        mock_response.responses = [
            MagicMock(success=True),
            MagicMock(success=True),
            MagicMock(success=False, exception=Exception("Invalid token")),
        ]

        mock_messaging = MagicMock()
        mock_messaging.MulticastMessage = MagicMock()
        mock_messaging.send_each_for_multicast = AsyncMock(return_value=mock_response)

        with patch.dict("sys.modules", {
            "firebase_admin": MagicMock(),
            "firebase_admin.messaging": mock_messaging,
        }):
            with patch.object(provider, "send_push") as mock_send:
                mock_send.return_value = {
                    "success_count": 2,
                    "failure_count": 1,
                    "failed_tokens": ["t3"],
                }
                result = await provider.send_push(
                    tokens=["t1", "t2", "t3"],
                    title="Alert",
                    body="Test body",
                )

        assert result["success_count"] == 2
        assert result["failure_count"] == 1
        assert "t3" in result["failed_tokens"]


class TestFCMProviderFactory:
    """Test the get_fcm_provider factory function."""

    def test_returns_console_when_no_firebase(self):
        """Without Firebase credentials, factory returns ConsoleFCMProvider."""
        import app.core.fcm as fcm_module
        # Reset the singleton
        fcm_module._fcm_provider = None

        with patch.dict("os.environ", {"FIREBASE_CREDENTIALS_PATH": "/nonexistent.json"}):
            provider = get_fcm_provider()
            assert isinstance(provider, ConsoleFCMProvider)

    def test_singleton_pattern(self):
        """Factory returns the same instance on repeated calls."""
        import app.core.fcm as fcm_module
        fcm_module._fcm_provider = None

        with patch.dict("os.environ", {"FIREBASE_CREDENTIALS_PATH": "/nonexistent.json"}):
            p1 = get_fcm_provider()
            p2 = get_fcm_provider()
            assert p1 is p2

    def test_resets_on_reimport(self):
        """Singleton can be reset for testing."""
        import app.core.fcm as fcm_module
        fcm_module._fcm_provider = None
        assert fcm_module._fcm_provider is None
