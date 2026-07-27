"""Notification service — creates, queries, and auto-generates notifications.

Handles notification creation for:
  - Weather alerts (frost, heavy rain, heat wave)
  - Price spike alerts (crop price > threshold)
  - Calendar reminders (sowing, irrigation, harvest)
  - System notifications (tips, scheme updates)

Every notification is persisted in-app AND delivered as a push
notification (FCM) when the farmer has registered device tokens.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device_token import DeviceToken
from app.models.notification import Notification

logger = logging.getLogger("mithrava.notifications")


class NotificationService:
    """Service for creating and managing farmer notifications."""

    # -------------------------------------------------------------------
    # Core CRUD
    # -------------------------------------------------------------------

    @staticmethod
    async def create(
        db: AsyncSession,
        farmer_id: str,
        title: str,
        message: str,
        notification_type: str,
        action_url: Optional[str] = None,
        send_push: bool = True,
    ) -> Notification:
        """Create and persist a notification, then send push delivery.

        Args:
            db: Async database session.
            farmer_id: Target farmer's ID.
            title: Short notification title.
            message: Full notification body.
            notification_type: Category (weather, price, calendar, system, info).
            action_url: Optional deep-link URL.
            send_push: Whether to also deliver via FCM push (default True).

        Returns:
            The created Notification.
        """
        notification = Notification(
            farmer_id=farmer_id,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
        )
        db.add(notification)
        await db.flush()
        await db.refresh(notification)
        logger.info("Notification created: %s → %s", notification_type, farmer_id)

        # Send push notification asynchronously (fire-and-forget style)
        if send_push:
            await NotificationService._send_push(
                db=db,
                farmer_id=farmer_id,
                title=title,
                body=message,
                notification_type=notification_type,
                action_url=action_url,
            )

        return notification

    @staticmethod
    async def get_unread_count(db: AsyncSession, farmer_id: str) -> int:
        """Count unread notifications for a farmer."""
        result = await db.execute(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.farmer_id == farmer_id,
                Notification.is_read == False,  # noqa: E712
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def mark_read(db: AsyncSession, notification_id: str, farmer_id: str) -> bool:
        """Mark a single notification as read. Returns True if found."""
        result = await db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.farmer_id == farmer_id,
            )
        )
        notification = result.scalar_one_or_none()
        if notification is None:
            return False
        notification.is_read = True
        await db.flush()
        return True

    @staticmethod
    async def mark_all_read(db: AsyncSession, farmer_id: str) -> int:
        """Mark all unread notifications as read. Returns count updated."""
        from sqlalchemy import update

        result = await db.execute(
            update(Notification)
            .where(
                Notification.farmer_id == farmer_id,
                Notification.is_read == False,  # noqa: E712
            )
            .values(is_read=True)
        )
        await db.flush()
        return result.rowcount  # type: ignore

    # -------------------------------------------------------------------
    # Push delivery helper
    # -------------------------------------------------------------------

    @staticmethod
    async def _send_push(
        db: AsyncSession,
        farmer_id: str,
        title: str,
        body: str,
        notification_type: str,
        action_url: Optional[str] = None,
    ) -> None:
        """Send push notification via FCM to all of a farmer's devices.

        Looks up active DeviceToken rows for the farmer, sends via the
        configured FCM provider, and deactivates any invalid tokens.
        """
        try:
            from app.core.fcm import get_fcm_provider

            # Fetch active device tokens for this farmer
            result = await db.execute(
                select(DeviceToken.token).where(
                    DeviceToken.farmer_id == farmer_id,
                    DeviceToken.is_active == True,  # noqa: E712
                )
            )
            tokens = [row[0] for row in result.all()]

            if not tokens:
                return  # No devices registered — skip push

            # Build data payload for deep-linking in the app
            data = {"notification_type": notification_type}
            if action_url:
                data["action_url"] = action_url

            fcm = get_fcm_provider()
            response = await fcm.send_push(
                tokens=tokens,
                title=title,
                body=body,
                data=data,
            )

            # Clean up invalid tokens
            if response.get("failed_tokens"):
                await NotificationService._cleanup_invalid_tokens(
                    db, response["failed_tokens"]
                )

            logger.info(
                "Push delivered for farmer %s: %d success, %d failed",
                farmer_id,
                response.get("success_count", 0),
                response.get("failure_count", 0),
            )

        except Exception as exc:
            # Push failure should never break notification creation
            logger.error("Push delivery failed for farmer %s: %s", farmer_id, exc)

    @staticmethod
    async def _cleanup_invalid_tokens(
        db: AsyncSession, invalid_tokens: list[str]
    ) -> None:
        """Deactivate device tokens that FCM rejected as invalid."""
        if not invalid_tokens:
            return

        from sqlalchemy import update

        await db.execute(
            update(DeviceToken)
            .where(DeviceToken.token.in_(invalid_tokens))
            .values(is_active=False)
        )
        await db.flush()
        logger.info("Deactivated %d invalid device tokens", len(invalid_tokens))

    # -------------------------------------------------------------------
    # Auto-trigger notification helpers
    # -------------------------------------------------------------------

    @staticmethod
    async def create_weather_alert(
        db: AsyncSession,
        farmer_id: str,
        alert_type: str,
        weather_summary: str,
        city: str,
    ) -> Optional[Notification]:
        """Create a weather alert notification.

        Alert types: frost, heavy_rain, heat_wave, strong_wind, high_humidity.
        Deduplicates within 6 hours to avoid spam.
        """
        # Check for recent duplicate (avoid spam)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=6)
        dup_check = await db.execute(
            select(Notification).where(
                Notification.farmer_id == farmer_id,
                Notification.notification_type == "weather",
                Notification.created_at >= cutoff,
            )
        )
        if dup_check.scalar_one_or_none():
            return None  # Already notified recently

        titles = {
            "frost": "❄️ Frost Warning",
            "heavy_rain": "🌧️ Heavy Rain Alert",
            "heat_wave": "🔥 Heat Wave Warning",
            "strong_wind": "💨 Strong Wind Alert",
            "high_humidity": "💧 High Humidity Alert",
        }

        tips = {
            "frost": "Cover sensitive crops with plastic sheets or straw mulch. Avoid irrigation tonight.",
            "heavy_rain": "Delay any planned spraying. Ensure proper field drainage. Check stored grain for moisture.",
            "heat_wave": "Increase irrigation frequency. Provide shade for young seedlings. Avoid field work during peak hours.",
            "strong_wind": "Secure tall crops with stakes. Delay pesticide spraying. Check greenhouse structures.",
            "high_humidity": "Watch for fungal diseases. Improve air circulation. Apply preventive fungicide if needed.",
        }

        title = titles.get(alert_type, "⚠️ Weather Alert")
        tip = tips.get(alert_type, "Stay safe and monitor weather updates.")
        message = f"{weather_summary} in {city}. {tip}"

        return await NotificationService.create(
            db=db,
            farmer_id=farmer_id,
            title=title,
            message=message,
            notification_type="weather",
            action_url="/weather",
        )

    @staticmethod
    async def create_price_alert(
        db: AsyncSession,
        farmer_id: str,
        crop_name: str,
        current_price: float,
        change_percent: float,
        mandi: str = "Mandi",
    ) -> Optional[Notification]:
        """Create a price alert notification.

        Triggers when a crop's price changes significantly (>10%).
        """
        direction = "risen" if change_percent > 0 else "dropped"
        emoji = "📈" if change_percent > 0 else "📉"

        title = f"{emoji} {crop_name} Price {direction.capitalize()}"
        message = (
            f"{crop_name} price at {mandi} has {direction} by "
            f"{abs(change_percent):.1f}% to ₹{current_price:,.0f}/quintal. "
        )

        if change_percent > 15:
            message += "Consider selling soon for good profit!"
        elif change_percent < -15:
            message += "Consider holding or checking other mandis."

        return await NotificationService.create(
            db=db,
            farmer_id=farmer_id,
            title=title,
            message=message,
            notification_type="price",
            action_url="/market",
        )

    @staticmethod
    async def create_calendar_reminder(
        db: AsyncSession,
        farmer_id: str,
        crop_name: str,
        task: str,
        days_until: int,
    ) -> Optional[Notification]:
        """Create a calendar/task reminder notification."""
        if days_until == 0:
            prefix = "📌 Today: "
        elif days_until == 1:
            prefix = "📌 Tomorrow: "
        else:
            prefix = f"📌 In {days_until} days: "

        title = f"{prefix}{task}"
        message = f"{task} for your {crop_name} crop"
        if days_until > 0:
            message += f" (due in {days_until} days)"
        message += "."

        return await NotificationService.create(
            db=db,
            farmer_id=farmer_id,
            title=title,
            message=message,
            notification_type="calendar",
            action_url="/crops",
        )

    @staticmethod
    async def create_disease_alert(
        db: AsyncSession,
        farmer_id: str,
        crop_name: str,
        disease_name: str,
        severity: str,
        confidence: float,
    ) -> Notification:
        """Create a disease detection alert notification.

        Called after disease scan completes to notify the farmer
        of the diagnosis and recommended action.
        """
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "info": "ℹ️",
        }
        emoji = severity_emoji.get(severity, "⚠️")

        title = f"{emoji} Disease Detected: {disease_name}"
        message = (
            f"Your {crop_name} crop may have {disease_name}. "
            f"Severity: {severity.upper()} (confidence: {confidence:.0f}%). "
            f"Tap to view treatment recommendations."
        )

        return await NotificationService.create(
            db=db,
            farmer_id=farmer_id,
            title=title,
            message=message,
            notification_type="disease",
            action_url="/crops",
        )

    @staticmethod
    async def create_system_notification(
        db: AsyncSession,
        farmer_id: str,
        title: str,
        message: str,
        action_url: Optional[str] = None,
    ) -> Notification:
        """Create a system notification (tips, scheme updates, etc.)."""
        return await NotificationService.create(
            db=db,
            farmer_id=farmer_id,
            title=title,
            message=message,
            notification_type="system",
            action_url=action_url,
        )
