"""Weather API endpoints."""

from typing import Optional

from fastapi import APIRouter, Query

from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current/{city}")
async def get_current_weather(city: str):
    """Get current weather conditions for a city.

    Returns temperature, humidity, wind, and farming-specific alerts.
    """
    weather = await WeatherService.get_current(city)
    return {
        "success": True,
        "message": "OK",
        "data": weather,
    }


@router.get("/forecast/{city}")
async def get_weather_forecast(
    city: str,
    days: int = Query(default=7, ge=1, le=7, description="Forecast days"),
):
    """Get multi-day weather forecast for a city.

    Up to 7 days of forecast data.
    """
    forecast = await WeatherService.get_forecast(city, days)
    return {
        "success": True,
        "message": "OK",
        "data": {
            "city": city,
            "days": days,
            "forecast": forecast,
        },
    }


@router.get("/advice")
async def get_farming_advice(
    city: str = Query(..., description="City name"),
    crop_type: Optional[str] = Query(default=None, description="Crop type for targeted advice"),
):
    """Get weather-based farming advice.

    Combines current weather with crop-specific recommendations.
    """
    result = await WeatherService.get_farming_advice_for_city(city, crop_type)
    return {
        "success": True,
        "message": "OK",
        "data": result,
    }
