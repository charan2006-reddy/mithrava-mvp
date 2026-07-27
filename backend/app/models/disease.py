"""Disease scan ORM model.

Stores the result of AI-powered crop disease analysis including
treatment recommendations, severity levels, and follow-up data.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DiseaseScan(Base):
    """Disease scan entity storing AI-based crop disease analysis results.

    Each record represents a single image analysis performed by the
    OpenAI Vision model, including the diagnosis, treatment plan, and
    metadata about the analysis pipeline version.
    """

    __tablename__ = "disease_scans"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    farmer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    crop_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # ── Diagnosis fields ────────────────────────────────────────────────
    disease_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_healthy: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Legacy treatment (kept for backward compatibility) ──────────────
    treatment: Mapped[str | None] = mapped_column(Text, nullable=True)
    alternative_diagnoses: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── Structured treatment data ───────────────────────────────────────
    treatment_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Structured treatment plan: {organic, chemical, prevention, urgency}",
    )
    prevention_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Prevention tips as JSON array",
    )

    # ── Analysis metadata ───────────────────────────────────────────────
    model_version: Mapped[str] = mapped_column(
        String(50), default="gpt-4o-v1",
        comment="Version of the analysis model/prompt used",
    )
    analyzed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Timestamp when AI analysis was completed",
    )

    # ── Timestamps ──────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
