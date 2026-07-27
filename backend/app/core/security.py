"""JWT authentication and password hashing utilities.

Provides token creation, verification, and password hashing
using python-jose for JWT and passlib for password hashing.
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Configuration — read from environment, auto-generate if missing
# ---------------------------------------------------------------------------

def _get_secret_key() -> str:
    """Load SECRET_KEY from environment, or auto-generate and warn.

    Never use a hardcoded secret in production. If the environment variable
    is not set (or still contains the placeholder), a random key is generated
    on startup. This means tokens will be invalidated on restart — which is
    acceptable for dev but signals misconfiguration in production.
    """
    key = os.environ.get("SECRET_KEY", "")
    placeholders = {
        "",
        "change-this-to-a-random-secret-key-in-production",
        "mithrava-secret-change-in-production-use-env-variable",
        "dev-secret-key-change-in-production",
    }
    if key in placeholders:
        import warnings
        warnings.warn(
            "SECRET_KEY is not set or uses a placeholder. "
            "Generating a random key — tokens will NOT persist across restarts. "
            "Set SECRET_KEY in your .env for stable auth.",
            RuntimeWarning,
            stacklevel=2,
        )
        key = secrets.token_urlsafe(64)
    return key


SECRET_KEY = _get_secret_key()
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password: The password in plaintext.
        hashed_password: The stored bcrypt hash.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: The plaintext password.

    Returns:
        The bcrypt hash string.
    """
    return pwd_context.hash(password)


# ---------------------------------------------------------------------------
# JWT Token management
# ---------------------------------------------------------------------------


class TokenPayload(BaseModel):
    """Payload schema for decoded JWT tokens."""

    sub: str  # farmer_id
    exp: datetime
    iat: datetime
    type: str = "access"  # "access" or "refresh"
    jti: str  # unique token identifier


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        data: Claims to encode (must include 'sub' with farmer_id).
        expires_delta: Custom expiry duration. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
            "jti": secrets.token_urlsafe(32),
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a signed JWT refresh token with a longer expiry.

    Args:
        data: Claims to encode (must include 'sub' with farmer_id).

    Returns:
        Encoded JWT refresh token string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32),
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> TokenPayload:
    """Decode and verify a JWT token.

    Args:
        token: The encoded JWT string.

    Returns:
        Decoded TokenPayload.

    Raises:
        ValueError: If the token is invalid, expired, or malformed.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(
            sub=payload["sub"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            type=payload.get("type", "access"),
            jti=payload.get("jti", ""),
        )
        return token_data
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc


# ---------------------------------------------------------------------------
# Refresh token storage helpers (hash for secure storage)
# ---------------------------------------------------------------------------


def hash_token(token: str) -> str:
    """Hash a token using SHA-256 for secure storage.

    Args:
        token: The raw token string.

    Returns:
        Hex-encoded SHA-256 hash.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
