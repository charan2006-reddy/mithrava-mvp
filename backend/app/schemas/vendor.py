"""Vendor-related schemas for marketplace."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VendorBase(BaseModel):
    """Base vendor schema with shared fields."""

    name: str = Field(..., min_length=2, max_length=200, description="Vendor or shop name")
    vendor_type: str = Field(
        ...,
        pattern=r"^(seed_shop|fertilizer_shop|equipment_rental|transport|mandi|processor|other)$",
        description="Type of vendor",
    )
    phone: str = Field(..., min_length=10, max_length=15)
    email: Optional[str] = Field(default=None)
    city: str = Field(..., max_length=100, description="City or town")
    state: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=500)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    description: Optional[str] = Field(default=None, max_length=1000)
    services: Optional[list[str]] = Field(
        default=None, description="List of services offered"
    )
    operating_hours: Optional[str] = Field(
        default=None, max_length=200, description="e.g. Mon-Sat 9AM-6PM"
    )


class VendorCreate(VendorBase):
    """Schema for creating a new vendor."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Agri Seeds Hub",
                    "vendor_type": "seed_shop",
                    "phone": "+919876543211",
                    "city": "Hyderabad",
                    "state": "Telangana",
                    "address": "123 Agricultural Market Road",
                    "description": "Premium seeds for all crop varieties",
                    "operating_hours": "Mon-Sat 9AM-6PM",
                }
            ]
        }
    }


class VendorResponse(VendorBase):
    """Schema for vendor data in API responses."""

    id: str
    rating: float = Field(default=0.0, ge=0, le=5)
    review_count: int = Field(default=0)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VendorReviewCreate(BaseModel):
    """Schema for creating a vendor review."""

    rating: float = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(default=None, max_length=1000)

    model_config = {
        "json_schema_extra": {"examples": [{"rating": 4.5, "comment": "Good quality seeds"}]}
    }


class VendorReviewResponse(BaseModel):
    """Schema for a vendor review in API responses."""

    id: str
    vendor_id: str
    farmer_id: str
    farmer_name: str
    rating: float
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
