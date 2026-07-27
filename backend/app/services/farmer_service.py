"""Farmer service layer.

Provides business logic for farmer CRUD operations, sitting between
the API layer and the repository layer.
"""

from datetime import date, timedelta
from typing import Optional

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import upload_image
from app.models.crop import Crop
from app.models.finance import Expense
from app.models.farmer import Farmer
from app.models.finance import Income
from app.repositories.farmer_repo import FarmerRepository
from app.schemas.farmer import FarmerCreate, FarmerUpdate


class FarmerService:
    """Service class for farmer profile management."""

    @staticmethod
    async def get_farmer(db: AsyncSession, farmer_id: str):
        """Get a farmer by ID.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.

        Returns:
            Farmer instance or None.
        """
        return await FarmerRepository.get_by_id(db, farmer_id)

    @staticmethod
    async def get_farmer_by_phone(db: AsyncSession, phone: str):
        """Get a farmer by phone number.

        Args:
            db: Async database session.
            phone: The farmer's phone number.

        Returns:
            Farmer instance or None.
        """
        return await FarmerRepository.get_by_phone(db, phone)

    @staticmethod
    async def update_farmer(
        db: AsyncSession, farmer_id: str, data
    ):
        """Update a farmer's profile.

        Only non-None fields are updated.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            data: Update data — either a Pydantic model or a plain dict.

        Returns:
            Updated Farmer instance, or None if not found.
        """
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.model_dump(exclude_unset=True)
        return await FarmerRepository.update(db, farmer_id, update_data)

    @staticmethod
    async def list_farmers(
        db: AsyncSession, skip: int = 0, limit: int = 20
    ) -> tuple[list, int]:
        """List all farmers with pagination.

        Args:
            db: Async database session.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            Tuple of (list of farmers, total count).
        """
        farmers = await FarmerRepository.list_all(db, skip, limit)
        total = await FarmerRepository.count(db)
        return farmers, total

    # -------------------------------------------------------------------
    # Profile management
    # -------------------------------------------------------------------

    @staticmethod
    async def update_profile(
        db: AsyncSession, farmer_id: str, data: dict
    ) -> Optional[Farmer]:
        """Update a farmer's profile fields.

        Accepts a plain dict of field updates. Only non-None values are
        applied — existing values are preserved for keys not present in
        the dict.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            data: Dict of fields to update.

        Returns:
            Updated Farmer instance, or ``None`` if not found.
        """
        cleaned = {k: v for k, v in data.items() if v is not None}
        if not cleaned:
            return await FarmerRepository.get_by_id(db, farmer_id)
        return await FarmerRepository.update(db, farmer_id, cleaned)

    @staticmethod
    async def upload_avatar(
        db: AsyncSession, farmer_id: str, file: UploadFile
    ) -> Optional[Farmer]:
        """Upload and set a profile avatar image for a farmer.

        Uploads the image to storage (local or S3), saves the public URL
        to the farmer's ``profile_image_url`` column, and returns the
        updated farmer.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            file: The uploaded avatar image.

        Returns:
            Updated Farmer instance, or ``None`` if not found.

        Raises:
            ValueError: If the uploaded file is not a valid image.
        """
        image_url = await upload_image(file, folder="avatars")
        return await FarmerRepository.update(
            db, farmer_id, {"profile_image_url": image_url}
        )

    @staticmethod
    async def get_stats(db: AsyncSession, farmer_id: str) -> dict:
        """Compute aggregated dashboard statistics for a farmer.

        Returns total crops, active crops, total land area, expenses,
        income, net profit, and upcoming harvests.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.

        Returns:
            Dict with dashboard statistics.
        """
        # ── Crop counts ───────────────────────────────────────────────
        total_crops_result = await db.execute(
            select(func.count())
            .select_from(Crop)
            .where(Crop.farmer_id == farmer_id)
        )
        total_crops = total_crops_result.scalar() or 0

        active_crops_result = await db.execute(
            select(func.count())
            .select_from(Crop)
            .where(
                Crop.farmer_id == farmer_id,
                Crop.status.in_(["planted", "growing"]),
            )
        )
        active_crops = active_crops_result.scalar() or 0

        # ── Land area ─────────────────────────────────────────────────
        land_result = await db.execute(
            select(func.coalesce(func.sum(Crop.area_acres), 0.0)).where(
                Crop.farmer_id == farmer_id
            )
        )
        total_land_acres = float(land_result.scalar() or 0.0)

        # ── Expenses ──────────────────────────────────────────────────
        expense_result = await db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
                Expense.farmer_id == farmer_id
            )
        )
        total_expenses = float(expense_result.scalar() or 0.0)

        # ── Income ────────────────────────────────────────────────────
        income_result = await db.execute(
            select(func.coalesce(func.sum(Income.amount), 0.0)).where(
                Income.farmer_id == farmer_id
            )
        )
        total_income = float(income_result.scalar() or 0.0)

        # ── Upcoming harvests (next 30 days) ─────────────────────────
        today = date.today()
        harvest_cutoff = today + timedelta(days=30)
        upcoming_result = await db.execute(
            select(func.count())
            .select_from(Crop)
            .where(
                Crop.farmer_id == farmer_id,
                Crop.status.in_(["planted", "growing"]),
                Crop.expected_harvest_date.isnot(None),
                Crop.expected_harvest_date <= harvest_cutoff,
                Crop.expected_harvest_date >= today,
            )
        )
        upcoming_harvests = upcoming_result.scalar() or 0

        return {
            "total_crops": total_crops,
            "active_crops": active_crops,
            "total_land_acres": total_land_acres,
            "total_expenses": total_expenses,
            "total_income": total_income,
            "profit": total_income - total_expenses,
            "upcoming_harvests": upcoming_harvests,
        }
