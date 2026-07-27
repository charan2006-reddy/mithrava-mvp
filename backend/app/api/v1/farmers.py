"""Farmer profile API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.farmer import Farmer
from app.schemas.farmer import FarmerUpdate
from app.services.farmer_service import FarmerService

router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.get("/")
async def list_farmers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """List all farmers (admin only).

    Supports pagination via skip and limit query parameters.
    """
    farmers, total = await FarmerService.list_farmers(db, skip, limit)
    return {
        "success": True,
        "message": "OK",
        "data": {
            "farmers": [
                {
                    "id": str(f.id),
                    "name": f.name,
                    "phone": f.phone,
                    "email": f.email,
                    "city": f.city,
                    "state": f.state,
                    "is_active": f.is_active,
                    "is_verified": f.is_verified,
                    "role": f.role,
                    "created_at": f.created_at.isoformat() if f.created_at else None,
                }
                for f in farmers
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total,
        },
    }


@router.get("/me")
async def get_my_profile(current_user: Farmer = Depends(get_current_user)):
    """Get the current user's own profile."""
    return {
        "success": True,
        "message": "OK",
        "data": {
            "id": str(current_user.id),
            "name": current_user.name,
            "phone": current_user.phone,
            "email": current_user.email,
            "city": current_user.city,
            "state": current_user.state,
            "preferred_language": current_user.preferred_language,
            "farm_size_acres": current_user.farm_size_acres,
            "soil_type": current_user.soil_type,
            "irrigation_type": current_user.irrigation_type,
            "profile_image_url": current_user.profile_image_url,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
    }


@router.put("/me")
async def update_my_profile(
    body: FarmerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Update the current user's profile."""
    update_data = body.model_dump(exclude_unset=True)
    updated = await FarmerService.update_farmer(db, str(current_user.id), update_data)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found.",
        )

    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": {
            "id": str(updated.id),
            "name": updated.name,
            "phone": updated.phone,
            "email": updated.email,
            "city": updated.city,
            "state": updated.state,
            "preferred_language": updated.preferred_language,
            "farm_size_acres": updated.farm_size_acres,
            "soil_type": updated.soil_type,
            "irrigation_type": updated.irrigation_type,
            "profile_image_url": updated.profile_image_url,
        },
    }


@router.put("/me/avatar")
async def upload_avatar(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Upload a profile avatar image for the current user.

    Accepts an image file (JPEG, PNG, WebP). The previous avatar is
    replaced and the new URL is returned.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only image files are accepted (JPEG, PNG, WebP).",
        )

    try:
        updated = await FarmerService.upload_avatar(
            db, str(current_user.id), file
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found.",
        )

    return {
        "success": True,
        "message": "Avatar uploaded successfully",
        "data": {
            "profile_image_url": updated.profile_image_url,
        },
    }


@router.get("/me/stats")
async def get_my_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Return aggregated dashboard statistics for the current farmer.

    Includes total crops, active crops, total land area, expenses,
    income, net profit, and upcoming harvests.
    """
    stats = await FarmerService.get_stats(db, str(current_user.id))
    return {
        "success": True,
        "message": "OK",
        "data": stats,
    }


@router.get("/{farmer_id}")
async def get_farmer_by_id(
    farmer_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """Get a specific farmer by ID (admin only)."""
    farmer = await FarmerService.get_farmer(db, farmer_id)
    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found.",
        )
    return {
        "success": True,
        "message": "OK",
        "data": {
            "id": str(farmer.id),
            "name": farmer.name,
            "phone": farmer.phone,
            "email": farmer.email,
            "city": farmer.city,
            "state": farmer.state,
            "preferred_language": farmer.preferred_language,
            "farm_size_acres": farmer.farm_size_acres,
            "soil_type": farmer.soil_type,
            "irrigation_type": farmer.irrigation_type,
            "profile_image_url": farmer.profile_image_url,
            "is_active": farmer.is_active,
            "is_verified": farmer.is_verified,
            "role": farmer.role,
            "created_at": farmer.created_at.isoformat() if farmer.created_at else None,
            "updated_at": farmer.updated_at.isoformat() if farmer.updated_at else None,
        },
    }
