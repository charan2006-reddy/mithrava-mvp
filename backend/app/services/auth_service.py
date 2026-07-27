"""Authentication service handling OTP, registration, and token management.

Orchestrates the full auth flow: OTP generation/verification, farmer
registration, JWT token creation, and refresh token rotation.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.otp import generate_otp, invalidate_otp, verify_otp as core_verify_otp
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_token,
    verify_password,
)
from app.core.sms import get_sms_provider
from app.models.farmer import Farmer
from app.repositories.farmer_repo import FarmerRepository
from app.schemas.auth import RegisterRequest, TokenResponse

logger = logging.getLogger("mithrava.auth")


class AuthService:
    """Service class for authentication-related operations.

    Coordinates between OTP, security, SMS, and farmer repository layers.
    """

    @staticmethod
    async def send_otp(phone: str) -> dict:
        """Generate and send an OTP for the given phone number.

        Generates the OTP, then attempts to deliver it via the configured
        SMS provider (Twilio/MSG91/Console). The OTP code is only included
        in the response for console mode (development).

        Args:
            phone: Phone number to send OTP to.

        Returns:
            Dict with OTP info (code included only in dev/demo mode).

        Raises:
            ValueError: If rate limit is exceeded.
        """
        try:
            code = generate_otp(phone)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

        # Send OTP via configured SMS provider
        sms_provider = get_sms_provider()
        sent = await sms_provider.send_otp(phone, code)

        # Include demo_otp only in console mode (dev/demo)
        from app.core.sms import ConsoleProvider
        is_dev = isinstance(sms_provider, ConsoleProvider)

        return {
            "phone": phone,
            "otp_sent": sent,
            "expires_in": 300,  # 5 minutes
            "demo_otp": code if is_dev else None,  # Only in dev mode
        }

    @staticmethod
    async def verify_otp_and_login(
        db: AsyncSession, phone: str, code: str
    ) -> Optional[TokenResponse]:
        """Verify an OTP and issue JWT tokens if valid.

        If the phone number is not yet registered, returns None
        so the client can proceed to registration.

        Args:
            db: Async database session.
            phone: Phone number.
            code: 6-digit OTP code.

        Returns:
            TokenResponse if login successful, None if phone not registered.
        """
        is_valid = core_verify_otp(phone, code)
        if not is_valid:
            return None

        farmer = await FarmerRepository.get_by_phone(db, phone)
        if farmer is None:
            # Phone is verified but not registered
            invalidate_otp(phone)
            return None

        if not farmer.is_active:
            return None

        # Generate tokens
        token_data = {"sub": farmer.id}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Store hashed refresh token
        farmer.refresh_token_hash = hash_token(refresh_token)
        await db.flush()

        invalidate_otp(phone)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800,
        )

    @staticmethod
    async def register(db: AsyncSession, data: RegisterRequest) -> Farmer:
        """Register a new farmer.

        Checks for duplicate phone numbers before creating.

        Args:
            db: Async database session.
            data: Registration request data.

        Returns:
            The newly created Farmer instance.

        Raises:
            ValueError: If phone number is already registered.
        """
        existing = await FarmerRepository.get_by_phone(db, data.phone)
        if existing is not None:
            raise ValueError("Phone number is already registered")

        farmer_data = data.model_dump()
        farmer = await FarmerRepository.create(db, farmer_data)
        return farmer

    @staticmethod
    async def refresh_token(db: AsyncSession, token: str) -> TokenResponse:
        """Issue a new access token using a valid refresh token.

        Implements refresh token rotation: the old refresh token is
        invalidated and a new pair is issued.

        Args:
            db: Async database session.
            token: The refresh token.

        Returns:
            New TokenResponse with fresh access and refresh tokens.

        Raises:
            ValueError: If the refresh token is invalid or expired.
        """
        token_payload = verify_token(token)

        if token_payload.type != "refresh":
            raise ValueError("Invalid token type: expected refresh token")

        farmer = await FarmerRepository.get_by_id(db, token_payload.sub)
        if farmer is None or not farmer.is_active:
            raise ValueError("Farmer not found or inactive")

        # Verify stored hash matches
        if farmer.refresh_token_hash and farmer.refresh_token_hash != hash_token(token):
            raise ValueError("Refresh token has been revoked")

        # Issue new token pair
        new_token_data = {"sub": farmer.id}
        new_access = create_access_token(new_token_data)
        new_refresh = create_refresh_token(new_token_data)

        # Update stored hash
        farmer.refresh_token_hash = hash_token(new_refresh)
        await db.flush()

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="bearer",
            expires_in=1800,
        )

    @staticmethod
    async def logout(db: AsyncSession, token: str) -> bool:
        """Log out a user by revoking their refresh token.

        Args:
            db: Async database session.
            token: The refresh token to revoke.

        Returns:
            True if logout succeeded.
        """
        try:
            token_payload = verify_token(token)
            farmer = await FarmerRepository.get_by_id(db, token_payload.sub)
            if farmer:
                farmer.refresh_token_hash = None
                await db.flush()
            return True
        except ValueError:
            return False

    @staticmethod
    async def get_current_user(
        db: AsyncSession, access_token: str
    ) -> Optional[Farmer]:
        """Get the current user from an access token.

        Args:
            db: Async database session.
            access_token: JWT access token.

        Returns:
            Farmer instance if valid, None otherwise.
        """
        try:
            token_payload = verify_token(access_token)
            if token_payload.type != "access":
                return None
            farmer = await FarmerRepository.get_by_id(db, token_payload.sub)
            if farmer and farmer.is_active:
                return farmer
        except ValueError:
            pass
        return None
