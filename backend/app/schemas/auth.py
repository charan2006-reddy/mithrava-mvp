"""Authentication request/response schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class OTPRequest(BaseModel):
    """Schema for requesting an OTP to be sent to a phone number."""

    phone: str = Field(
        ...,
        min_length=10,
        max_length=15,
        pattern=r"^\+?[0-9\s\-()]+$",
        description="Phone number in international format",
    )

    model_config = {"json_schema_extra": {"examples": [{"phone": "+919876543210"}]}}


class OTPVerify(BaseModel):
    """Schema for verifying an OTP code."""

    phone: str = Field(
        ...,
        min_length=10,
        max_length=15,
        description="Phone number used during OTP request",
    )
    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^[0-9]+$",
        description="6-digit OTP code",
    )


class TokenResponse(BaseModel):
    """Schema for JWT token pair returned after authentication."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token for obtaining new access tokens")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(
        default=1800, description="Access token expiry time in seconds"
    )


class RefreshRequest(BaseModel):
    """Schema for requesting a new access token using a refresh token."""

    refresh_token: str = Field(..., description="Valid refresh token")


class RegisterRequest(BaseModel):
    """Schema for new farmer registration."""

    name: str = Field(
        ..., min_length=2, max_length=100, description="Farmer's full name"
    )
    phone: str = Field(
        ...,
        min_length=10,
        max_length=15,
        pattern=r"^\+?[0-9\s\-()]+$",
        description="Phone number in international format",
    )
    email: Optional[str] = Field(default=None, description="Optional email address")
    city: Optional[str] = Field(default=None, description="City or town")
    state: Optional[str] = Field(default=None, description="State or province")
    preferred_language: str = Field(
        default="en",
        pattern=r"^(en|hi|te|ta|kn|ml|mr|gu|bn|pa)$",
        description="Preferred language code",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Rajesh Kumar",
                    "phone": "+919876543210",
                    "email": "rajesh@example.com",
                    "city": "Hyderabad",
                    "state": "Telangana",
                    "preferred_language": "te",
                }
            ]
        }
    }
