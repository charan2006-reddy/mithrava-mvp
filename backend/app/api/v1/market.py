"""Market price API endpoints.

Provides crop price information, trends, and market data.
Uses realistic base prices derived from actual Indian mandi/mandi data
with deterministic daily fluctuation so prices change each day but are
consistent within a day for the same crop.

Future: Replace with real market API (data.gov.in, Agmarknet).
"""

import hashlib
from datetime import datetime, timedelta
import random
from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter(prefix="/market", tags=["Market Prices"])


# ---------------------------------------------------------------------------
# Mock market data (realistic Indian mandi prices in INR per quintal)
# ---------------------------------------------------------------------------

MOCK_PRICES: dict[str, dict] = {
    "rice": {
        "name": "Rice (Paddy)",
        "unit": "quintal",
        "current_price": 2050,
        "msp": 2040,
        "min_price": 1800,
        "max_price": 2300,
        "mandi": "Hyderabad",
        "updated_at": "2025-07-15T10:00:00",
    },
    "wheat": {
        "name": "Wheat",
        "unit": "quintal",
        "current_price": 2275,
        "msp": 2275,
        "min_price": 2100,
        "max_price": 2500,
        "mandi": "Hyderabad",
        "updated_at": "2025-07-15T10:00:00",
    },
    "cotton": {
        "name": "Cotton",
        "unit": "quintal",
        "current_price": 6620,
        "msp": 6620,
        "min_price": 6000,
        "max_price": 7200,
        "mandi": "Adilabad",
        "updated_at": "2025-07-15T10:00:00",
    },
    "chilli": {
        "name": "Red Chilli",
        "unit": "quintal",
        "current_price": 12000,
        "msp": None,
        "min_price": 10000,
        "max_price": 15000,
        "mandi": "Guntur",
        "updated_at": "2025-07-15T10:00:00",
    },
    "tomato": {
        "name": "Tomato",
        "unit": "quintal",
        "current_price": 2500,
        "msp": None,
        "min_price": 1000,
        "max_price": 5000,
        "mandi": "Kurnool",
        "updated_at": "2025-07-15T10:00:00",
    },
    "groundnut": {
        "name": "Groundnut",
        "unit": "quintal",
        "current_price": 5500,
        "msp": 5550,
        "min_price": 5000,
        "max_price": 6200,
        "mandi": "Anantapur",
        "updated_at": "2025-07-15T10:00:00",
    },
    "soybean": {
        "name": "Soybean",
        "unit": "quintal",
        "current_price": 4600,
        "msp": 4600,
        "min_price": 4200,
        "max_price": 5000,
        "mandi": "Hyderabad",
        "updated_at": "2025-07-15T10:00:00",
    },
    "maize": {
        "name": "Maize (Corn)",
        "unit": "quintal",
        "current_price": 1870,
        "msp": 1870,
        "min_price": 1700,
        "max_price": 2100,
        "mandi": "Warangal",
        "updated_at": "2025-07-15T10:00:00",
    },
    "onion": {
        "name": "Onion",
        "unit": "quintal",
        "current_price": 1800,
        "msp": None,
        "min_price": 800,
        "max_price": 3500,
        "mandi": "Nashik",
        "updated_at": "2025-07-15T10:00:00",
    },
    "potato": {
        "name": "Potato",
        "unit": "quintal",
        "current_price": 1200,
        "msp": None,
        "min_price": 800,
        "max_price": 1800,
        "mandi": "Indore",
        "updated_at": "2025-07-15T10:00:00",
    },
}

# Available markets
ALL_MARKETS = [
    "Hyderabad", "Warangal", "Kurnool", "Adilabad",
    "Guntur", "Anantapur", "Nashik", "Indore",
]


def _daily_seed(crop: str, date_str: str) -> float:
    """Generate a deterministic pseudo-random fluctuation factor for a crop on a given date.

    Uses a hash of crop+date to produce a value between -0.06 and +0.06,
    so prices vary by up to ±6% daily but are consistent within a day.

    Args:
        crop: Crop key (e.g., "rice").
        date_str: Date string in YYYY-MM-DD format.

    Returns:
        Fluctuation multiplier between -0.06 and +0.06.
    """
    h = hashlib.md5(f"{crop}:{date_str}".encode()).hexdigest()
    # Convert first 8 hex chars to a float between 0 and 1
    normalized = int(h[:8], 16) / 0xFFFFFFFF
    # Map to range [-0.06, +0.06]
    return (normalized - 0.5) * 0.12


def _get_fluctuated_price(base_price: int, crop: str, date_str: str) -> int:
    """Apply daily fluctuation to a base price.

    Args:
        base_price: The reference price in INR per quintal.
        crop: Crop key.
        date_str: Date string (YYYY-MM-DD).

    Returns:
        Fluctuated price rounded to nearest 10.
    """
    factor = _daily_seed(crop, date_str)
    fluctuated = base_price * (1 + factor)
    return max(base_price * 0.80, min(base_price * 1.20, round(fluctuated / 10) * 10))


def _generate_trend(crop: str, days: int = 30) -> list[dict]:
    """Generate price trend data for a crop using deterministic daily fluctuation.

    Each day's price is derived from the base price + a per-day hash seed,
    creating a realistic but reproducible trend line.

    Args:
        crop: Crop name key.
        days: Number of days of history.

    Returns:
        List of daily price points.
    """
    base_price = MOCK_PRICES.get(crop, {}).get("current_price", 2000)
    trend: list[dict] = []

    for i in range(days, 0, -1):
        date = datetime.utcnow() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        price = _get_fluctuated_price(base_price, crop, date_str)
        trend.append({
            "date": date_str,
            "price": float(price),
        })

    return trend


def _compute_best_day(trend: list[dict]) -> tuple[str, float, float]:
    """Analyze trend to find best day to sell and compute averages.

    Returns:
        Tuple of (best_day_name, weekly_avg, monthly_avg).
    """
    if not trend:
        return "N/A", 0, 0

    day_prices: dict[str, list[float]] = {}
    for point in trend:
        dt = datetime.strptime(point["date"], "%Y-%m-%d")
        day_name = dt.strftime("%A")
        day_prices.setdefault(day_name, []).append(point["price"])

    best_day = "Wednesday"
    best_avg = 0.0
    for day, prices in day_prices.items():
        avg = sum(prices) / len(prices)
        if avg > best_avg:
            best_avg = avg
            best_day = day

    recent_7 = trend[-7:] if len(trend) >= 7 else trend
    weekly_avg = sum(p["price"] for p in recent_7) / len(recent_7)
    monthly_avg = sum(p["price"] for p in trend) / len(trend)

    return best_day, round(weekly_avg, 0), round(monthly_avg, 0)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/crops")
async def list_available_crops():
    """List all crops with available market price data."""
    crops = [
        {"key": key, "name": data["name"]}
        for key, data in MOCK_PRICES.items()
    ]
    return {
        "success": True,
        "message": "OK",
        "data": crops,
    }


@router.get("/markets")
async def list_available_markets():
    """List all markets with available price data."""
    return {
        "success": True,
        "message": "OK",
        "data": ALL_MARKETS,
    }


@router.get("/prices")
async def list_crop_prices(
    crop: Optional[str] = Query(default=None, description="Filter by crop name"),
):
    """List current prices for all tracked crops, or a specific crop.

    Prices are based on realistic Indian mandi data with daily fluctuation
    so values change each day but remain within historical ranges.

    Args:
        crop: Optional crop key to filter (e.g., "rice", "wheat").
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")

    if crop:
        crop_lower = crop.lower()
        if crop_lower not in MOCK_PRICES:
            return {
                "success": False,
                "message": f"Price data not available for '{crop}'",
                "data": None,
            }
        price_data = MOCK_PRICES[crop_lower].copy()
        # Apply daily fluctuation to current price
        price_data["current_price"] = _get_fluctuated_price(
            price_data["current_price"], crop_lower, today
        )
        price_data["updated_at"] = f"{today}T10:00:00"
        trend = _generate_trend(crop_lower, 30)
        best_day, weekly_avg, monthly_avg = _compute_best_day(trend)

        return {
            "success": True,
            "message": "OK",
            "data": {
                "crops": [price_data],
                "trend": trend,
                "summary": {
                    "best_day_to_sell": best_day,
                    "weekly_avg": weekly_avg,
                    "monthly_avg": monthly_avg,
                },
                "updated_at": price_data["updated_at"],
                "note": "Prices are indicative with daily fluctuation. Actual mandi prices may vary.",
            },
        }

    # Return all crops with today's fluctuated prices
    all_crops = []
    for key, data in MOCK_PRICES.items():
        c = data.copy()
        c["current_price"] = _get_fluctuated_price(data["current_price"], key, today)
        c["updated_at"] = f"{today}T10:00:00"
        all_crops.append(c)

    return {
        "success": True,
        "message": "OK",
        "data": {
            "crops": all_crops,
            "updated_at": f"{today}T10:00:00",
            "note": "Prices are indicative with daily fluctuation. Actual mandi prices may vary.",
        },
    }


@router.get("/trend")
async def get_crop_trend(
    crop: str = Query(..., description="Crop name (e.g., rice, wheat)"),
    market: Optional[str] = Query(default=None, description="Market name"),
    days: int = Query(default=30, ge=7, le=90, description="Number of days"),
):
    """Get price trend data for a crop over time.

    Uses deterministic daily fluctuation based on crop+date hashing,
    so the trend is reproducible and changes each day.

    Args:
        crop: Crop name key.
        market: Optional market filter.
        days: Number of historical days.
    """
    crop_lower = crop.lower()
    trend = _generate_trend(crop_lower, days)
    best_day, weekly_avg, monthly_avg = _compute_best_day(trend)

    return {
        "success": True,
        "message": "OK",
        "data": {
            "crop": crop_lower,
            "market": market or MOCK_PRICES.get(crop_lower, {}).get("mandi", "All"),
            "days": days,
            "trend": trend,
            "summary": {
                "best_day_to_sell": best_day,
                "weekly_avg": weekly_avg,
                "monthly_avg": monthly_avg,
            },
        },
    }
