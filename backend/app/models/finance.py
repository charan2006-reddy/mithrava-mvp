"""Finance ORM models (Expense and Income).

Tracks farmer expenditures and earnings with proper foreign keys
and relationships for profit/loss analysis.
"""

import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.farmer import Farmer


class Expense(Base):
    """Expense entity for tracking farmer expenditures."""

    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    farmer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    crop_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("crops.id", ondelete="SET NULL"),
        nullable=True,
    )
    receipt_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ──────────────────────────────────────────────────
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="expenses")

    __table_args__ = (
        Index("ix_expenses_farmer_category", "farmer_id", "category"),
        Index("ix_expenses_date", "date"),
    )


class Income(Base):
    """Income entity for tracking farmer earnings from crop sales."""

    __tablename__ = "income"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    farmer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crop_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("crops.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_per_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    buyer_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ──────────────────────────────────────────────────
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="incomes")

    __table_args__ = (
        Index("ix_income_farmer_date", "farmer_id", "date"),
    )
