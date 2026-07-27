"""Repository for crop database operations.

Provides CRUD plus farmer-specific queries for crop management.
"""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crop import Crop


class CropRepository:
    """Repository class for Crop CRUD and query operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, crop_id: str) -> Optional[Crop]:
        """Fetch a crop by its unique ID.

        Args:
            db: Async database session.
            crop_id: The crop's unique identifier.

        Returns:
            Crop instance if found, None otherwise.
        """
        result = await db.execute(select(Crop).where(Crop.id == crop_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_farmer_and_id(
        db: AsyncSession, crop_id: str, farmer_id: str
    ) -> Optional[Crop]:
        """Fetch a crop by ID, ensuring it belongs to the given farmer.

        Args:
            db: Async database session.
            crop_id: The crop's unique identifier.
            farmer_id: The owning farmer's ID.

        Returns:
            Crop instance if found and owned, None otherwise.
        """
        result = await db.execute(
            select(Crop).where(Crop.id == crop_id, Crop.farmer_id == farmer_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, crop_data: dict) -> Crop:
        """Create a new crop record.

        Args:
            db: Async database session.
            crop_data: Dict of field values.

        Returns:
            The created Crop instance.
        """
        crop = Crop(**crop_data)
        db.add(crop)
        await db.flush()
        await db.refresh(crop)
        return crop

    @staticmethod
    async def update(db: AsyncSession, crop_id: str, data: dict) -> Optional[Crop]:
        """Update an existing crop record.

        Args:
            db: Async database session.
            crop_id: The crop's unique identifier.
            data: Dict of fields to update.

        Returns:
            The updated Crop instance, or None if not found.
        """
        crop = await CropRepository.get_by_id(db, crop_id)
        if crop is None:
            return None

        for key, value in data.items():
            if value is not None and hasattr(crop, key):
                setattr(crop, key, value)

        await db.flush()
        await db.refresh(crop)
        return crop

    @staticmethod
    async def delete(db: AsyncSession, crop_id: str) -> bool:
        """Delete a crop record.

        Args:
            db: Async database session.
            crop_id: The crop's unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        crop = await CropRepository.get_by_id(db, crop_id)
        if crop is None:
            return False
        await db.delete(crop)
        await db.flush()
        return True

    @staticmethod
    async def list_by_farmer(
        db: AsyncSession, farmer_id: str, skip: int = 0, limit: int = 20
    ) -> list[Crop]:
        """List all crops belonging to a farmer with pagination.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of Crop instances.
        """
        result = await db.execute(
            select(Crop)
            .where(Crop.farmer_id == farmer_id)
            .offset(skip)
            .limit(limit)
            .order_by(Crop.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def count_by_farmer(db: AsyncSession, farmer_id: str) -> int:
        """Count total crops for a farmer.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.

        Returns:
            Total count of crops for the farmer.
        """
        result = await db.execute(
            select(func.count())
            .select_from(Crop)
            .where(Crop.farmer_id == farmer_id)
        )
        return result.scalar() or 0

    @staticmethod
    async def count_by_status(
        db: AsyncSession, farmer_id: str
    ) -> dict[str, int]:
        """Count crops grouped by status for a farmer.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.

        Returns:
            Dict mapping status to count (e.g., {"planted": 3, "harvested": 5}).
        """
        result = await db.execute(
            select(Crop.status, func.count())
            .where(Crop.farmer_id == farmer_id)
            .group_by(Crop.status)
        )
        return {row[0]: row[1] for row in result.all()}
