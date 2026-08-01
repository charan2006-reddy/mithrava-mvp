"""Initial schema — baseline created directly from current SQLAlchemy models.

Revision ID: 127c0115b699
Revises:
Create Date: 2026-08-01 00:13:22.030634

This migration builds the full schema from ``Base.metadata`` so the database
always matches the current models. It replaces the previously stale hand
written migrations (001/002) which were out of sync with the models.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '127c0115b699'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the full schema from the current models."""
    # Enable pgvector extension (required for VECTOR columns)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Import models so Base.metadata is fully populated, then create all tables
    # in dependency order (create_all handles table ordering automatically).
    from app.models import (  # noqa: F401
        farmer,
        crop,
        disease,
        finance,
        vendor,
        forum,
        mitra,
        notification,
        support,
        knowledge,
        push_subscription,
        device_token,
        otp,
        audit_log,
        land,
        market_price,
        expert_call,
        refresh_token,
        settings,
    )
    from app.database import Base

    bind = op.get_bind()
    Base.metadata.create_all(bind)


def downgrade() -> None:
    """Drop all tables in reverse dependency order."""
    from app.database import Base

    bind = op.get_bind()
    Base.metadata.drop_all(bind)
