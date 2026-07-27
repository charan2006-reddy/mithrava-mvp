"""Crop-related schemas for CRUD operations and API responses."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class CropBase(BaseModel):
    """Base crop schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Crop name")
    variety: Optional[str] = Field(default=None, max_length=100, description="Crop variety")
    area_acres: float = Field(..., gt=0, description="Area under cultivation in acres")
    planting_date: Optional[date] = Field(default=None, description="Date of planting")
    expected_harvest_date: Optional[date] = Field(
        default=None, description="Expected harvest date"
    )
    soil_type: Optional[str] = Field(default=None, max_length=50)
    irrigation_type: Optional[str] = Field(default=None, max_length=50)
    seed_cost: Optional[float] = Field(default=None, ge=0, description="Cost of seeds")
    fertilizer_cost: Optional[float] = Field(default=None, ge=0)
    pesticide_cost: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=1000)


class CropCreate(CropBase):
    """Schema for creating a new crop entry."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Rice",
                    "variety": "Sona Masoori",
                    "area_acres": 2.5,
                    "planting_date": "2025-06-15",
                    "expected_harvest_date": "2025-10-15",
                    "soil_type": "clay",
                    "irrigation_type": "flood",
                    "seed_cost": 2500.0,
                    "fertilizer_cost": 5000.0,
                    "pesticide_cost": 1500.0,
                }
            ]
        }
    }


class CropUpdate(BaseModel):
    """Schema for updating a crop (all fields optional)."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    variety: Optional[str] = Field(default=None, max_length=100)
    area_acres: Optional[float] = Field(default=None, gt=0)
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    status: Optional[str] = Field(
        default=None,
        pattern=r"^(planted|growing|harvested|failed)$",
    )
    soil_type: Optional[str] = Field(default=None, max_length=50)
    irrigation_type: Optional[str] = Field(default=None, max_length=50)
    seed_cost: Optional[float] = Field(default=None, ge=0)
    fertilizer_cost: Optional[float] = Field(default=None, ge=0)
    pesticide_cost: Optional[float] = Field(default=None, ge=0)
    yield_quantity: Optional[float] = Field(default=None, ge=0, description="Yield in kg")
    sale_price: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=1000)


class CropResponse(CropBase):
    """Schema for crop data in API responses."""

    id: str
    farmer_id: str
    status: str = Field(default="planted")
    actual_harvest_date: Optional[date] = None
    yield_quantity: Optional[float] = None
    sale_price: Optional[float] = None
    total_cost: Optional[float] = Field(
        default=None, description="Calculated total cost"
    )
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Calendar & Daily Action schemas
# ---------------------------------------------------------------------------


class DailyAction(BaseModel):
    """A single priority action for today based on crop calendar."""

    crop_id: str = Field(..., description="Associated crop ID")
    crop_name: str = Field(..., description="Name of the crop")
    action: str = Field(..., description="Action to perform today")
    priority: str = Field(
        ...,
        pattern=r"^(high|medium|low)$",
        description="Priority level: high, medium, or low",
    )
    icon: str = Field(default="🌱", description="Icon hint for the frontend")
    category: str = Field(
        ...,
        description="Action category: irrigation, fertilizer, pest, harvest, preparation",
    )


class CropCalendarItem(BaseModel):
    """A single crop entry in the personalized calendar response."""

    crop_id: str = Field(..., description="Unique crop ID")
    crop_name: str = Field(..., description="Crop name")
    stage: str = Field(..., description="Current growth stage name")
    week_number: int = Field(..., ge=0, description="Current week number since sowing")
    tasks: list[str] = Field(default_factory=list, description="Stage-specific tasks")
    advice: str = Field(default="", description="Simple-language farming advice")
    priority: str = Field(
        ...,
        pattern=r"^(high|medium|low)$",
        description="Priority level for this stage",
    )


class CropCalendarResponse(BaseModel):
    """Full personalized crop calendar response."""

    crops: list[CropCalendarItem] = Field(
        default_factory=list, description="Calendar items for all farmer crops"
    )
    daily_actions: list[DailyAction] = Field(
        default_factory=list, description="Today's priority actions"
    )


# ---------------------------------------------------------------------------
# Crop detail with calendar stage
# ---------------------------------------------------------------------------


class CropDetailResponse(CropResponse):
    """Extended crop response with calendar stage information."""

    current_stage: Optional[str] = Field(
        default=None, description="Current growth stage name"
    )
    days_since_sowing: Optional[int] = Field(
        default=None, ge=0, description="Days elapsed since planting date"
    )
    week_number: Optional[int] = Field(
        default=None, ge=0, description="Current week number since sowing"
    )
    next_action: Optional[str] = Field(
        default=None, description="Next recommended action"
    )
