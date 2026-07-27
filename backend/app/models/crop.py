"""Crop ORM model."""

import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.farmer import Farmer
    from app.models.land import Land


class Crop(Base):
    """Crop entity representing a cultivation entry for a farmer."""

    __tablename__ = "crops"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    farmer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    land_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("lands.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    variety: Mapped[str | None] = mapped_column(String(100), nullable=True)
    area_acres: Mapped[float] = mapped_column(Float, nullable=False)
    planting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="planted")
    soil_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    irrigation_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    seed_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    fertilizer_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    pesticide_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    yield_quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    sale_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="crops")
    land: Mapped[Optional["Land"]] = relationship("Land", back_populates="crops")
