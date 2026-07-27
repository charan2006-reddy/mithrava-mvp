"""Crop service layer.

Provides business logic for crop management and crop calendar generation.
"""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.crop_repo import CropRepository
from app.schemas.crop import CropCreate, CropUpdate, CropDetailResponse
from app.services.calendar_service import (
    build_calendar_items,
    build_crop_detail,
    build_daily_actions,
)


# ---------------------------------------------------------------------------
# Crop calendar data (simplified for MVP)
# ---------------------------------------------------------------------------

CROP_CALENDAR: dict[str, dict] = {
    "rice": {
        "planting_months": [5, 6, 7],
        "harvest_months": [10, 11],
        "duration_days": 150,
        "season": "kharif",
    },
    "wheat": {
        "planting_months": [10, 11, 12],
        "harvest_months": [3, 4],
        "duration_days": 120,
        "season": "rabi",
    },
    "maize": {
        "planting_months": [6, 7],
        "harvest_months": [9, 10],
        "duration_days": 90,
        "season": "kharif",
    },
    "cotton": {
        "planting_months": [5, 6],
        "harvest_months": [11, 12],
        "duration_days": 180,
        "season": "kharif",
    },
    "tomato": {
        "planting_months": [1, 6, 7],
        "harvest_months": [4, 9, 10],
        "duration_days": 80,
        "season": "all",
    },
    "chilli": {
        "planting_months": [6, 7],
        "harvest_months": [11, 12, 1],
        "duration_days": 120,
        "season": "kharif",
    },
    "groundnut": {
        "planting_months": [6, 7],
        "harvest_months": [10, 11],
        "duration_days": 110,
        "season": "kharif",
    },
    "soybean": {
        "planting_months": [6, 7],
        "harvest_months": [10, 11],
        "duration_days": 100,
        "season": "kharif",
    },
    "sugarcane": {
        "planting_months": [1, 2, 3],
        "harvest_months": [12, 1, 2],
        "duration_days": 365,
        "season": "annual",
    },
    "pulses": {
        "planting_months": [6, 7, 10],
        "harvest_months": [10, 11, 3],
        "duration_days": 90,
        "season": "kharif/rabi",
    },
}


class CropService:
    """Service class for crop management and calendar."""

    @staticmethod
    async def create_crop(db: AsyncSession, farmer_id: str, data: CropCreate):
        """Create a new crop record for a farmer.

        Args:
            db: Async database session.
            farmer_id: The owning farmer's ID.
            data: Crop creation data.

        Returns:
            The created Crop instance.
        """
        crop_data = data.model_dump()
        crop_data["farmer_id"] = farmer_id

        # Calculate total cost
        seed_cost = crop_data.get("seed_cost") or 0
        fert_cost = crop_data.get("fertilizer_cost") or 0
        pest_cost = crop_data.get("pesticide_cost") or 0
        crop_data["total_cost"] = seed_cost + fert_cost + pest_cost

        return await CropRepository.create(db, crop_data)

    @staticmethod
    async def get_crop(db: AsyncSession, crop_id: str, farmer_id: str):
        """Get a specific crop for a farmer.

        Args:
            db: Async database session.
            crop_id: Crop unique identifier.
            farmer_id: The owning farmer's ID.

        Returns:
            Crop instance if found and owned, None otherwise.
        """
        return await CropRepository.get_by_farmer_and_id(db, crop_id, farmer_id)

    @staticmethod
    async def update_crop(
        db: AsyncSession, crop_id: str, data: CropUpdate
    ):
        """Update a crop record.

        Args:
            db: Async database session.
            crop_id: The crop's unique identifier.
            data: Update data.

        Returns:
            Updated Crop instance, or None if not found.
        """
        update_data = data.model_dump(exclude_unset=True)

        # Recalculate total cost if any cost field changed
        cost_fields = {"seed_cost", "fertilizer_cost", "pesticide_cost"}
        if cost_fields.intersection(update_data.keys()):
            crop = await CropRepository.get_by_id(db, crop_id)
            if crop:
                seed = update_data.get("seed_cost", crop.seed_cost) or 0
                fert = update_data.get("fertilizer_cost", crop.fertilizer_cost) or 0
                pest = update_data.get("pesticide_cost", crop.pesticide_cost) or 0
                update_data["total_cost"] = seed + fert + pest

        return await CropRepository.update(db, crop_id, update_data)

    @staticmethod
    async def delete_crop(db: AsyncSession, crop_id: str) -> bool:
        """Delete a crop record.

        Args:
            db: Async database session.
            crop_id: The crop's unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        return await CropRepository.delete(db, crop_id)

    @staticmethod
    async def list_farmer_crops(
        db: AsyncSession, farmer_id: str, skip: int = 0, limit: int = 20
    ) -> tuple[list, int]:
        """List all crops for a farmer with pagination.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            skip: Offset.
            limit: Maximum records.

        Returns:
            Tuple of (list of crops, total count).
        """
        crops = await CropRepository.list_by_farmer(db, farmer_id, skip, limit)
        total = await CropRepository.count_by_farmer(db, farmer_id)
        return crops, total

    @staticmethod
    async def get_status_counts(db: AsyncSession, farmer_id: str) -> dict:
        """Get crop counts grouped by status.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.

        Returns:
            Dict mapping status to count.
        """
        return await CropRepository.count_by_status(db, farmer_id)

    @staticmethod
    def get_crop_calendar() -> dict:
        """Get the crop planting and harvesting calendar.

        Returns:
            Dict with crop names mapped to their calendar info.
        """
        return CROP_CALENDAR

    @staticmethod
    def get_upcoming_tasks() -> list[dict]:
        """Get farming tasks for the current month based on the calendar.

        Returns:
            List of task dicts with crop, action, and timing info.
        """
        today = date.today()
        current_month = today.month
        tasks: list[dict] = []

        for crop_name, info in CROP_CALENDAR.items():
            if current_month in info["planting_months"]:
                tasks.append({
                    "crop": crop_name,
                    "action": "plant",
                    "month": current_month,
                    "description": f"Optimal time to plant {crop_name}",
                    "season": info["season"],
                })
            if current_month in info["harvest_months"]:
                tasks.append({
                    "crop": crop_name,
                    "action": "harvest",
                    "month": current_month,
                    "description": f"Optimal time to harvest {crop_name}",
                    "season": info["season"],
                })

        return tasks

    # -------------------------------------------------------------------
    # Personalised crop calendar
    # -------------------------------------------------------------------

    @staticmethod
    async def get_crop_calendar(
        db: AsyncSession, farmer_id: str
    ) -> dict:
        """Generate a personalised crop calendar for a farmer.

        Iterates over every crop the farmer owns, calculates the current
        growth stage based on the sowing date, and returns stage-specific
        tasks, advice, and priority levels.

        Args:
            db: Async database session.
            farmer_id: The owning farmer's ID.

        Returns:
            Dict with ``crops`` (list of calendar items) and
            ``daily_actions`` (list of priority actions for today).
        """
        crops = await CropRepository.list_by_farmer(db, farmer_id, skip=0, limit=100)
        today = date.today()

        calendar_items: list[dict] = []
        daily_actions: list[dict] = []

        for crop in crops:
            item = build_calendar_items(
                crop_id=str(crop.id),
                crop_name=crop.name,
                sowing_date=crop.planting_date,
                today=today,
            )
            if item is not None:
                calendar_items.append(item)

            actions = build_daily_actions(
                crop_id=str(crop.id),
                crop_name=crop.name,
                sowing_date=crop.planting_date,
                today=today,
            )
            daily_actions.extend(actions)

        return {"crops": calendar_items, "daily_actions": daily_actions}

    @staticmethod
    async def get_daily_actions(
        db: AsyncSession, farmer_id: str
    ) -> list[dict]:
        """Return today's priority actions across all of a farmer's crops.

        Only returns actions for crops that have a supported timeline and
        an active sowing date.

        Args:
            db: Async database session.
            farmer_id: The owning farmer's ID.

        Returns:
            List of daily action dicts, sorted by priority (high first).
        """
        crops = await CropRepository.list_by_farmer(db, farmer_id, skip=0, limit=100)
        today = date.today()
        all_actions: list[dict] = []

        for crop in crops:
            actions = build_daily_actions(
                crop_id=str(crop.id),
                crop_name=crop.name,
                sowing_date=crop.planting_date,
                today=today,
            )
            all_actions.extend(actions)

        # Sort: high → medium → low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        all_actions.sort(key=lambda a: priority_order.get(a.get("priority", "low"), 2))

        return all_actions

    @staticmethod
    async def get_crop_detail(
        db: AsyncSession, crop_id: str, farmer_id: str
    ) -> Optional[CropDetailResponse]:
        """Return full crop info enriched with calendar stage details.

        Fetches the crop and augments it with the current growth stage,
        days since sowing, week number, and next recommended action.

        Args:
            db: Async database session.
            crop_id: The crop's unique identifier.
            farmer_id: The owning farmer's ID.

        Returns:
            ``CropDetailResponse`` if the crop is found, ``None`` otherwise.
        """
        crop = await CropRepository.get_by_farmer_and_id(db, crop_id, farmer_id)
        if crop is None:
            return None

        detail = build_crop_detail(
            crop_id=str(crop.id),
            crop_name=crop.name,
            sowing_date=crop.planting_date,
        )

        return CropDetailResponse(
            id=str(crop.id),
            farmer_id=crop.farmer_id,
            name=crop.name,
            variety=crop.variety,
            area_acres=crop.area_acres,
            planting_date=crop.planting_date,
            expected_harvest_date=crop.expected_harvest_date,
            soil_type=crop.soil_type,
            irrigation_type=crop.irrigation_type,
            seed_cost=crop.seed_cost,
            fertilizer_cost=crop.fertilizer_cost,
            pesticide_cost=crop.pesticide_cost,
            notes=crop.notes,
            status=crop.status,
            actual_harvest_date=crop.actual_harvest_date,
            yield_quantity=crop.yield_quantity,
            sale_price=crop.sale_price,
            total_cost=crop.total_cost,
            created_at=crop.created_at,
            updated_at=crop.updated_at,
            current_stage=detail["current_stage"],
            days_since_sowing=detail["days_since_sowing"],
            week_number=detail["week_number"],
            next_action=detail["next_action"],
        )
