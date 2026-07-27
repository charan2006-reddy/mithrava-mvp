"""Database configuration and session management.

Provides async SQLAlchemy engine and session factory.
Supports both PostgreSQL (production) and SQLite (development/demo).
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# ---------------------------------------------------------------------------
# SQLite compatibility — register type compilers for PostgreSQL-specific types
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/mithrava",
)

if "sqlite" in DATABASE_URL.lower():
    from sqlalchemy.ext.compiler import compiles
    from sqlalchemy.dialects.postgresql import JSONB, UUID

    @compiles(JSONB, "sqlite")
    def _compile_jsonb_sqlite(type_, compiler, **kw):
        return "JSON"

    @compiles(UUID, "sqlite")
    def _compile_uuid_sqlite(type_, compiler, **kw):
        return "VARCHAR(36)"

    try:
        from pgvector.sqlalchemy import Vector

        @compiles(Vector, "sqlite")
        def _compile_vector_sqlite(type_, compiler, **kw):
            return "TEXT"
    except ImportError:
        pass

# For Alembic sync operations
if "sqlite" in DATABASE_URL.lower():
    SYNC_DATABASE_URL = DATABASE_URL.replace("+aiosqlite", "")
else:
    SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "+psycopg2")

# ---------------------------------------------------------------------------
# Engine & Session
# ---------------------------------------------------------------------------

_engine_kwargs = {
    "echo": False,
}

# Only use pool settings for PostgreSQL (not supported by SQLite)
if DATABASE_URL.startswith("postgresql"):
    _engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,
    })

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Base model
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


# ---------------------------------------------------------------------------
# Database lifecycle
# ---------------------------------------------------------------------------


async def init_db() -> None:
    """Initialize the database by creating all tables.

    For production, use Alembic migrations instead of create_all.
    Imports every model module so Base.metadata knows about all tables.
    """
    async with engine.begin() as conn:
        # Import ALL model modules so Base.metadata discovers every table
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
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close the database engine and all connections."""
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    Automatically commits on success and rolls back on exception.

    Yields:
        AsyncSession instance.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
