"""Admin dashboard API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.farmer import Farmer
from app.models.crop import Crop
from app.models.disease import DiseaseScan
from app.models.vendor import Vendor
from app.repositories.farmer_repo import FarmerRepository

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """Get dashboard statistics for the admin panel."""
    farmer_count = await FarmerRepository.count(db)

    crop_count_result = await db.execute(select(func.count()).select_from(Crop))
    crop_count = crop_count_result.scalar() or 0

    active_crop_result = await db.execute(
        select(func.count()).select_from(Crop).where(
            Crop.status.in_(["planted", "growing"])
        )
    )
    active_crops = active_crop_result.scalar() or 0

    scan_count_result = await db.execute(select(func.count()).select_from(DiseaseScan))
    scan_count = scan_count_result.scalar() or 0

    vendor_count_result = await db.execute(select(func.count()).select_from(Vendor))
    vendor_count = vendor_count_result.scalar() or 0

    return {
        "success": True,
        "message": "OK",
        "data": {
            "total_farmers": farmer_count,
            "total_crops": crop_count,
            "active_crops": active_crops,
            "disease_scans": scan_count,
            "total_vendors": vendor_count,
        },
    }


@router.get("/farmers")
async def list_all_farmers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """List all farmers (admin)."""
    farmers = await FarmerRepository.list_all(db, skip, limit)
    total = await FarmerRepository.count(db)
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
        },
    }


@router.post("/farmers", status_code=status.HTTP_201_CREATED)
async def admin_create_farmer(
    name: str,
    phone: str,
    email: str = None,
    city: str = None,
    state: str = None,
    role: str = "farmer",
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """Create a new farmer (admin)."""
    data = {
        "name": name,
        "phone": phone,
        "email": email,
        "city": city,
        "state": state,
        "role": role,
    }
    farmer = await FarmerRepository.create(db, data)
    await db.commit()

    return {
        "success": True,
        "message": "Farmer created successfully",
        "data": {
            "id": str(farmer.id),
            "name": farmer.name,
            "phone": farmer.phone,
            "role": farmer.role,
        },
    }


@router.put("/farmers/{farmer_id}")
async def admin_update_farmer(
    farmer_id: str,
    name: str = None,
    phone: str = None,
    email: str = None,
    city: str = None,
    state: str = None,
    is_active: bool = None,
    is_verified: bool = None,
    role: str = None,
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """Update a farmer (admin)."""
    data = {}
    if name is not None:
        data["name"] = name
    if phone is not None:
        data["phone"] = phone
    if email is not None:
        data["email"] = email
    if city is not None:
        data["city"] = city
    if state is not None:
        data["state"] = state
    if is_active is not None:
        data["is_active"] = is_active
    if is_verified is not None:
        data["is_verified"] = is_verified
    if role is not None:
        data["role"] = role

    farmer = await FarmerRepository.update(db, farmer_id, data)
    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found.",
        )
    await db.commit()

    return {
        "success": True,
        "message": "Farmer updated successfully",
        "data": {
            "id": str(farmer.id),
            "name": farmer.name,
            "phone": farmer.phone,
            "is_active": farmer.is_active,
            "is_verified": farmer.is_verified,
            "role": farmer.role,
        },
    }


@router.delete("/farmers/{farmer_id}")
async def admin_delete_farmer(
    farmer_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """Soft-delete a farmer (admin — sets is_active=False)."""
    farmer = await FarmerRepository.get_by_id(db, farmer_id)
    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found.",
        )

    farmer.is_active = False
    await db.commit()

    return {
        "success": True,
        "message": "Farmer deactivated successfully",
        "data": None,
    }


@router.get("/vendors")
async def list_all_vendors(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """List all vendors (admin)."""
    from app.models.vendor import Vendor

    result = await db.execute(
        select(Vendor).offset(skip).limit(limit).order_by(Vendor.created_at.desc())
    )
    vendors = list(result.scalars().all())

    count_result = await db.execute(select(func.count()).select_from(Vendor))
    total = count_result.scalar() or 0

    return {
        "success": True,
        "message": "OK",
        "data": {
            "vendors": [
                {
                    "id": str(v.id),
                    "name": v.name,
                    "vendor_type": v.vendor_type,
                    "phone": v.phone,
                    "city": v.city,
                    "rating": v.rating,
                    "is_active": v.is_active,
                    "is_verified": v.is_verified,
                }
                for v in vendors
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        },
    }


@router.post("/vendors", status_code=status.HTTP_201_CREATED)
async def admin_create_vendor(
    name: str,
    vendor_type: str,
    phone: str,
    city: str,
    state: str = None,
    address: str = None,
    description: str = None,
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """Create a new vendor (admin)."""
    from app.models.vendor import Vendor

    vendor = Vendor(
        name=name,
        vendor_type=vendor_type,
        phone=phone,
        city=city,
        state=state,
        address=address,
        description=description,
    )
    db.add(vendor)
    await db.flush()
    await db.refresh(vendor)
    await db.commit()

    return {
        "success": True,
        "message": "Vendor created successfully",
        "data": {
            "id": str(vendor.id),
            "name": vendor.name,
            "vendor_type": vendor.vendor_type,
        },
    }


@router.put("/vendors/{vendor_id}")
async def admin_update_vendor(
    vendor_id: str,
    name: str = None,
    vendor_type: str = None,
    phone: str = None,
    city: str = None,
    is_active: bool = None,
    is_verified: bool = None,
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """Update a vendor (admin)."""
    from app.models.vendor import Vendor

    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found.",
        )

    if name is not None:
        vendor.name = name
    if vendor_type is not None:
        vendor.vendor_type = vendor_type
    if phone is not None:
        vendor.phone = phone
    if city is not None:
        vendor.city = city
    if is_active is not None:
        vendor.is_active = is_active
    if is_verified is not None:
        vendor.is_verified = is_verified

    await db.commit()

    return {
        "success": True,
        "message": "Vendor updated successfully",
        "data": {
            "id": str(vendor.id),
            "name": vendor.name,
            "is_active": vendor.is_active,
            "is_verified": vendor.is_verified,
        },
    }


@router.delete("/vendors/{vendor_id}")
async def admin_delete_vendor(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """Soft-delete a vendor (admin — sets is_active=False)."""
    from app.models.vendor import Vendor

    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found.",
        )

    vendor.is_active = False
    await db.commit()

    return {
        "success": True,
        "message": "Vendor deactivated successfully",
        "data": None,
    }
