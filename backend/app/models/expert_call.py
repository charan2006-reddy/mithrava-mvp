"""
Expert Call Model — Request a callback from an agricultural expert.

Farmers submit a request with their question; the platform tracks the
status as it moves through pending → contacted → resolved.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.farmer import Farmer


class ExpertCall(Base):
    """Expert calls table — tracks expert callback requests."""

    __tablename__ = "expert_calls"

    # ── Columns ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    farmer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("farmers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Farmer making the request (nullable for guest)",
    )
    name: Mapped[str] = mapped_column(
        String(150), nullable=False, comment="Caller's display name"
    )
    phone: Mapped[str] = mapped_column(
        String(15), nullable=False, comment="Contact phone number (E.164)"
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Caller's city"
    )
    message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Question or issue description"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="Request status: pending, contacted, resolved",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="Request timestamp"
    )

    # ── Relationships ──────────────────────────────────────────────────
    farmer: Mapped[Optional["Farmer"]] = relationship("Farmer", back_populates="expert_calls")

    # ── Indexes ────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_expert_calls_status", "status"),
        Index("ix_expert_calls_created", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<ExpertCall(id={self.id}, name={self.name!r}, "
            f"status={self.status!r}, phone={self.phone!r})>"
        )
