"""Disease detection API endpoints.

After a successful scan, disease alerts are automatically sent as
push notifications (via NotificationService.create_disease_alert)
when the result is not healthy.
"""

import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import validate_image
from app.database import get_db
from app.dependencies import get_current_user
from app.models.farmer import Farmer
from app.services.disease_service import DiseaseService
from app.services.notification_service import NotificationService

logger = logging.getLogger("mithrava.disease")

router = APIRouter(prefix="/disease", tags=["Disease Detection"])


async def _send_disease_notification(
    db: AsyncSession,
    farmer_id: str,
    crop_id: str | None,
    disease_name: str | None,
    severity: str | None,
    confidence: float | None,
) -> None:
    """Send a push notification for disease detection results.

    Only sends if the crop is NOT healthy and severity is medium or above.
    Looks up the crop name from the crop_id if available.
    """
    if not disease_name or severity is None:
        return

    # Determine crop name
    crop_name = "your crop"
    if crop_id:
        from sqlalchemy import select
        from app.models.crop import Crop

        crop_result = await db.execute(
            select(Crop.name).where(Crop.id == crop_id, Crop.farmer_id == farmer_id)
        )
        row = crop_result.first()
        if row:
            crop_name = row[0]

    try:
        await NotificationService.create_disease_alert(
            db=db,
            farmer_id=farmer_id,
            crop_name=crop_name,
            disease_name=disease_name,
            severity=severity or "low",
            confidence=(confidence or 0) * 100,
        )
    except Exception as exc:
        # Notification failure should never block the scan response
        logger.warning("Disease notification failed: %s", exc)


@router.post("/analyze")
async def analyze_disease(
    file: UploadFile = File(..., description="Crop image to analyze"),
    crop_id: str = Form(default=None, description="Associated crop ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Upload a crop image and analyze it for diseases.

    Accepts JPEG, PNG, WebP images up to 10MB.
    Returns disease name, confidence, severity, and treatment.
    """
    # Validate image
    if not await validate_image(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image. Accepted formats: JPEG, PNG, WebP. Max size: 10MB.",
        )

    # Read image data
    image_data = await file.read()

    result = await DiseaseService.analyze_image(
        db=db,
        image_data=image_data,
        farmer_id=str(current_user.id),
        crop_id=crop_id,
        image_filename=file.filename or "upload.jpg",
    )

    # Send push notification if disease detected (not healthy)
    if not result.is_healthy:
        await _send_disease_notification(
            db=db,
            farmer_id=str(current_user.id),
            crop_id=crop_id,
            disease_name=result.disease_name,
            severity=result.severity,
            confidence=result.confidence,
        )

    return {
        "success": True,
        "message": "Disease analysis complete",
        "data": {
            "id": str(result.id),
            "farmer_id": str(result.farmer_id),
            "crop_id": str(result.crop_id) if result.crop_id else None,
            "image_url": result.image_url,
            "disease_name": result.disease_name,
            "confidence": result.confidence,
            "severity": result.severity,
            "treatment": result.treatment,
            "created_at": result.created_at.isoformat() if result.created_at else None,
        },
    }


@router.post("/scan")
async def scan_disease_hybrid(
    file: UploadFile = File(..., description="Crop image to analyze"),
    crop_id: str = Form(default=None, description="Associated crop ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Smart disease scan — ML model first, GPT-4o fallback.

    Uses MobileNetV2 for fast, free prediction. If confidence is low,
    automatically falls back to GPT-4o Vision for accurate analysis.

    Accepts JPEG, PNG, WebP images up to 10MB.
    """
    if not await validate_image(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image. Accepted formats: JPEG, PNG, WebP. Max size: 10MB.",
        )

    image_data = await file.read()

    result = await DiseaseService.analyze_with_ml(
        db=db,
        farmer_id=str(current_user.id),
        crop_id=crop_id,
        image_bytes=image_data,
        image_filename=file.filename or "upload.jpg",
    )

    # Send push notification if disease detected (not healthy)
    if not result.get("is_healthy", True):
        await _send_disease_notification(
            db=db,
            farmer_id=str(current_user.id),
            crop_id=crop_id,
            disease_name=result.get("disease_name"),
            severity=result.get("severity"),
            confidence=result.get("confidence"),
        )

    return {
        "success": True,
        "message": f"Analysis complete (method: {result['method']})",
        "data": result,
    }


@router.get("/history")
async def get_disease_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Get the disease scan history for the current farmer."""
    scans, total = await DiseaseService.get_history(
        db, str(current_user.id), skip, limit
    )
    return {
        "success": True,
        "message": "OK",
        "data": {
            "scans": [
                {
                    "id": str(s.id),
                    "disease_name": s.disease_name,
                    "confidence": s.confidence,
                    "severity": s.severity,
                    "image_url": s.image_url,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in scans
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total,
        },
    }


@router.get("/{scan_id}")
async def get_scan_detail(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Get details of a specific disease scan."""
    scan = await DiseaseService.get_scan_by_id(
        db, scan_id, str(current_user.id)
    )
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease scan not found.",
        )
    return {
        "success": True,
        "message": "OK",
        "data": {
            "id": str(scan.id),
            "farmer_id": str(scan.farmer_id),
            "crop_id": str(scan.crop_id) if scan.crop_id else None,
            "image_url": scan.image_url,
            "disease_name": scan.disease_name,
            "confidence": scan.confidence,
            "severity": scan.severity,
            "treatment": scan.treatment,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
        },
    }
