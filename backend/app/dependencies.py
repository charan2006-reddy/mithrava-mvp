"""FastAPI dependency injection functions.

Provides reusable dependencies for authentication, authorization,
and database session management.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.database import get_db
from app.models.farmer import Farmer
from app.repositories.farmer_repo import FarmerRepository

# ---------------------------------------------------------------------------
# Security scheme
# ---------------------------------------------------------------------------

bearer_scheme = HTTPBearer(
    auto_error=False,
    description="JWT Bearer token for authentication",
)


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Farmer:
    """Extract and validate the current user from the JWT access token.

    Decodes the token, verifies it, and fetches the farmer from the database.

    Args:
        credentials: Bearer token from the Authorization header.
        db: Async database session.

    Returns:
        The authenticated Farmer instance.

    Raises:
        HTTPException 401: If token is missing, invalid, or user not found.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = verify_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Access token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    farmer = await FarmerRepository.get_by_id(db, payload.sub)
    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not farmer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Please contact support.",
        )

    return farmer


async def get_current_admin(
    current_user: Farmer = Depends(get_current_user),
) -> Farmer:
    """Verify that the current user has admin privileges.

    Args:
        current_user: The authenticated farmer from get_current_user.

    Returns:
        The Farmer instance if they are an admin.

    Raises:
        HTTPException 403: If the user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this operation.",
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[Farmer]:
    """Optionally extract the current user. Returns None if not authenticated.

    Useful for endpoints that behave differently for authenticated vs
    anonymous users.

    Args:
        credentials: Optional bearer token.
        db: Async database session.

    Returns:
        Farmer instance if authenticated, None otherwise.
    """
    if credentials is None:
        return None

    try:
        payload = verify_token(credentials.credentials)
        if payload.type != "access":
            return None
        farmer = await FarmerRepository.get_by_id(db, payload.sub)
        if farmer and farmer.is_active:
            return farmer
    except ValueError:
        pass

    return None
