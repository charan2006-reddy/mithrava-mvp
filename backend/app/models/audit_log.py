"""
AuditLog Model — Immutable record of data mutations.

Every create, update, or delete on sensitive entities is logged here
for compliance, debugging, and security forensics.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.farmer import Farmer


class AuditLog(Base):
    """Audit logs table — append-only change history."""

    __tablename__ = "audit_logs"

    # ── Columns ────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    farmer_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("farmers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Farmer who performed the action (nullable for system actions)",
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Action verb: create, update, delete, login, etc."
    )
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Target entity type: farmer, crop, expense, etc."
    )
    entity_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, comment="ID of the affected entity"
    )
    old_value: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Entity state before the change"
    )
    new_value: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Entity state after the change"
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True, comment="Client IP address (IPv4 or IPv6)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="Audit event timestamp"
    )

    # ── Relationships ──────────────────────────────────────────────────
    farmer: Mapped[Optional["Farmer"]] = relationship("Farmer", back_populates="audit_logs")

    # ── Indexes ────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_created", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, action={self.action!r}, "
            f"entity={self.entity_type!r}/{self.entity_id})>"
        )
