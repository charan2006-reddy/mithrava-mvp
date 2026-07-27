"""
Market Price Model — Daily crop commodity prices from mandis.

Stores price data scraped from government sources (Agmarknet) or third-party
APIs. Used for the market price dashboard and trend analysis.
"""

import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Float, Date, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MarketPrice(Base):
    """Market prices table — daily commodity prices per market."""

    __tablename__ = "market_prices"

    # ── Columns ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    crop_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Crop commodity name"
    )
    market_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Mandi / market name"
    )
    price_per_kg: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Price per kilogram in INR"
    )
    unit: Mapped[str] = mapped_column(
        String(20), nullable=False, default="kg", comment="Unit of measurement"
    )
    trend: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, comment="Price trend: up, down, stable"
    )
    date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="Price observation date"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="Record creation timestamp"
    )

    # ── Indexes ────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_market_prices_crop_date", "crop_name", "date"),
        Index("ix_market_prices_market", "market_name"),
        Index("ix_market_prices_date", "date"),
    )

    def __repr__(self) -> str:
        return (
            f"<MarketPrice(id={self.id}, crop={self.crop_name!r}, "
            f"market={self.market_name!r}, price={self.price_per_kg}, "
            f"date={self.date})>"
        )
