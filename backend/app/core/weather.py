"""Weather service using OpenWeatherMap API.

Provides current weather, forecasts, and farming-specific advice
based on weather conditions and crop type.
"""

import os
from datetime import datetime
from typing import Optional

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "") or os.getenv("OPENWEATHERMAP_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


# ---------------------------------------------------------------------------
# Weather data fetching
# ---------------------------------------------------------------------------


async def get_current_weather(city: str) -> dict:
    """Fetch current weather data for a city from OpenWeatherMap.

    Args:
        city: City name (e.g., "Hyderabad", "Telangana").

    Returns:
        Dict with weather data including temperature, humidity, wind, etc.
    """
    if not OPENWEATHER_API_KEY:
        # Return mock data for development
        return _mock_current_weather(city)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{OPENWEATHER_BASE_URL}/weather",
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
            },
        )
        response.raise_for_status()
        data = response.json()

        return {
            "city": data.get("name", city),
            "country": data.get("sys", {}).get("country", ""),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"].get("deg", 0),
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "clouds": data.get("clouds", {}).get("all", 0),
            "visibility": data.get("visibility", 10000),
            "sunrise": datetime.fromtimestamp(
                data["sys"]["sunrise"]
            ).isoformat(),
            "sunset": datetime.fromtimestamp(
                data["sys"]["sunset"]
            ).isoformat(),
            "timestamp": datetime.utcnow().isoformat(),
        }


async def get_forecast(city: str, days: int = 7) -> list[dict]:
    """Fetch multi-day weather forecast for a city.

    Args:
        city: City name.
        days: Number of forecast days (max 7 on free tier).

    Returns:
        List of daily forecast dicts.
    """
    if not OPENWEATHER_API_KEY:
        return _mock_forecast(city, days)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{OPENWEATHER_BASE_URL}/forecast",
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "cnt": min(days * 8, 40),  # 3-hour intervals
            },
        )
        response.raise_for_status()
        data = response.json()

        forecasts: list[dict] = []
        seen_dates: set[str] = set()

        for item in data.get("list", []):
            dt = datetime.fromtimestamp(item["dt"])
            date_str = dt.strftime("%Y-%m-%d")
            if date_str not in seen_dates and len(forecasts) < days:
                seen_dates.add(date_str)
                forecasts.append({
                    "date": date_str,
                    "temperature_min": item["main"]["temp_min"],
                    "temperature_max": item["main"]["temp_max"],
                    "humidity": item["main"]["humidity"],
                    "description": item["weather"][0]["description"],
                    "icon": item["weather"][0]["icon"],
                    "rain_chance": item.get("pop", 0) * 100,
                    "wind_speed": item["wind"]["speed"],
                })

        return forecasts


# ---------------------------------------------------------------------------
# Farming advice
# ---------------------------------------------------------------------------


def get_farming_advice(weather_data: dict, crop_type: Optional[str] = None) -> str:
    """Generate farming advice based on current weather conditions.

    Args:
        weather_data: Current weather data dict.
        crop_type: Optional crop type for targeted advice.

    Returns:
        Farming advice string.
    """
    temp = weather_data.get("temperature", 25)
    humidity = weather_data.get("humidity", 50)
    wind_speed = weather_data.get("wind_speed", 0)
    description = weather_data.get("description", "").lower()

    advice_parts: list[str] = []

    # Temperature-based advice
    if temp > 40:
        advice_parts.append(
            "Extreme heat alert! Irrigate crops early morning and late evening. "
            "Use mulching to retain soil moisture."
        )
    elif temp > 35:
        advice_parts.append(
            "High temperature. Ensure adequate irrigation. Consider shade nets "
            "for sensitive crops."
        )
    elif temp < 10:
        advice_parts.append(
            "Cold weather. Protect seedlings with covers. Avoid irrigation during "
            "coldest hours."
        )

    # Humidity-based advice
    if humidity > 85:
        advice_parts.append(
            "High humidity increases disease risk. Monitor crops for fungal "
            "infections. Ensure proper drainage."
        )
    elif humidity < 30:
        advice_parts.append(
            "Low humidity detected. Increase irrigation frequency. Consider "
            "mulching to conserve moisture."
        )

    # Rain-related advice
    if "rain" in description or "drizzle" in description:
        advice_parts.append(
            "Rain expected. Delay any planned pesticide/fertilizer application. "
            "Ensure field drainage is clear."
        )

    # Wind advice
    if wind_speed > 10:
        advice_parts.append(
            "Strong winds. Secure tall crops with stakes. Check that drip "
            "irrigation lines are properly anchored."
        )

    # Crop-specific advice
    if crop_type:
        crop_lower = crop_type.lower()
        if crop_lower in ("rice", "paddy"):
            advice_parts.append(
                "For rice: maintain 2-5cm standing water in the field. "
                "Monitor for blast disease in high humidity."
            )
        elif crop_lower in ("tomato", "chilli"):
            advice_parts.append(
                "For tomatoes/chilli: watch for early blight in humid conditions. "
                "Stake plants to improve air circulation."
            )
        elif crop_lower in ("cotton",):
            advice_parts.append(
                "For cotton: monitor for bollworm. Ensure good drainage to "
                "prevent root rot in wet conditions."
            )

    if not advice_parts:
        advice_parts.append(
            "Weather conditions look favorable for farming. Continue regular "
            "crop monitoring and maintenance."
        )

    return " ".join(advice_parts)


def generate_weather_alerts(weather_data: dict) -> list[str]:
    """Generate farming-relevant weather alerts.

    Args:
        weather_data: Current weather data dict.

    Returns:
        List of alert strings.
    """
    alerts: list[str] = []
    temp = weather_data.get("temperature", 25)
    humidity = weather_data.get("humidity", 50)
    wind_speed = weather_data.get("wind_speed", 0)
    description = weather_data.get("description", "").lower()

    if temp > 42:
        alerts.append("🔴 HEAT WAVE: Extreme temperature above 42°C. Take immediate irrigation measures.")
    elif temp > 38:
        alerts.append("🟡 HIGH TEMPERATURE: Temperature above 38°C. Increase irrigation and use mulching.")

    if temp < 5:
        alerts.append("🔴 FROST WARNING: Near-freezing temperatures. Protect all sensitive crops.")

    if humidity > 90:
        alerts.append("🟡 HIGH HUMIDITY: Risk of fungal diseases. Apply preventive fungicide if needed.")

    if "thunderstorm" in description or "storm" in description:
        alerts.append("🔴 STORM ALERT: Thunderstorm expected. Secure loose structures and delay spraying.")

    if "heavy rain" in description:
        alerts.append("🟡 HEAVY RAIN: Ensure proper field drainage to prevent waterlogging.")

    if wind_speed > 15:
        alerts.append("🟡 STRONG WINDS: Secure tall crops and check irrigation equipment.")

    return alerts


# ---------------------------------------------------------------------------
# Mock data for development
# ---------------------------------------------------------------------------


def _mock_current_weather(city: str) -> dict:
    """Return mock weather data for development/testing."""
    return {
        "city": city,
        "country": "IN",
        "temperature": 32.5,
        "feels_like": 35.0,
        "humidity": 65,
        "pressure": 1012,
        "wind_speed": 4.2,
        "wind_direction": 180,
        "description": "partly cloudy",
        "icon": "02d",
        "clouds": 40,
        "visibility": 10000,
        "sunrise": "2025-07-15T05:45:00",
        "sunset": "2025-07-15T18:30:00",
        "timestamp": datetime.utcnow().isoformat(),
    }


def _mock_forecast(city: str, days: int) -> list[dict]:
    """Return mock forecast data for development/testing."""
    from datetime import timedelta

    today = datetime.utcnow()
    forecasts: list[dict] = []
    for i in range(days):
        date = today + timedelta(days=i)
        forecasts.append({
            "date": date.strftime("%Y-%m-%d"),
            "temperature_min": 24.0 + (i % 3),
            "temperature_max": 33.0 + (i % 3),
            "humidity": 60 + (i * 2),
            "description": ["partly cloudy", "clear sky", "light rain", "haze"][i % 4],
            "icon": "02d",
            "rain_chance": 20 if i % 3 == 2 else 5,
            "wind_speed": 3.5 + i,
        })
    return forecasts
