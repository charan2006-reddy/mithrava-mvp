"""
Refresh Token Model — Persistent session tokens for JWT refresh flow.

Stores hashed refresh tokens so they can be revoked server-side (e.g.,
on logout, password change, or suspected compromise).
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.farmer import Farmer


class RefreshToken(Base):
    """Refresh tokens table — server-side refresh token storage."""

    __tablename__ = "refresh_tokens"

    # ── Columns ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    farmer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Token owner farmer ID",
    )
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="SHA-256 hash of the refresh token (never store raw tokens)",
    )
    device_info: Mapped[str] = mapped_column(
        String(500), nullable=False, default="unknown", comment="User-agent / device description"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Token expiration timestamp"
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Whether the token has been revoked"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="Token issuance timestamp"
    )

    # ── Relationships ──────────────────────────────────────────────────
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="refresh_tokens")

    # ── Indexes ────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_refresh_tokens_farmer_active", "farmer_id", "revoked"),
    )

    def __repr__(self) -> str:
        return (
            f"<RefreshToken(id={self.id}, farmer_id={self.farmer_id}, "
            f"revoked={self.revoked}, expires_at={self.expires_at})>"
        )
