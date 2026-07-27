"""Weather service wrapping the core weather module.

Adds caching, alert generation, and farming advice integration.
"""

from typing import Optional

from app.core.weather import (
    generate_weather_alerts,
    get_current_weather,
    get_farming_advice,
    get_forecast,
)


class WeatherService:
    """Service class for weather data and farming weather advice."""

    @staticmethod
    async def get_current(city: str) -> dict:
        """Get current weather for a city.

        Args:
            city: City name.

        Returns:
            Current weather data dict.
        """
        weather = await get_current_weather(city)
        alerts = generate_weather_alerts(weather)
        weather["alerts"] = alerts
        return weather

    @staticmethod
    async def get_forecast(city: str, days: int = 7) -> list[dict]:
        """Get multi-day weather forecast for a city.

        Args:
            city: City name.
            days: Number of days (max 7).

        Returns:
            List of daily forecast dicts.
        """
        return await get_forecast(city, days)

    @staticmethod
    async def get_farming_advice_for_city(
        city: str, crop_type: Optional[str] = None
    ) -> dict:
        """Get weather-based farming advice for a city.

        Args:
            city: City name.
            crop_type: Optional crop type for targeted advice.

        Returns:
            Dict with weather data, advice, and alerts.
        """
        weather = await get_current_weather(city)
        advice = get_farming_advice(weather, crop_type)
        alerts = generate_weather_alerts(weather)

        return {
            "city": city,
            "weather": weather,
            "advice": advice,
            "alerts": alerts,
        }
