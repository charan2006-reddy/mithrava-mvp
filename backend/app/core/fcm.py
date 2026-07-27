"""Firebase Cloud Messaging (FCM) push notification provider.

Sends push notifications to Android/iOS devices via FCM HTTP v1 API.
Falls back to console logging when Firebase is not configured (dev mode).

Configuration via environment variables:
  - FIREBASE_CREDENTIALS_PATH: Path to Firebase service account JSON file
    (default: "firebase-service-account.json" in project root)

Provider pattern mirrors app/core/sms.py for consistency.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mithrava.fcm")


class FCMProvider(ABC):
    """Abstract base class for push notification providers."""

    @abstractmethod
    async def send_push(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a push notification to one or more device tokens.

        Args:
            tokens: List of FCM device registration tokens.
            title: Notification title.
            body: Notification body text.
            data: Optional key-value data payload (deep-link info, etc.).
            image_url: Optional image URL for rich notifications.

        Returns:
            Dict with 'success_count' and 'failure_count' and optional 'failed_tokens'.
        """
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider has all required credentials."""
        ...


class FirebaseFCMProvider(FCMProvider):
    """Production FCM provider using firebase-admin SDK.

    Requires:
      - firebase-admin package installed
      - Firebase service account credentials (path in FIREBASE_CREDENTIALS_PATH)

    Uses FCM HTTP v1 API via firebase-admin.messaging.send_each_for_multicast().
    """

    def __init__(self):
        self._app = None
        self._configured = False
        self._initialize()

    def _initialize(self) -> None:
        """Attempt to initialize the Firebase Admin SDK."""
        try:
            import firebase_admin
            from firebase_admin import credentials

            # Resolve credentials path
            creds_path = os.environ.get(
                "FIREBASE_CREDENTIALS_PATH", "firebase-service-account.json"
            )

            if not os.path.exists(creds_path):
                logger.warning(
                    "Firebase credentials not found at %s — FCM disabled", creds_path
                )
                return

            cred = credentials.Certificate(creds_path)
            self._app = firebase_admin.initialize_app(cred)
            self._configured = True
            logger.info("Firebase Admin SDK initialized from %s", creds_path)

        except ImportError:
            logger.warning(
                "firebase-admin package not installed — FCM disabled. "
                "Install with: pip install firebase-admin"
            )
        except Exception as exc:
            logger.error("Firebase Admin SDK initialization failed: %s", exc)

    def is_configured(self) -> bool:
        return self._configured

    async def send_push(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send push notification via Firebase Admin SDK.

        Uses MulticastMessage to batch-send to multiple tokens efficiently.
        Automatically cleans up invalid tokens (returns failed token list).
        """
        if not self._configured:
            logger.warning("FCM not configured — skipping push to %d tokens", len(tokens))
            return {"success_count": 0, "failure_count": len(tokens), "failed_tokens": tokens}

        if not tokens:
            return {"success_count": 0, "failure_count": 0, "failed_tokens": []}

        try:
            from firebase_admin import messaging

            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url,
            )

            # Build Android config with default channel
            android_config = messaging.AndroidConfig(
                notification=messaging.AndroidNotification(
                    channel_id="mithrava_alerts",
                    priority="high",
                ),
            )

            # Build APNS config for iOS
            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(title=title, body=body),
                        badge=1,
                        sound="default",
                    )
                ),
            )

            # Build multicast message
            multicast = messaging.MulticastMessage(
                notification=notification,
                tokens=tokens,
                data=data or {},
                android=android_config,
                apns=apns_config,
            )

            # Send in batch
            response = messaging.send_each_for_multicast(multicast)

            # Identify failed tokens for cleanup
            failed_tokens: List[str] = []
            for idx, send_response in enumerate(response.responses):
                if not send_response.success:
                    logger.warning(
                        "FCM send failed for token index %d: %s",
                        idx,
                        send_response.exception,
                    )
                    failed_tokens.append(tokens[idx])

            logger.info(
                "FCM multicast: %d success, %d failed out of %d tokens",
                response.success_count,
                response.failure_count,
                len(tokens),
            )

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "failed_tokens": failed_tokens,
            }

        except ImportError:
            logger.error("firebase-admin package not installed")
            return {"success_count": 0, "failure_count": len(tokens), "failed_tokens": tokens}
        except Exception as exc:
            logger.error("FCM send failed: %s", exc)
            return {"success_count": 0, "failure_count": len(tokens), "failed_tokens": tokens}


class ConsoleFCMProvider(FCMProvider):
    """Dev/demo provider that logs push notifications to console.

    Used when Firebase is not configured, or in development mode.
    """

    def is_configured(self) -> bool:
        return True

    async def send_push(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Log push notification to console (dev mode)."""
        logger.info(
            "📱 [DEV PUSH] Title: %s | Body: %s | Tokens: %d",
            title,
            body,
            len(tokens),
        )
        print(f"\n{'='*60}")
        print(f"  📱 PUSH NOTIFICATION (DEV)")
        print(f"  Title: {title}")
        print(f"  Body:  {body}")
        print(f"  To:    {len(tokens)} device(s)")
        if data:
            print(f"  Data:  {json.dumps(data, indent=2)}")
        if image_url:
            print(f"  Image: {image_url}")
        print(f"{'='*60}\n")
        return {
            "success_count": len(tokens),
            "failure_count": 0,
            "failed_tokens": [],
        }


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------

_fcm_provider: Optional[FCMProvider] = None


def get_fcm_provider() -> FCMProvider:
    """Get the configured FCM provider.

    Reads FIREBASE_CREDENTIALS_PATH env var. If Firebase SDK is installed
    and credentials exist, uses FirebaseFCMProvider. Otherwise falls back
    to ConsoleFCMProvider for development.

    Returns:
        Configured FCMProvider instance (singleton).
    """
    global _fcm_provider
    if _fcm_provider is not None:
        return _fcm_provider

    firebase_path = os.environ.get(
        "FIREBASE_CREDENTIALS_PATH", "firebase-service-account.json"
    )

    # Try Firebase first
    provider = FirebaseFCMProvider()
    if provider.is_configured():
        logger.info("Using Firebase FCM provider (production)")
        _fcm_provider = provider
        return _fcm_provider

    # Fall back to console
    logger.info("Using console FCM provider (development)")
    _fcm_provider = ConsoleFCMProvider()
    return _fcm_provider
