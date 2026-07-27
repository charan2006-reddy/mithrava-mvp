"""Vendor marketplace API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache
from app.database import get_db
from app.dependencies import get_current_user
from app.models.farmer import Farmer
from app.schemas.vendor import VendorReviewCreate
from app.services.vendor_service import VendorService

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("/")
async def list_vendors(
    city: Optional[str] = Query(default=None, description="Filter by city"),
    vendor_type: Optional[str] = Query(default=None, description="Filter by type"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List vendors with optional city and type filters."""
    data = await VendorService.list_vendors(
        db, city=city, vendor_type=vendor_type, skip=skip, limit=limit
    )
    return {
        "success": True,
        "message": "OK",
        "data": data,
    }


@router.get("/{vendor_id}")
async def get_vendor(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific vendor."""
    data = await VendorService.get_vendor_detail(db, vendor_id=vendor_id)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found.",
        )
    return {
        "success": True,
        "message": "OK",
        "data": data,
    }


@router.post("/{vendor_id}/review", status_code=status.HTTP_201_CREATED)
async def add_vendor_review(
    vendor_id: str,
    body: VendorReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Add a review for a vendor."""
    data = await VendorService.add_review(
        db,
        vendor_id=vendor_id,
        farmer_id=str(current_user.id),
        rating=body.rating,
        comment=body.comment,
    )
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found.",
        )
    if data == "duplicate":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this vendor.",
        )
    await db.commit()
    await cache.invalidate_pattern("vendors:list")
    return {
        "success": True,
        "message": "Review added successfully",
        "data": data,
    }
