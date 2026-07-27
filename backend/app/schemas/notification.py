"""Notification schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Schema for a notification in API responses."""

    id: str
    farmer_id: str
    title: str
    message: str
    notification_type: str = Field(
        ...,
        pattern=r"^(weather_alert|disease_alert|market_update|forum_reply|system|reminder)$",
    )
    is_read: bool = Field(default=False)
    action_url: Optional[str] = Field(default=None, description="Deep link or URL")
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Paginated list of notifications."""

    notifications: list[NotificationResponse]
    total: int
    unread_count: int
