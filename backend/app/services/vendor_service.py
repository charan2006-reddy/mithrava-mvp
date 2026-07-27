"""Vendor marketplace service layer.

Provides business logic for vendors, vendor search, and vendor reviews.
"""

from typing import Optional, Dict, Any, Union

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cached
from app.models.vendor import Vendor, VendorReview


class VendorService:
    """Business logic for vendors and vendor reviews."""

    @staticmethod
    @cached(ttl_seconds=120, prefix="vendors:list")
    async def list_vendors(
        db: AsyncSession,
        city: Optional[str] = None,
        vendor_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """List active vendors with optional filters.

        Args:
            db: Async database session.
            city: Optional city filter (case-insensitive partial match).
            vendor_type: Optional exact vendor type filter.
            skip: Pagination offset.
            limit: Maximum number of vendors to return.

        Returns:
            Dict with vendors list and pagination info.
        """
        query = select(Vendor).where(Vendor.is_active == True)
        if city:
            query = query.where(Vendor.city.ilike(f"%{city}%"))
        if vendor_type:
            query = query.where(Vendor.vendor_type == vendor_type)
        query = query.offset(skip).limit(limit).order_by(Vendor.rating.desc())
        result = await db.execute(query)
        vendors = list(result.scalars().all())

        return {
            "vendors": [
                {
                    "id": str(v.id),
                    "name": v.name,
                    "vendor_type": v.vendor_type,
                    "phone": v.phone,
                    "city": v.city,
                    "state": v.state,
                    "rating": v.rating,
                    "review_count": v.review_count,
                    "is_verified": v.is_verified,
                    "description": v.description,
                    "operating_hours": v.operating_hours,
                }
                for v in vendors
            ],
            "total": len(vendors),
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    async def get_vendor_detail(
        db: AsyncSession,
        vendor_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get detailed vendor info with recent reviews.

        Args:
            db: Async database session.
            vendor_id: The vendor's unique identifier.

        Returns:
            Dict with full vendor details and reviews, or None if not found.
        """
        result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
        vendor = result.scalar_one_or_none()
        if vendor is None:
            return None

        reviews_result = await db.execute(
            select(VendorReview)
            .where(VendorReview.vendor_id == vendor_id)
            .order_by(VendorReview.created_at.desc())
            .limit(10)
        )
        reviews = list(reviews_result.scalars().all())

        return {
            "id": str(vendor.id),
            "name": vendor.name,
            "vendor_type": vendor.vendor_type,
            "phone": vendor.phone,
            "email": vendor.email,
            "city": vendor.city,
            "state": vendor.state,
            "address": vendor.address,
            "latitude": vendor.latitude,
            "longitude": vendor.longitude,
            "description": vendor.description,
            "services": vendor.services,
            "operating_hours": vendor.operating_hours,
            "rating": vendor.rating,
            "review_count": vendor.review_count,
            "is_verified": vendor.is_verified,
            "reviews": [
                {
                    "id": str(r.id),
                    "farmer_id": str(r.farmer_id),
                    "rating": r.rating,
                    "comment": r.comment,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in reviews
            ],
        }

    @staticmethod
    async def add_review(
        db: AsyncSession,
        vendor_id: str,
        farmer_id: str,
        rating: float,
        comment: Optional[str] = None,
    ) -> Union[Dict[str, Any], str, None]:
        """Add a review for a vendor.

        Validates that the vendor exists and the farmer hasn't already
        reviewed this vendor, then recalculates the vendor's average rating.

        Args:
            db: Async database session.
            vendor_id: The vendor's unique identifier.
            farmer_id: The reviewing farmer's ID.
            rating: Review rating value.
            comment: Optional review comment.

        Returns:
            Dict with created review data on success,
            ``"duplicate"`` if the farmer already reviewed this vendor,
            or ``None`` if the vendor was not found.
        """
        vendor_result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
        vendor = vendor_result.scalar_one_or_none()
        if vendor is None:
            return None

        existing = await db.execute(
            select(VendorReview).where(
                VendorReview.vendor_id == vendor_id,
                VendorReview.farmer_id == farmer_id,
            )
        )
        if existing.scalar_one_or_none():
            return "duplicate"

        review = VendorReview(
            vendor_id=vendor_id,
            farmer_id=farmer_id,
            rating=rating,
            comment=comment,
        )
        db.add(review)

        # Recalculate vendor rating
        count_result = await db.execute(
            select(func.count(), func.avg(VendorReview.rating)).where(
                VendorReview.vendor_id == vendor_id
            )
        )
        avg_row = count_result.one()
        vendor.review_count = avg_row[0]
        vendor.rating = round(float(avg_row[1] or 0), 1)

        await db.flush()
        await db.refresh(review)

        return {
            "id": str(review.id),
            "rating": review.rating,
            "comment": review.comment,
        }
