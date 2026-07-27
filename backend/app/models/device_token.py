"""Device token ORM model for FCM push notifications.

Stores Firebase Cloud Messaging (FCM) device registration tokens,
one per device per farmer. Used for mobile push notifications.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DeviceToken(Base):
    """FCM device token for push notifications.

    Each row represents one device (phone/tablet) registered for push.
    A farmer may have multiple devices. Tokens are invalidated when the
    app is uninstalled or the token rotates.
    """

    __tablename__ = "device_tokens"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    farmer_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(
        String(500), nullable=False, unique=True, index=True
    )
    platform: Mapped[str] = mapped_column(
        String(10), nullable=False, default="android"
    )  # android | ios | web
    device_info: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )  # e.g. "Samsung Galaxy S24"
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_device_tokens_farmer_active", "farmer_id", "is_active"),
    )
