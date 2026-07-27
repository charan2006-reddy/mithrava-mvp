"""Shared test fixtures for Mithrava API integration tests.

Uses an in-memory SQLite database so no PostgreSQL instance is needed.
Provides: async test DB session, httpx AsyncClient, and auth helper.
"""

import os
import asyncio
import sys
from typing import AsyncGenerator
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

# ---------------------------------------------------------------------------
# CRITICAL: Set env vars BEFORE any app imports, and patch create_async_engine
# to strip PostgreSQL-specific kwargs when the URL is SQLite.
# ---------------------------------------------------------------------------

os.environ["SECRET_KEY"] = "test-secret-key-do-not-use-in-production"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ALGORITHM"] = "HS256"

# ---------------------------------------------------------------------------
# Register SQLite-compatible type compilers for PostgreSQL types
# so that create_all() works with SQLite.
# ---------------------------------------------------------------------------

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(Vector, "sqlite")
def compile_vector_sqlite(type_, compiler, **kw):
    return "TEXT"

# Also register at type map level for reflection
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
SQLiteTypeCompiler.visit_JSONB = lambda self, type_, **kw: "JSON"
SQLiteTypeCompiler.visit_Vector = lambda self, type_, **kw: "TEXT"

# Save original and wrap to strip pool params for SQLite
import sqlalchemy.ext.asyncio as _saio

_original_create_async_engine = _saio.create_async_engine


def _test_create_async_engine(url, **kwargs):
    """Intercept engine creation to drop PostgreSQL-only params for SQLite."""
    if "sqlite" in url:
        kwargs.pop("pool_size", None)
        kwargs.pop("max_overflow", None)
        kwargs.pop("pool_pre_ping", None)
    return _original_create_async_engine(url, **kwargs)


# Monkey-patch BEFORE importing any app modules
_saio.create_async_engine = _test_create_async_engine

try:
    from app.database import Base, get_db  # noqa: E402
    from app.main import app  # noqa: E402
    from app.core.security import create_access_token, create_refresh_token  # noqa: E402
finally:
    # Restore original (good hygiene)
    _saio.create_async_engine = _original_create_async_engine


# ---------------------------------------------------------------------------
# Async event loop
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# In-memory SQLite engine & session (for tests)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Create all tables before each test, drop them after."""
    import app.models  # noqa: F401
    import app.models.push_subscription  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh async database session for direct DB assertions."""
    async with test_session_factory() as session:
        yield session


# ---------------------------------------------------------------------------
# Override FastAPI dependency to use test DB
# ---------------------------------------------------------------------------

async def _override_get_db():
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = _override_get_db


# ---------------------------------------------------------------------------
# HTTP client fixture
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an httpx AsyncClient wired to the FastAPI test app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


# ---------------------------------------------------------------------------
# Auth helpers — bypass OTP entirely by creating users directly in the DB
# ---------------------------------------------------------------------------

TEST_PHONE = "+919876543210"
TEST_PHONE_2 = "+919876543211"


async def _create_test_user(client: AsyncClient, name: str, phone: str, email: str = None) -> dict:
    """Create a test user directly in DB and return JWT tokens.

    Bypasses the OTP flow entirely to avoid rate limits.
    """
    import uuid
    from app.core.security import create_access_token, create_refresh_token, hash_password
    from app.models.farmer import Farmer

    farmer_id = str(uuid.uuid4())

    # Create farmer directly in DB
    async with test_session_factory() as session:
        farmer = Farmer(
            id=farmer_id,
            name=name,
            phone=phone,
            email=email,
            city="Hyderabad",
            state="Telangana",
            preferred_language="en",
            is_active=True,
            is_verified=True,
            role="farmer",
        )
        session.add(farmer)
        await session.commit()

    # Generate JWT tokens
    access_token = create_access_token({"sub": farmer_id})
    refresh_token = create_refresh_token({"sub": farmer_id})

    return {
        "farmer": {"id": farmer_id, "name": name, "phone": phone},
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    }


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Register a test user and return the full response data (farmer + tokens)."""
    return await _create_test_user(client, "Test Farmer", TEST_PHONE, "test@mithrava.com")


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, registered_user: dict) -> dict:
    """Return Authorization headers with a valid access token."""
    token = registered_user["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_2(client: AsyncClient) -> dict:
    """Register a second user and return their auth headers."""
    user2 = await _create_test_user(client, "Test Farmer 2", TEST_PHONE_2)
    return {"Authorization": f"Bearer {user2['tokens']['access_token']}"}
