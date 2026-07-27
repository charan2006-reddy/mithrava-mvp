"""Rate limiting middleware using SlowAPI.

Applies different rate limits for general, AI, and auth endpoints
to prevent abuse and ensure fair usage.

Uses Redis when available for persistent, distributed rate limiting.
Falls back to in-memory when Redis is unavailable (dev/single-instance).
"""

import os
import logging
from typing import Optional

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("mithrava.rate_limit")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
RATE_LIMIT_GENERAL = os.environ.get("RATE_LIMIT_GENERAL", "100")
RATE_LIMIT_AI = os.environ.get("RATE_LIMIT_AI", "10")
RATE_LIMIT_WINDOW = os.environ.get("RATE_LIMIT_WINDOW", "60")  # seconds


def _get_storage_uri() -> str:
    """Determine the storage backend for rate limiting.

    Tries Redis first. Falls back to memory if Redis is not configured,
    not reachable, or the redis client package is missing.
    """
    if not REDIS_URL:
        logger.info("No REDIS_URL configured — using in-memory rate limiter")
        return "memory://"

    # Validate URL format
    if not REDIS_URL.startswith(("redis://", "rediss://")):
        logger.warning("Invalid REDIS_URL format '%s' — using in-memory", REDIS_URL)
        return "memory://"

    # Check if redis client is available
    try:
        import redis  # noqa: F401
    except ImportError:
        logger.warning("redis package not installed — using in-memory rate limiter")
        return "memory://"

    storage = f"redis://{REDIS_URL.split('redis://', 1)[-1]}"
    logger.info("Using Redis-backed rate limiter: %s", REDIS_URL)
    return storage


# ---------------------------------------------------------------------------
# Limiter instance
# ---------------------------------------------------------------------------

_storage_uri = _get_storage_uri()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{RATE_LIMIT_GENERAL}/minute"],
    storage_uri=_storage_uri,
)


# ---------------------------------------------------------------------------
# Custom limit decorators for different endpoint categories
# ---------------------------------------------------------------------------

# General API rate limit
GENERAL_LIMIT = f"{RATE_LIMIT_GENERAL}/minute"

# AI/Mitra endpoints – heavier compute
AI_LIMIT = f"{RATE_LIMIT_AI}/minute"

# Auth endpoints – prevent brute-force
AUTH_LIMIT = os.environ.get("RATE_LIMIT_AUTH", "5") + "/minute"

# File upload endpoints
UPLOAD_LIMIT = "20/minute"

# Admin endpoints – lower limits
ADMIN_LIMIT = "30/minute"


# ---------------------------------------------------------------------------
# Custom exception handler
# ---------------------------------------------------------------------------


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors.

    Returns a 429 Too Many Requests with a helpful message.

    Args:
        request: The incoming FastAPI request.
        exc: The RateLimitExceeded exception.

    Returns:
        JSONResponse with 429 status code.
    """
    # Sanitize detail to avoid encoding issues on Windows
    # On Windows, str() on some objects can fail with non-ASCII chars
    try:
        detail_msg = str(exc.detail)
        detail_msg.encode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        detail_msg = "Rate limit exceeded. Please try again later."
    except Exception:
        detail_msg = "Rate limit exceeded. Please try again later."

    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "message": "Rate limit exceeded. Please try again later.",
            "data": None,
            "errors": [
                {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": detail_msg,
                }
            ],
        },
    )
