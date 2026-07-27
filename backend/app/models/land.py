"""
Land Model — Agricultural land parcels owned by farmers.

Each land record represents a distinct physical plot with its area, soil
characteristics, and optional geolocation for map-based features.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.farmer import Farmer
    from app.models.crop import Crop


class Land(Base):
    """Lands table — stores farmer-owned agricultural land parcels."""

    __tablename__ = "lands"

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
        comment="Owner farmer ID",
    )
    name: Mapped[str] = mapped_column(
        String(150), nullable=False, comment="User-defined plot name"
    )
    area_acres: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Land area in acres"
    )
    soil_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="Soil type: clay, sandy, loamy, silty, etc."
    )
    location_lat: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Latitude (WGS-84)"
    )
    location_lng: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Longitude (WGS-84)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="Record creation timestamp"
    )

    # ── Relationships ──────────────────────────────────────────────────
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="lands")
    crops: Mapped[List["Crop"]] = relationship(
        "Crop", back_populates="land", cascade="all, delete-orphan", lazy="selectin"
    )

    # ── Indexes ────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_lands_farmer_name", "farmer_id", "name"),
    )

    def __repr__(self) -> str:
        return (
            f"<Land(id={self.id}, name={self.name!r}, "
            f"area={self.area_acres} acres, farmer_id={self.farmer_id})>"
        )
