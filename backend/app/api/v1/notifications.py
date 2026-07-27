"""Notification API endpoints — list, mark-read, subscribe, device tokens, auto-alerts."""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.device_token import DeviceToken
from app.models.farmer import Farmer
from app.models.notification import Notification
from app.models.push_subscription import PushSubscription
from app.services.notification_service import NotificationService

logger = logging.getLogger("mithrava.notifications")

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class PushSubscriptionRequest(BaseModel):
    """Web Push API subscription from the browser."""

    endpoint: str = Field(..., description="Push service endpoint URL")
    p256dh: str = Field(..., description="P256DH key")
    auth: str = Field(..., description="Auth key")
    user_agent: Optional[str] = Field(default=None, description="Browser user agent")


class DeviceTokenRequest(BaseModel):
    """FCM device token registration from mobile app."""

    token: str = Field(
        ..., min_length=10, max_length=500,
        description="FCM device registration token",
    )
    platform: str = Field(
        default="android",
        description="Device platform: android, ios, or web",
    )
    device_info: Optional[str] = Field(
        default=None, max_length=200,
        description="Device description (e.g. 'Samsung Galaxy S24')",
    )


# ---------------------------------------------------------------------------
# List notifications
# ---------------------------------------------------------------------------


@router.get("/")
async def list_notifications(
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """List notifications for the current farmer.

    Optional query params:
      - type: Filter by notification_type (weather, price, calendar, system)
    """
    query = (
        select(Notification)
        .where(Notification.farmer_id == str(current_user.id))
    )

    if type:
        query = query.where(Notification.notification_type == type)

    query = query.order_by(Notification.created_at.desc()).limit(50)
    result = await db.execute(query)
    notifications = list(result.scalars().all())

    unread_count = await NotificationService.get_unread_count(
        db, str(current_user.id)
    )

    return {
        "success": True,
        "message": "OK",
        "data": {
            "notifications": [
                {
                    "id": str(n.id),
                    "title": n.title,
                    "message": n.message,
                    "notification_type": n.notification_type,
                    "is_read": n.is_read,
                    "action_url": n.action_url,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                }
                for n in notifications
            ],
            "total": len(notifications),
            "unread_count": unread_count,
        },
    }


# ---------------------------------------------------------------------------
# Unread count (lightweight endpoint for header badge)
# ---------------------------------------------------------------------------


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Get the count of unread notifications for the current farmer."""
    count = await NotificationService.get_unread_count(
        db, str(current_user.id)
    )
    return {
        "success": True,
        "message": "OK",
        "data": {"count": count},
    }


# ---------------------------------------------------------------------------
# Mark as read
# ---------------------------------------------------------------------------


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Mark a single notification as read."""
    found = await NotificationService.mark_read(
        db, notification_id, str(current_user.id)
    )
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )
    return {
        "success": True,
        "message": "Notification marked as read",
        "data": {"id": notification_id, "is_read": True},
    }


@router.put("/read-all")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Mark all notifications as read for the current farmer."""
    count = await NotificationService.mark_all_read(
        db, str(current_user.id)
    )
    return {
        "success": True,
        "message": f"{count} notifications marked as read",
        "data": {"updated_count": count},
    }


# ---------------------------------------------------------------------------
# Push subscription management
# ---------------------------------------------------------------------------


@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_push(
    body: PushSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Register a Web Push subscription for the current farmer.

    The browser sends its PushSubscription object here after
    requesting notification permission via the Push API.
    """
    # Check if this endpoint is already registered
    existing = await db.execute(
        select(PushSubscription).where(
            PushSubscription.farmer_id == str(current_user.id),
            PushSubscription.endpoint == body.endpoint,
        )
    )
    if existing.scalar_one_or_none():
        # Update last_used_at
        sub = existing.scalar_one_or_none()
        sub.last_used_at = func.now()  # type: ignore
        await db.flush()
        return {
            "success": True,
            "message": "Subscription updated",
            "data": {"endpoint": body.endpoint},
        }

    subscription = PushSubscription(
        farmer_id=str(current_user.id),
        endpoint=body.endpoint,
        p256dh=body.p256dh,
        auth=body.auth,
        user_agent=body.user_agent,
    )
    db.add(subscription)
    await db.flush()

    return {
        "success": True,
        "message": "Subscription registered",
        "data": {"endpoint": body.endpoint},
    }


@router.delete("/subscribe")
async def unsubscribe_push(
    endpoint: str,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Remove a push subscription by endpoint URL."""
    from sqlalchemy import delete

    result = await db.execute(
        delete(PushSubscription).where(
            PushSubscription.farmer_id == str(current_user.id),
            PushSubscription.endpoint == endpoint,
        )
    )
    await db.flush()

    return {
        "success": True,
        "message": "Subscription removed",
        "data": None,
    }


# ---------------------------------------------------------------------------
# Device Token management (FCM mobile push)
# ---------------------------------------------------------------------------


@router.post("/device-token", status_code=status.HTTP_201_CREATED)
async def register_device_token(
    body: DeviceTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Register or update an FCM device token for push notifications.

    The mobile app should call this on every launch and whenever the
    FCM token rotates. If the token already exists for this farmer,
    it is reactivated and updated.
    """
    farmer_id = str(current_user.id)

    # Check if token already exists (any farmer — a device can be re-registered)
    existing = await db.execute(
        select(DeviceToken).where(DeviceToken.token == body.token)
    )
    existing_token = existing.scalar_one_or_none()

    if existing_token:
        if existing_token.farmer_id != farmer_id:
            # Token was previously registered to a different farmer — reassign
            existing_token.farmer_id = farmer_id
        existing_token.platform = body.platform
        existing_token.device_info = body.device_info
        existing_token.is_active = True
        existing_token.last_used_at = datetime.now(timezone.utc)
        await db.flush()
        return {
            "success": True,
            "message": "Device token updated",
            "data": {"id": existing_token.id, "is_new": False},
        }

    # Check if farmer already has a token for this platform — deactivate old ones
    old_tokens = await db.execute(
        select(DeviceToken).where(
            DeviceToken.farmer_id == farmer_id,
            DeviceToken.platform == body.platform,
            DeviceToken.is_active == True,  # noqa: E712
        )
    )
    for old in old_tokens.scalars().all():
        old.is_active = False

    # Create new token
    device_token = DeviceToken(
        farmer_id=farmer_id,
        token=body.token,
        platform=body.platform,
        device_info=body.device_info,
        is_active=True,
        last_used_at=datetime.now(timezone.utc),
    )
    db.add(device_token)
    await db.flush()

    logger.info(
        "Device token registered: farmer=%s platform=%s", farmer_id, body.platform
    )

    return {
        "success": True,
        "message": "Device token registered",
        "data": {"id": device_token.id, "is_new": True},
    }


@router.delete("/device-token")
async def remove_device_token(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Remove (deactivate) a device token. Called on logout or app uninstall."""
    result = await db.execute(
        select(DeviceToken).where(
            DeviceToken.farmer_id == str(current_user.id),
            DeviceToken.token == token,
        )
    )
    device_token = result.scalar_one_or_none()
    if device_token:
        device_token.is_active = False
        await db.flush()

    return {
        "success": True,
        "message": "Device token removed",
        "data": None,
    }
