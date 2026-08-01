"""
OTP Code Model — Phone-based one-time password authentication.

Stores time-limited OTPs for phone number verification during login
or registration. Each code is single-use and expires after a set period.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OTPCode(Base):
    """OTP codes table — temporary phone verification codes."""

    __tablename__ = "otp_codes"

    # ── Columns ────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(15), nullable=False, comment="Target phone number (E.164)"
    )
    code: Mapped[str] = mapped_column(
        String(6), nullable=False, comment="The OTP digits"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Expiration timestamp"
    )
    used: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Whether the OTP has been consumed"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="Creation timestamp"
    )

    # ── Indexes ────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_otp_codes_phone_code", "phone", "code"),
        Index("ix_otp_codes_expires", "expires_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<OTPCode(id={self.id}, phone={self.phone!r}, "
            f"used={self.used}, expires_at={self.expires_at})>"
        )
