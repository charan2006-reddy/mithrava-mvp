"""Alembic environment configuration for async SQLAlchemy.

Supports both async (asyncpg) and sync (psycopg2) migration modes.
Dynamically reads DATABASE_URL from environment for portability.
"""

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------

config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import ALL models so Alembic can detect every table for autogenerate.
# ---------------------------------------------------------------------------

from app.database import Base

# Core
from app.models.farmer import Farmer  # noqa: F401
from app.models.crop import Crop  # noqa: F401
from app.models.disease import DiseaseScan  # noqa: F401
from app.models.finance import Expense, Income  # noqa: F401

# Marketplace
from app.models.vendor import Vendor, VendorReview  # noqa: F401

# Community
from app.models.forum import ForumPost, ForumComment, ForumLike  # noqa: F401

# AI Assistant
from app.models.mitra import MitraConversation, MitraMessage  # noqa: F401

# Notifications
from app.models.notification import Notification  # noqa: F401
from app.models.push_subscription import PushSubscription  # noqa: F401
from app.models.device_token import DeviceToken  # noqa: F401

# Knowledge / RAG
from app.models.knowledge import (  # noqa: F401
    KnowledgeCategory,
    KnowledgeArticle,
    KnowledgeChunk,
    KnowledgeDocument,
    DocumentEmbedding,
)

# Support
from app.models.support import SupportCall  # noqa: F401

# Auth / Security
from app.models.otp import OTPCode  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401

# Audit / Compliance
from app.models.audit_log import AuditLog  # noqa: F401

# Land / Market
from app.models.land import Land  # noqa: F401
from app.models.market_price import MarketPrice  # noqa: F401

# Expert Calls
from app.models.expert_call import ExpertCall  # noqa: F401

# Settings
from app.models.settings import FarmerSetting  # noqa: F401

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Database URL resolution
# ---------------------------------------------------------------------------

# Read DATABASE_URL from environment, with a fallback for local dev
ASYNC_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/mithrava",
)

# For Alembic, always use the sync driver
SYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("+asyncpg", "+psycopg2")
# Handle edge case: if someone uses aiosqlite for local dev
SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("+aiosqlite", "")

config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Required for SQLite ALTER TABLE support
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with a synchronous connection.

    Args:
        connection: SQLAlchemy connection.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,  # Required for SQLite ALTER TABLE support
    )
    with context.begin_transaction():
        context.run_migrations()


def run_async_migrations() -> None:
    """Run migrations in async mode using asyncpg driver."""
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(ASYNC_DATABASE_URL)

    async def run_async() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    asyncio.run(run_async())


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and connects to the database.
    """
    run_async_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
