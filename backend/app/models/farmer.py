"""Farmer ORM model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.crop import Crop
    from app.models.finance import Expense, Income
    from app.models.audit_log import AuditLog
    from app.models.expert_call import ExpertCall
    from app.models.refresh_token import RefreshToken
    from app.models.settings import FarmerSetting
    from app.models.land import Land


class Farmer(Base):
    """Farmer entity representing a platform user.

    Stores profile information, authentication data, and preferences.
    """

    __tablename__ = "farmers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(5), default="en")
    farm_size_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    irrigation_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(20), default="farmer")
    refresh_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────
    crops: Mapped[List["Crop"]] = relationship(
        "Crop", back_populates="farmer", cascade="all, delete-orphan", lazy="selectin"
    )
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense", back_populates="farmer", cascade="all, delete-orphan", lazy="noload"
    )
    incomes: Mapped[List["Income"]] = relationship(
        "Income", back_populates="farmer", cascade="all, delete-orphan", lazy="noload"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="farmer", lazy="noload"
    )
    expert_calls: Mapped[List["ExpertCall"]] = relationship(
        "ExpertCall", back_populates="farmer", lazy="noload"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="farmer", cascade="all, delete-orphan", lazy="noload"
    )
    setting: Mapped[Optional["FarmerSetting"]] = relationship(
        "FarmerSetting", back_populates="farmer", uselist=False, lazy="selectin"
    )
    lands: Mapped[List["Land"]] = relationship(
        "Land", back_populates="farmer", cascade="all, delete-orphan", lazy="selectin"
    )
