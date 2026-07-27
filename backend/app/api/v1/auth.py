"""Auth API endpoints.

Handles OTP-based authentication, registration, login, token refresh,
and current user retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.farmer import Farmer
from app.repositories.farmer_repo import FarmerRepository
from app.schemas.auth import (
    OTPRequest,
    OTPVerify,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService
from app.core.security import hash_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/send-otp")
async def send_otp(body: OTPRequest):
    """Send an OTP to the given phone number.

    For MVP, the OTP is returned in the response. In production,
    it would be sent via SMS/WhatsApp.
    """
    try:
        result = await AuthService.send_otp(body.phone)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        )
    return {
        "success": True,
        "message": "OTP sent successfully",
        "data": result,
    }


@router.post("/verify-otp")
async def verify_otp(body: OTPVerify, db: AsyncSession = Depends(get_db)):
    """Verify an OTP code and log in (or redirect to registration).

    Returns JWT tokens if the phone is already registered.
    Returns a flag indicating registration is needed otherwise.
    """
    result = await AuthService.verify_otp_and_login(db, body.phone, body.code)

    if result is None:
        # Check if phone exists to differentiate between "wrong OTP" and "needs registration"
        from app.repositories.farmer_repo import FarmerRepository

        farmer = await FarmerRepository.get_by_phone(db, body.phone)
        if farmer is None:
            return {
                "success": True,
                "message": "Phone verified. Please complete registration.",
                "data": {
                    "needs_registration": True,
                    "phone": body.phone,
                },
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired OTP code.",
            )

    return {
        "success": True,
        "message": "Login successful",
        "data": result.model_dump(),
    }


@router.post("/register")
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new farmer account.

    If the phone number is already registered, auto-login the user
    instead of returning an error.
    """
    try:
        result = await AuthService.register(db, body)
    except ValueError as exc:
        # If the error is "phone already registered", auto-login instead
        if "already registered" in str(exc).lower():
            existing = await FarmerRepository.get_by_phone(db, body.phone)
            if existing is not None:
                from app.core.security import create_access_token, create_refresh_token

                farmer_id = str(existing.id)
                access_token = create_access_token({"sub": farmer_id})
                refresh_token = create_refresh_token({"sub": farmer_id})

                # Store hashed refresh token
                existing.refresh_token_hash = hash_token(refresh_token)
                await db.flush()

                return {
                    "success": True,
                    "message": "Phone already registered. Logged in successfully.",
                    "data": {
                        "farmer": {
                            "id": farmer_id,
                            "name": existing.name,
                            "phone": existing.phone,
                            "email": existing.email,
                            "city": existing.city,
                            "state": existing.state,
                            "preferred_language": existing.preferred_language,
                        },
                        "tokens": {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "token_type": "bearer",
                            "expires_in": 1800,
                        },
                    },
                }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    # Auto-login after registration
    tokens = TokenResponse(
        access_token="",
        refresh_token="",
        token_type="bearer",
        expires_in=1800,
    )

    from app.core.security import create_access_token, create_refresh_token

    farmer_id = str(result.id)
    tokens.access_token = create_access_token({"sub": farmer_id})
    tokens.refresh_token = create_refresh_token({"sub": farmer_id})

    return {
        "success": True,
        "message": "Registration successful",
        "data": {
            "farmer": {
                "id": farmer_id,
                "name": result.name,
                "phone": result.phone,
                "email": result.email,
                "city": result.city,
                "state": result.state,
                "preferred_language": result.preferred_language,
            },
            "tokens": tokens.model_dump(),
        },
    }


@router.post("/login")
async def login(body: OTPVerify, db: AsyncSession = Depends(get_db)):
    """Login with phone and OTP (convenience endpoint for verify-otp flow)."""
    result = await AuthService.verify_otp_and_login(db, body.phone, body.code)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or OTP expired.",
        )
    return {
        "success": True,
        "message": "Login successful",
        "data": result.model_dump(),
    }


@router.post("/refresh")
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Get a new access token using a valid refresh token.

    Implements refresh token rotation — the old refresh token is
    invalidated after use.
    """
    try:
        result = await AuthService.refresh_token(db, body.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )
    return {
        "success": True,
        "message": "Token refreshed successfully",
        "data": result.model_dump(),
    }


@router.post("/logout")
async def logout(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Log out by revoking the refresh token."""
    await AuthService.logout(db, body.refresh_token)
    return {
        "success": True,
        "message": "Logged out successfully",
        "data": None,
    }


@router.get("/me")
async def get_me(current_user: Farmer = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return {
        "success": True,
        "message": "OK",
        "data": {
            "id": str(current_user.id),
            "name": current_user.name,
            "phone": current_user.phone,
            "email": current_user.email,
            "city": current_user.city,
            "state": current_user.state,
            "preferred_language": current_user.preferred_language,
            "farm_size_acres": current_user.farm_size_acres,
            "soil_type": current_user.soil_type,
            "irrigation_type": current_user.irrigation_type,
            "profile_image_url": current_user.profile_image_url,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
    }
