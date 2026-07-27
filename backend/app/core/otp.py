"""OTP generation and verification service.

Provides time-limited OTP codes with rate limiting for MVP.
Stores OTPs in an in-memory dictionary (replace with Redis in production).
"""

import random
import string
import time
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 300  # 5 minutes
RATE_LIMIT_MAX_REQUESTS = 3
RATE_LIMIT_WINDOW_SECONDS = 600  # 10 minutes


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class OTPRecord:
    """Internal record for a stored OTP."""

    code: str
    created_at: float
    attempts: int = 0
    verified: bool = False


@dataclass
class RateLimitRecord:
    """Tracks OTP request timestamps for rate limiting."""

    timestamps: list[float] = field(default_factory=list)


# ---------------------------------------------------------------------------
# In-memory stores (replace with Redis for production)
# ---------------------------------------------------------------------------

_otp_store: dict[str, OTPRecord] = {}
_rate_limit_store: dict[str, RateLimitRecord] = {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_otp(phone: str) -> str:
    """Generate a 6-digit OTP for the given phone number.

    Applies rate limiting: max 3 requests per phone per 10 minutes.
    OTPs expire after 5 minutes.

    Args:
        phone: The phone number to generate OTP for.

    Returns:
        The generated 6-digit OTP string.

    Raises:
        ValueError: If rate limit is exceeded.
    """
    now = time.time()
    _cleanup_expired()

    # Rate limiting
    rate_key = phone
    if rate_key not in _rate_limit_store:
        _rate_limit_store[rate_key] = RateLimitRecord()

    rate_record = _rate_limit_store[rate_key]
    # Prune timestamps outside the window
    rate_record.timestamps = [
        ts for ts in rate_record.timestamps
        if now - ts < RATE_LIMIT_WINDOW_SECONDS
    ]

    if len(rate_record.timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        raise ValueError(
            f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX_REQUESTS} OTP requests "
            f"per {RATE_LIMIT_WINDOW_SECONDS // 60} minutes."
        )

    # Generate 6-digit numeric OTP
    # In dev/demo mode (console SMS provider), use fixed OTP for easy testing
    from app.core.sms import get_sms_provider, ConsoleProvider
    sms_provider = get_sms_provider()
    if isinstance(sms_provider, ConsoleProvider):
        code = "123456"
    else:
        code = "".join(random.choices(string.digits, k=OTP_LENGTH))

    # Store OTP
    _otp_store[phone] = OTPRecord(code=code, created_at=now)
    rate_record.timestamps.append(now)

    return code


def verify_otp(phone: str, code: str) -> bool:
    """Verify an OTP code for the given phone number.

    Checks the code against the stored OTP, enforcing expiry and
    maximum attempt limits.

    Args:
        phone: The phone number to verify OTP for.
        code: The 6-digit OTP code to verify.

    Returns:
        True if the OTP is valid and not expired, False otherwise.
    """
    _cleanup_expired()

    record = _otp_store.get(phone)
    if record is None:
        return False

    if record.verified:
        return False

    now = time.time()
    if now - record.created_at > OTP_EXPIRY_SECONDS:
        # OTP expired
        _otp_store.pop(phone, None)
        return False

    record.attempts += 1
    if record.attempts > 5:
        # Too many wrong attempts – invalidate
        _otp_store.pop(phone, None)
        return False

    if record.code == code:
        record.verified = True
        return True

    return False


def is_otp_pending(phone: str) -> bool:
    """Check if there is an active (unverified) OTP for the phone.

    Args:
        phone: Phone number to check.

    Returns:
        True if an active OTP exists, False otherwise.
    """
    _cleanup_expired()
    record = _otp_store.get(phone)
    if record is None or record.verified:
        return False
    now = time.time()
    return (now - record.created_at) <= OTP_EXPIRY_SECONDS


def invalidate_otp(phone: str) -> None:
    """Manually invalidate/clear the OTP for a phone number.

    Args:
        phone: Phone number whose OTP should be cleared.
    """
    _otp_store.pop(phone, None)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _cleanup_expired() -> None:
    """Remove all expired OTP records from the store."""
    now = time.time()
    expired_phones = [
        phone
        for phone, record in _otp_store.items()
        if (now - record.created_at) > OTP_EXPIRY_SECONDS
    ]
    for phone in expired_phones:
        _otp_store.pop(phone, None)
