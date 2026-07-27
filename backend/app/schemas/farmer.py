"""Farmer-related schemas for CRUD operations and API responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FarmerBase(BaseModel):
    """Base farmer schema with shared fields."""

    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    email: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    preferred_language: str = Field(default="en")
    farm_size_acres: Optional[float] = Field(default=None, ge=0)
    soil_type: Optional[str] = Field(default=None, max_length=50)
    irrigation_type: Optional[str] = Field(default=None, max_length=50)


class FarmerCreate(FarmerBase):
    """Schema for creating a new farmer."""

    password: Optional[str] = Field(default=None, min_length=6)

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
                    "farm_size_acres": 5.0,
                    "soil_type": "red",
                    "irrigation_type": "drip",
                }
            ]
        }
    }


class FarmerUpdate(BaseModel):
    """Schema for updating farmer profile (all fields optional)."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    preferred_language: Optional[str] = Field(default=None)
    farm_size_acres: Optional[float] = Field(default=None, ge=0)
    soil_type: Optional[str] = Field(default=None, max_length=50)
    irrigation_type: Optional[str] = Field(default=None, max_length=50)
    profile_image_url: Optional[str] = Field(default=None)


class FarmerResponse(FarmerBase):
    """Schema for farmer data in API responses."""

    id: str = Field(..., description="Unique farmer ID")
    profile_image_url: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    role: str = Field(default="farmer")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FarmerListResponse(BaseModel):
    """Paginated list of farmers."""

    farmers: list[FarmerResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


# ---------------------------------------------------------------------------
# Profile update (subset of fields)
# ---------------------------------------------------------------------------


class FarmerProfileUpdate(BaseModel):
    """Schema for updating a farmer's profile from the mobile app.

    Only a limited subset of fields are editable by the farmer themselves.
    """

    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    preferred_language: Optional[str] = Field(default=None, max_length=5)


# ---------------------------------------------------------------------------
# Farmer dashboard statistics
# ---------------------------------------------------------------------------


class FarmerStats(BaseModel):
    """Aggregated statistics for the farmer dashboard."""

    total_crops: int = Field(default=0, description="Total crops ever added")
    active_crops: int = Field(default=0, description="Currently growing crops")
    total_land_acres: float = Field(
        default=0.0, ge=0, description="Total cultivated land in acres"
    )
    total_expenses: float = Field(
        default=0.0, ge=0, description="Total expenses in INR"
    )
    total_income: float = Field(
        default=0.0, ge=0, description="Total income in INR"
    )
    profit: float = Field(
        default=0.0, description="Net profit (income - expenses) in INR"
    )
    upcoming_harvests: int = Field(
        default=0,
        description="Number of crops expected to be harvested in the next 30 days",
    )
