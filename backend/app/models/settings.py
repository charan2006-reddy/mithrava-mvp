"""
FarmerSetting Model — Per-farmer application preferences.

Stores UI and notification preferences such as language, voice settings,
and notification toggles. The primary key is the farmer_id itself (1:1).
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.farmer import Farmer


class FarmerSetting(Base):
    """Farmer settings table — 1:1 extension of the farmers table."""

    __tablename__ = "farmer_settings"

    # ── Columns ────────────────────────────────────────────────────────
    farmer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("farmers.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Primary key — same as farmer ID",
    )
    preferred_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
        comment="Preferred UI language ISO 639-1",
    )
    voice_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Enable voice input"
    )
    auto_speak: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Auto-read responses aloud"
    )
    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="Receive push notifications"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="Record creation timestamp"
    )

    # ── Relationships ──────────────────────────────────────────────────
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="setting")

    def __repr__(self) -> str:
        return (
            f"<FarmerSetting(farmer_id={self.farmer_id}, "
            f"lang={self.preferred_language!r}, voice={self.voice_enabled})>"
        )
