"""Support and expert callback API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.farmer import Farmer
from app.services.support_service import SupportService

router = APIRouter(prefix="/support", tags=["Support"])


@router.post("/request-call")
async def request_expert_call(
    topic: str = Query(..., description="Topic for the call"),
    description: str = Query(default="", description="Brief description"),
    preferred_time: str = Query(default=None, description="Preferred time slot"),
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Request a callback from an agricultural expert."""
    data = await SupportService.create_call(
        db,
        farmer_id=str(current_user.id),
        topic=topic,
        description=description,
        preferred_time=preferred_time,
    )
    return {
        "success": True,
        "message": "Expert callback requested. You will receive a call within 24 hours.",
        "data": data,
    }


@router.get("/my-calls")
async def list_my_calls(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """List the current farmer's own support call requests."""
    data = await SupportService.list_my_calls(
        db,
        farmer_id=str(current_user.id),
        skip=skip,
        limit=limit,
    )
    return {
        "success": True,
        "data": data,
    }


@router.get("/calls")
async def list_calls(
    call_status: str = Query(default=None, description="Filter by status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """List all support call requests (admin only)."""
    data = await SupportService.list_calls(
        db, call_status=call_status, skip=skip, limit=limit
    )
    return {
        "success": True,
        "message": "OK",
        "data": data,
    }


@router.put("/calls/{call_id}")
async def update_call_status(
    call_id: str,
    call_status: str = Query(..., description="New status: pending/scheduled/completed/cancelled"),
    notes: str = Query(default=None, description="Admin notes"),
    db: AsyncSession = Depends(get_db),
    admin: Farmer = Depends(get_current_admin),
):
    """Update a support call status (admin only)."""
    data = await SupportService.update_call_status(
        db, call_id=call_id, call_status=call_status, notes=notes
    )
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support call not found.",
        )
    return {
        "success": True,
        "message": "Call status updated successfully",
        "data": data,
    }
