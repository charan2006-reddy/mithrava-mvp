"""Support service layer.

Provides business logic for expert support call requests and management.
"""

from typing import Optional, Dict, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.support import SupportCall


class SupportService:
    """Business logic for support calls."""

    @staticmethod
    async def create_call(
        db: AsyncSession,
        farmer_id: str,
        topic: str,
        description: str = "",
        preferred_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a support call request.

        Args:
            db: Async database session.
            farmer_id: The requesting farmer's ID.
            topic: Topic for the support call.
            description: Brief description of the issue.
            preferred_time: Preferred time slot for the call.

        Returns:
            Dict with the created call's summary data.
        """
        call = SupportCall(
            farmer_id=farmer_id,
            topic=topic,
            description=description,
            preferred_time=preferred_time,
            status="pending",
        )
        db.add(call)
        await db.flush()
        await db.refresh(call)

        return {
            "id": str(call.id),
            "topic": call.topic,
            "status": call.status,
            "preferred_time": call.preferred_time,
        }

    @staticmethod
    async def list_calls(
        db: AsyncSession,
        call_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """List all support calls (admin view).

        Args:
            db: Async database session.
            call_status: Optional status filter.
            skip: Pagination offset.
            limit: Maximum number of calls to return.

        Returns:
            Dict with calls list and pagination info.
        """
        query = select(SupportCall)
        if call_status:
            query = query.where(SupportCall.status == call_status)
        query = query.offset(skip).limit(limit).order_by(SupportCall.created_at.desc())
        result = await db.execute(query)
        calls = list(result.scalars().all())

        count_query = select(func.count()).select_from(SupportCall)
        if call_status:
            count_query = count_query.where(SupportCall.status == call_status)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        return {
            "calls": [
                {
                    "id": str(c.id),
                    "farmer_id": str(c.farmer_id),
                    "topic": c.topic,
                    "description": c.description,
                    "preferred_time": c.preferred_time,
                    "status": c.status,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in calls
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    async def list_my_calls(
        db: AsyncSession,
        farmer_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """List support calls for a specific farmer.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            skip: Pagination offset.
            limit: Maximum number of calls to return.

        Returns:
            Dict with calls list and pagination info.
        """
        query = (
            select(SupportCall)
            .where(SupportCall.farmer_id == farmer_id)
            .order_by(SupportCall.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        calls = list(result.scalars().all())

        count_query = (
            select(func.count())
            .select_from(SupportCall)
            .where(SupportCall.farmer_id == farmer_id)
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        return {
            "calls": [
                {
                    "id": str(c.id),
                    "topic": c.topic,
                    "description": c.description,
                    "preferred_time": c.preferred_time,
                    "status": c.status,
                    "admin_notes": c.admin_notes,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in calls
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    async def update_call_status(
        db: AsyncSession,
        call_id: str,
        call_status: str,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a support call status.

        Args:
            db: Async database session.
            call_id: The call's unique identifier.
            call_status: New status value.
            notes: Optional admin notes.

        Returns:
            Dict with updated call data, or None if not found.
        """
        result = await db.execute(select(SupportCall).where(SupportCall.id == call_id))
        call = result.scalar_one_or_none()
        if call is None:
            return None

        call.status = call_status
        if notes:
            call.admin_notes = notes
        await db.flush()

        return {
            "id": str(call.id),
            "status": call.status,
            "admin_notes": call.admin_notes,
        }
