"""Repository for farmer database operations.

Uses async SQLAlchemy for all database interactions.
"""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.farmer import Farmer


class FarmerRepository:
    """Repository class for Farmer CRUD operations.

    Encapsulates all database queries related to the farmers table.
    """

    @staticmethod
    async def get_by_id(db: AsyncSession, farmer_id: str) -> Optional[Farmer]:
        """Fetch a farmer by their unique ID.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.

        Returns:
            Farmer instance if found, None otherwise.
        """
        result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_phone(db: AsyncSession, phone: str) -> Optional[Farmer]:
        """Fetch a farmer by their phone number.

        Args:
            db: Async database session.
            phone: The farmer's phone number.

        Returns:
            Farmer instance if found, None otherwise.
        """
        result = await db.execute(select(Farmer).where(Farmer.phone == phone))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, farmer_data: dict) -> Farmer:
        """Create a new farmer record.

        Args:
            db: Async database session.
            farmer_data: Dict of field values for the new farmer.

        Returns:
            The created Farmer instance with generated fields.
        """
        farmer = Farmer(**farmer_data)
        db.add(farmer)
        await db.flush()
        await db.refresh(farmer)
        return farmer

    @staticmethod
    async def update(db: AsyncSession, farmer_id: str, data: dict) -> Optional[Farmer]:
        """Update an existing farmer's profile.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            data: Dict of fields to update (None values are skipped).

        Returns:
            The updated Farmer instance, or None if not found.
        """
        farmer = await FarmerRepository.get_by_id(db, farmer_id)
        if farmer is None:
            return None

        for key, value in data.items():
            if value is not None and hasattr(farmer, key):
                setattr(farmer, key, value)

        await db.flush()
        await db.refresh(farmer)
        return farmer

    @staticmethod
    async def list_all(
        db: AsyncSession, skip: int = 0, limit: int = 20
    ) -> list[Farmer]:
        """List all farmers with pagination.

        Args:
            db: Async database session.
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.

        Returns:
            List of Farmer instances.
        """
        result = await db.execute(
            select(Farmer).offset(skip).limit(limit).order_by(Farmer.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def count(db: AsyncSession) -> int:
        """Count total number of farmers.

        Args:
            db: Async database session.

        Returns:
            Total count of farmer records.
        """
        result = await db.execute(select(func.count()).select_from(Farmer))
        return result.scalar() or 0
