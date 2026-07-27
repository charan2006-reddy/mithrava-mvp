"""Crop management API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.farmer import Farmer
from app.schemas.crop import CropCreate, CropUpdate
from app.services.crop_service import CropService
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/crops", tags=["Crops"])


@router.get("/calendar")
async def get_crop_calendar(
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Get the personalised crop calendar for the current farmer.

    Returns stage-based calendar items for all crops belonging to the
    authenticated farmer, along with today's priority actions.
    """
    data = await CropService.get_crop_calendar(db, str(current_user.id))
    return {
        "success": True,
        "message": "OK",
        "data": data,
    }


@router.get("/weather-calendar")
async def get_weather_aware_calendar(
    city: str = Query(..., description="City name for weather data"),
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Get crop calendar adjusted for current weather conditions.

    Combines the farmer's crop calendar with real-time weather forecast
    to provide weather-aware task adjustments:
    - Delay spraying if rain expected
    - Increase irrigation in heat waves
    - Protect crops before storms
    - Adjust harvest timing based on rain forecast
    """
    # Get calendar and weather data in parallel
    calendar_data = await CropService.get_crop_calendar(db, str(current_user.id))
    forecast = await WeatherService.get_forecast(city, 7)
    weather = await WeatherService.get_current(city)

    # Generate weather-aware adjustments
    adjustments = _generate_weather_adjustments(weather, forecast)

    return {
        "success": True,
        "message": "OK",
        "data": {
            "calendar": calendar_data,
            "weather": weather,
            "forecast": forecast[:3],  # Next 3 days
            "adjustments": adjustments,
        },
    }


@router.get("/daily-actions")
async def get_daily_actions(
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Get today's priority actions across all of the farmer's crops.

    Returns actions sorted by priority (high first).
    """
    actions = await CropService.get_daily_actions(db, str(current_user.id))
    return {
        "success": True,
        "message": "OK",
        "data": {
            "actions": actions,
            "total": len(actions),
        },
    }


@router.get("/")
async def list_my_crops(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """List all crops for the current farmer."""
    crops, total = await CropService.list_farmer_crops(
        db, str(current_user.id), skip, limit
    )
    return {
        "success": True,
        "message": "OK",
        "data": {
            "crops": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "variety": c.variety,
                    "area_acres": c.area_acres,
                    "planting_date": c.planting_date.isoformat() if c.planting_date else None,
                    "expected_harvest_date": (
                        c.expected_harvest_date.isoformat() if c.expected_harvest_date else None
                    ),
                    "status": c.status,
                    "total_cost": c.total_cost,
                    "yield_quantity": c.yield_quantity,
                }
                for c in crops
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total,
        },
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_crop(
    body: CropCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Create a new crop record."""
    crop = await CropService.create_crop(db, str(current_user.id), body)
    return {
        "success": True,
        "message": "Crop created successfully",
        "data": {
            "id": str(crop.id),
            "name": crop.name,
            "variety": crop.variety,
            "area_acres": crop.area_acres,
            "planting_date": crop.planting_date.isoformat() if crop.planting_date else None,
            "expected_harvest_date": (
                crop.expected_harvest_date.isoformat() if crop.expected_harvest_date else None
            ),
            "status": crop.status,
            "total_cost": crop.total_cost,
        },
    }


@router.get("/{crop_id}")
async def get_crop(
    crop_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Get full crop details including calendar stage information.

    Returns comprehensive crop data along with the current growth stage,
    days since sowing, and the next recommended action.
    """
    detail = await CropService.get_crop_detail(
        db, crop_id, str(current_user.id)
    )
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found.",
        )
    return {
        "success": True,
        "message": "OK",
        "data": detail.model_dump(mode="json"),
    }


@router.put("/{crop_id}")
async def update_crop(
    crop_id: str,
    body: CropUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Update a crop record."""
    crop = await CropService.get_crop(db, crop_id, str(current_user.id))
    if crop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found.",
        )

    updated = await CropService.update_crop(db, crop_id, body)
    return {
        "success": True,
        "message": "Crop updated successfully",
        "data": {
            "id": str(updated.id),
            "name": updated.name,
            "variety": updated.variety,
            "area_acres": updated.area_acres,
            "status": updated.status,
            "total_cost": updated.total_cost,
        },
    }


@router.delete("/{crop_id}")
async def delete_crop(
    crop_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Delete a crop record."""
    crop = await CropService.get_crop(db, crop_id, str(current_user.id))
    if crop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found.",
        )

    await CropService.delete_crop(db, crop_id)
    return {
        "success": True,
        "message": "Crop deleted successfully",
        "data": None,
    }


# ---------------------------------------------------------------------------
# Weather-aware calendar helpers
# ---------------------------------------------------------------------------


def _generate_weather_adjustments(
    weather: dict, forecast: list[dict]
) -> list[dict]:
    """Generate weather-based task adjustments for the crop calendar.

    Examines current weather and upcoming forecast to produce actionable
    adjustments the farmer should consider for their planned tasks.

    Args:
        weather: Current weather data dict.
        forecast: List of forecast day dicts.

    Returns:
        List of adjustment dicts with type, message, and priority.
    """
    adjustments: list[dict] = []
    temp = weather.get("temperature", 25)
    humidity = weather.get("humidity", 50)
    description = weather.get("description", "").lower()

    # Check for rain in the next 3 days
    rain_days = [
        f for f in forecast[:3]
        if f.get("rain_chance", 0) > 40
        or "rain" in f.get("description", "").lower()
    ]

    # Heat wave adjustments
    if temp > 38:
        adjustments.append({
            "type": "irrigation",
            "icon": "🌡️",
            "priority": "high",
            "message": (
                f"High temperature ({temp}°C). Schedule irrigation early morning "
                "or late evening. Increase water supply by 20-30%."
            ),
            "original_task": "Regular irrigation",
            "adjusted_task": "Extended irrigation — early AM + late PM",
        })
    elif temp > 42:
        adjustments.append({
            "type": "protection",
            "icon": "🔴",
            "priority": "critical",
            "message": (
                f"Heat wave alert ({temp}°C)! Set up shade nets for sensitive crops. "
                "Mist irrigation recommended. Avoid all field work during noon."
            ),
            "original_task": "Regular field activities",
            "adjusted_task": "Emergency shade + mist irrigation",
        })

    # Cold weather adjustments
    if temp < 10:
        adjustments.append({
            "type": "protection",
            "icon": "❄️",
            "priority": "high",
            "message": (
                "Cold weather alert. Cover seedlings with protective sheets. "
                "Avoid irrigation during coldest hours (4-6 AM)."
            ),
            "original_task": "Regular irrigation",
            "adjusted_task": "Delayed irrigation + frost protection",
        })

    # Rain-based adjustments
    if rain_days:
        rain_count = len(rain_days)
        adjustments.append({
            "type": "spraying",
            "icon": "🌧️",
            "priority": "high",
            "message": (
                f"Rain expected in {rain_count} of the next 3 days. "
                "Delay all pesticide and fertilizer applications. "
                "Ensure field drainage channels are clear."
            ),
            "original_task": "Pesticide/fertilizer application",
            "adjusted_task": f"Delay spraying — wait {rain_count + 1} days for dry window",
        })

    # Heavy rain adjustments
    heavy_rain = [
        f for f in forecast[:3]
        if f.get("rain_chance", 0) > 70
        or "heavy" in f.get("description", "").lower()
    ]
    if heavy_rain:
        adjustments.append({
            "type": "drainage",
            "icon": "⛈️",
            "priority": "high",
            "message": (
                "Heavy rain expected. Clear all drainage channels immediately. "
                "Avoid harvesting. Secure stored produce against water damage."
            ),
            "original_task": "Harvesting or field work",
            "adjusted_task": "Clear drainage — postpone harvest",
        })

    # High humidity adjustments
    if humidity > 85:
        adjustments.append({
            "type": "disease",
            "icon": "🦠",
            "priority": "medium",
            "message": (
                f"High humidity ({humidity}%) increases disease risk. "
                "Apply preventive fungicide on susceptible crops. "
                "Improve air circulation by pruning dense foliage."
            ),
            "original_task": "Regular monitoring",
            "adjusted_task": "Preventive fungicide + enhanced monitoring",
        })

    # Wind adjustments
    wind_speed = weather.get("wind_speed", 0)
    if wind_speed > 10:
        adjustments.append({
            "type": "spraying",
            "icon": "💨",
            "priority": "medium",
            "message": (
                f"Strong winds ({wind_speed} m/s). Delay spraying activities — "
                "spray drift reduces effectiveness and may damage nearby crops. "
                "Secure tall crops with stakes."
            ),
            "original_task": "Spraying",
            "adjusted_task": "Delay spraying until wind subsides",
        })

    # Good conditions — positive reinforcement
    if not adjustments and 15 < temp < 35 and 40 < humidity < 80:
        adjustments.append({
            "type": "general",
            "icon": "✅",
            "priority": "low",
            "message": (
                "Weather conditions are favorable! Good time for all planned "
                "activities including spraying, irrigation, and field work."
            ),
            "original_task": "All planned tasks",
            "adjusted_task": "Proceed as planned — ideal conditions",
        })

    return adjustments
