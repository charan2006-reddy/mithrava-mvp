"""Disease detection service.

Handles image upload, analysis via LLM Vision, and storage of
disease scan results with history tracking. Supports both the legacy
analysis flow and the enhanced Sprint 3 analysis with structured
treatment recommendations.
"""

import base64
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm import (
    analyze_disease_image,
    analyze_image_with_vision,
    DISEASE_VISION_PROMPT,
    _default_disease_response,
)
from app.core.storage import upload_image
from app.models.crop import Crop
from app.models.disease import DiseaseScan

logger = logging.getLogger("mithrava.disease")


class DiseaseService:
    """Service class for crop disease detection and history."""

    # ------------------------------------------------------------------
    # Sprint 3: Enhanced image analysis
    # ------------------------------------------------------------------

    @staticmethod
    async def analyze_disease_image(
        db: AsyncSession,
        farmer_id: str,
        crop_id: Optional[str],
        image_bytes: bytes,
        image_filename: str = "upload.jpg",
    ) -> DiseaseScan:
        """Analyze a crop image using the enhanced Vision API prompt.

        Performs the full analysis pipeline:
        1. Upload image to storage
        2. Encode to base64 and send to OpenAI Vision
        3. Parse structured response (disease, treatment, prevention)
        4. Save a DiseaseScan record with all fields populated
        5. Return the complete scan result

        Args:
            db: Async database session.
            farmer_id: The farmer submitting the scan.
            crop_id: Optional associated crop ID.
            image_bytes: Raw image bytes.
            image_filename: Original filename for extension detection.

        Returns:
            DiseaseScan instance with full analysis results.

        Raises:
            RuntimeError: If image upload or AI analysis fails.
        """
        import io

        # Step 1: Upload image to storage
        file_obj = io.BytesIO(image_bytes)
        upload_file = UploadFile(
            filename=image_filename,
            file=file_obj,
            content_type="image/jpeg",
        )
        image_url = await upload_image(upload_file, folder="disease_scans")

        # Step 2: Analyze with enhanced Vision prompt
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        analysis = await analyze_image_with_vision(image_base64, DISEASE_VISION_PROMPT)

        # Step 3: Parse and normalize the response
        disease_name = analysis.get("disease_name")
        is_healthy = analysis.get("is_healthy", disease_name is None)
        confidence = float(analysis.get("confidence", 0.0))
        severity = analysis.get("severity", "low")
        description = analysis.get("description", "")

        # Build structured treatment plan
        treatment_json = {
            "organic": analysis.get("organic_treatment", []),
            "chemical": analysis.get("chemical_treatment", []),
            "prevention": analysis.get("prevention", []),
            "urgency": analysis.get("urgency", "when_convenient"),
        }

        # Build prevention data
        prevention_json = {
            "tips": analysis.get("prevention", []),
            "urgency": analysis.get("urgency", "when_convenient"),
        }

        # Legacy treatment string for backward compatibility
        treatment_parts = []
        if analysis.get("organic_treatment"):
            treatment_parts.append(
                "Organic: " + "; ".join(analysis["organic_treatment"])
            )
        if analysis.get("chemical_treatment"):
            treatment_parts.append(
                "Chemical: " + "; ".join(analysis["chemical_treatment"])
            )
        treatment_str = " | ".join(treatment_parts) if treatment_parts else (
            description or "Please consult a local expert."
        )

        now = datetime.now(timezone.utc)

        # Step 4: Create and persist scan record
        scan = DiseaseScan(
            farmer_id=farmer_id,
            crop_id=crop_id,
            image_url=image_url,
            disease_name=disease_name,
            confidence=confidence,
            severity=severity,
            is_healthy=is_healthy,
            description=description,
            treatment=treatment_str,
            treatment_json=treatment_json,
            prevention_json=prevention_json,
            model_version="gpt-4o-v1",
            analyzed_at=now,
        )
        db.add(scan)
        await db.flush()
        await db.refresh(scan)

        logger.info(
            "Disease scan completed: farmer=%s disease=%s confidence=%.2f",
            farmer_id, disease_name, confidence,
        )
        return scan

    # ------------------------------------------------------------------
    # Sprint 3: Detailed scan retrieval
    # ------------------------------------------------------------------

    @staticmethod
    async def get_scan_detail(
        db: AsyncSession, scan_id: str, farmer_id: str
    ) -> Optional[dict]:
        """Get full scan result with treatment plan and follow-up recommendations.

        Args:
            db: Async database session.
            scan_id: The scan's unique identifier.
            farmer_id: The owning farmer's ID.

        Returns:
            Dict with full scan data, treatment plan, and follow-up
            recommendations, or None if not found.
        """
        result = await db.execute(
            select(DiseaseScan, Crop)
            .outerjoin(
                Crop,
                (DiseaseScan.crop_id == Crop.id)
                & (Crop.farmer_id == farmer_id),
            )
            .where(
                DiseaseScan.id == scan_id,
                DiseaseScan.farmer_id == farmer_id,
            )
        )
        row = result.first()
        if row is None:
            return None

        scan, crop = row

        # Build follow-up recommendations based on severity and urgency
        follow_up = DiseaseService._build_follow_up(scan)

        detail = {
            "id": str(scan.id),
            "farmer_id": str(scan.farmer_id),
            "crop_id": str(scan.crop_id) if scan.crop_id else None,
            "image_url": scan.image_url,
            "disease_name": scan.disease_name,
            "confidence": scan.confidence,
            "severity": scan.severity,
            "is_healthy": scan.is_healthy,
            "description": scan.description,
            "treatment": scan.treatment,
            "treatment_json": scan.treatment_json,
            "prevention_json": scan.prevention_json,
            "model_version": scan.model_version,
            "analyzed_at": (
                scan.analyzed_at.isoformat() if scan.analyzed_at else None
            ),
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "follow_up": follow_up,
            "crop": None,
        }

        if crop is not None:
            detail["crop"] = {
                "id": str(crop.id),
                "name": crop.name,
                "variety": crop.variety,
                "area_acres": crop.area_acres,
                "status": crop.status,
            }

        return detail

    @staticmethod
    def _build_follow_up(scan: DiseaseScan) -> dict:
        """Build follow-up recommendations based on scan severity.

        Args:
            scan: The disease scan record.

        Returns:
            Dict with follow-up actions and timing recommendations.
        """
        severity = (scan.severity or "low").lower()
        urgency = "when_convenient"
        if scan.treatment_json and isinstance(scan.treatment_json, dict):
            urgency = scan.treatment_json.get("urgency", "when_convenient")

        actions = []
        re_scan_days = 30

        if severity == "critical":
            actions = [
                "Immediately consult a local agricultural officer",
                "Isolate affected plants if possible",
                "Apply recommended treatment within 24 hours",
                "Take photos of treatment progress daily",
            ]
            re_scan_days = 7
        elif severity == "high":
            actions = [
                "Apply treatment within 2-3 days",
                "Monitor the crop daily for changes",
                "Consult an expert if no improvement in a week",
            ]
            re_scan_days = 14
        elif severity == "medium":
            actions = [
                "Apply treatment within this week",
                "Re-scan in 2 weeks to check progress",
                "Maintain proper irrigation and nutrition",
            ]
            re_scan_days = 21
        else:
            actions = [
                "Monitor the crop regularly",
                "Apply preventive measures as needed",
                "Re-scan if symptoms worsen",
            ]

        if scan.is_healthy:
            actions = [
                "Your crop looks healthy! Continue current practices",
                "Regular monitoring is recommended",
                "Maintain proper nutrition and irrigation",
            ]
            re_scan_days = 30

        return {
            "actions": actions,
            "re_scan_recommended_days": re_scan_days,
            "urgency": urgency,
            "expert_consultation_needed": severity in ("high", "critical"),
        }

    # ------------------------------------------------------------------
    # Existing methods (preserved from Sprint 1/2)
    # ------------------------------------------------------------------

    @staticmethod
    async def analyze_with_ml(
        db: AsyncSession,
        farmer_id: str,
        crop_id: Optional[str],
        image_bytes: bytes,
        image_filename: str = "upload.jpg",
    ) -> dict:
        """Analyze disease using ML model first, with GPT-4o fallback.

        Pipeline:
        1. Run MobileNetV2 inference (free, fast)
        2. If confidence >= 70%, return ML result
        3. If confidence < 70%, fallback to GPT-4o Vision
        4. Save result to database
        5. Return combined result

        Args:
            db: Async database session.
            farmer_id: The farmer submitting the scan.
            crop_id: Optional associated crop ID.
            image_bytes: Raw image bytes.
            image_filename: Original filename.

        Returns:
            Dict with analysis results from ML or GPT-4o.
        """
        from app.services.ml_disease_service import MLDiseaseService

        # Step 1: Try ML model first
        ml_result = await MLDiseaseService.predict(image_bytes)

        if ml_result.get("success") and not ml_result.get("needs_gpt4_fallback"):
            # ML model is confident enough — use its result
            logger.info(
                "ML model prediction: %s (%.1f%%)",
                ml_result["disease_name"],
                ml_result["confidence"],
            )

            # Save to database
            import io
            from fastapi import UploadFile
            from app.core.storage import upload_image

            file_obj = io.BytesIO(image_bytes)
            upload_file = UploadFile(
                filename=image_filename, file=file_obj, content_type="image/jpeg"
            )
            image_url = await upload_image(upload_file, folder="disease_scans")

            treatment_str = ""
            if ml_result.get("treatment"):
                parts = []
                if ml_result["treatment"].get("organic"):
                    parts.append("Organic: " + "; ".join(ml_result["treatment"]["organic"]))
                if ml_result["treatment"].get("chemical"):
                    parts.append("Chemical: " + "; ".join(ml_result["treatment"]["chemical"]))
                treatment_str = " | ".join(parts)

            scan = DiseaseScan(
                farmer_id=farmer_id,
                crop_id=crop_id,
                image_url=image_url,
                disease_name=ml_result["disease_name"],
                confidence=ml_result["confidence"] / 100.0,
                severity=ml_result["severity"],
                is_healthy=ml_result["is_healthy"],
                description=f"Detected by MobileNetV2: {ml_result['disease_name']}",
                treatment=treatment_str or "No treatment needed.",
                treatment_json=ml_result.get("treatment", {}),
                model_version="mobilenetv2-v1",
                analyzed_at=datetime.now(timezone.utc),
            )
            db.add(scan)
            await db.flush()
            await db.refresh(scan)

            return {
                "method": "ML",
                "scan_id": str(scan.id),
                "crop_detected": ml_result["crop_detected"],
                "disease_name": ml_result["disease_name"],
                "confidence": ml_result["confidence"],
                "is_healthy": ml_result["is_healthy"],
                "severity": ml_result["severity"],
                "top_predictions": ml_result.get("top_predictions", []),
                "treatment": ml_result.get("treatment", {}),
                "description": f"Detected by MobileNetV2: {ml_result['disease_name']}",
            }

        # Step 2: ML not confident enough — fallback to GPT-4o
        logger.info(
            "ML confidence too low (%.1f%%), falling back to GPT-4o",
            ml_result.get("confidence", 0),
        )
        gpt4_result = await DiseaseService.analyze_disease_image(
            db, farmer_id, crop_id, image_bytes, image_filename
        )

        return {
            "method": "GPT-4o",
            "scan_id": str(gpt4_result.id),
            "crop_detected": None,
            "disease_name": gpt4_result.disease_name,
            "confidence": (gpt4_result.confidence or 0) * 100,
            "is_healthy": gpt4_result.is_healthy,
            "severity": gpt4_result.severity,
            "top_predictions": [],
            "treatment": gpt4_result.treatment_json or {},
            "description": gpt4_result.description or "",
        }

    @staticmethod
    async def analyze_image(
        db: AsyncSession,
        image_data: bytes,
        farmer_id: str,
        crop_id: Optional[str] = None,
        image_filename: str = "upload.jpg",
    ) -> DiseaseScan:
        """Analyze a crop image for diseases (legacy flow).

        Uploads the image, sends it to the Vision model, and stores
        the scan result.

        Args:
            db: Async database session.
            image_data: Raw image bytes.
            farmer_id: The farmer submitting the scan.
            crop_id: Optional associated crop ID.
            image_filename: Original filename for extension detection.

        Returns:
            DiseaseScan instance with analysis results.
        """
        import io

        file_obj = io.BytesIO(image_data)
        upload_file = UploadFile(
            filename=image_filename,
            file=file_obj,
            content_type="image/jpeg",
        )

        image_url = await upload_image(upload_file, folder="disease_scans")

        image_base64 = base64.b64encode(image_data).decode("utf-8")
        analysis = await analyze_disease_image(image_base64)

        now = datetime.now(timezone.utc)

        scan = DiseaseScan(
            farmer_id=farmer_id,
            crop_id=crop_id,
            image_url=image_url,
            disease_name=analysis.get("disease_name", "Unknown"),
            confidence=analysis.get("confidence", 0.0),
            severity=analysis.get("severity", "medium"),
            is_healthy=analysis.get("is_healthy", False),
            description=analysis.get("description", ""),
            treatment=analysis.get("treatment", "Please consult a local expert."),
            alternative_diagnoses=analysis.get("alternative_diagnoses", []),
            analyzed_at=now,
        )
        db.add(scan)
        await db.flush()
        await db.refresh(scan)
        return scan

    @staticmethod
    async def get_history(
        db: AsyncSession,
        farmer_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[DiseaseScan], int]:
        """Get disease scan history for a farmer.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            Tuple of (list of DiseaseScan, total count).
        """
        result = await db.execute(
            select(DiseaseScan)
            .where(DiseaseScan.farmer_id == farmer_id)
            .offset(skip)
            .limit(limit)
            .order_by(DiseaseScan.created_at.desc())
        )
        scans = list(result.scalars().all())

        count_result = await db.execute(
            select(func.count())
            .select_from(DiseaseScan)
            .where(DiseaseScan.farmer_id == farmer_id)
        )
        total = count_result.scalar() or 0

        return scans, total

    @staticmethod
    async def get_scan_by_id(
        db: AsyncSession, scan_id: str, farmer_id: str
    ) -> Optional[DiseaseScan]:
        """Get a specific disease scan by ID.

        Args:
            db: Async database session.
            scan_id: The scan's unique identifier.
            farmer_id: The owning farmer's ID.

        Returns:
            DiseaseScan instance if found, None otherwise.
        """
        result = await db.execute(
            select(DiseaseScan).where(
                DiseaseScan.id == scan_id,
                DiseaseScan.farmer_id == farmer_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_scan(
        db: AsyncSession, scan_id: str, farmer_id: str
    ) -> bool:
        """Delete a disease scan record.

        Args:
            db: Async database session.
            scan_id: The scan's unique identifier.
            farmer_id: The owning farmer's ID (for authorization).

        Returns:
            True if the scan was found and deleted, False otherwise.
        """
        result = await db.execute(
            select(DiseaseScan).where(
                DiseaseScan.id == scan_id,
                DiseaseScan.farmer_id == farmer_id,
            )
        )
        scan = result.scalar_one_or_none()
        if scan is None:
            return False

        await db.delete(scan)
        await db.flush()
        return True

    @staticmethod
    async def get_recent_scans_with_context(
        db: AsyncSession,
        farmer_id: str,
        skip: int = 0,
        limit: int = 10,
    ) -> list[dict]:
        """Return recent disease scans enriched with crop context.

        Joins each scan with its related crop (if any) to provide the
        frontend with crop name, variety, and area information alongside
        the diagnosis result.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of dicts containing scan data plus crop context.
        """
        result = await db.execute(
            select(DiseaseScan, Crop)
            .outerjoin(
                Crop,
                (DiseaseScan.crop_id == Crop.id)
                & (Crop.farmer_id == farmer_id),
            )
            .where(DiseaseScan.farmer_id == farmer_id)
            .order_by(DiseaseScan.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        rows = result.all()
        scans_with_context: list[dict] = []

        for scan, crop in rows:
            scan_dict = {
                "id": str(scan.id),
                "image_url": scan.image_url,
                "disease_name": scan.disease_name,
                "confidence": scan.confidence,
                "severity": scan.severity,
                "is_healthy": scan.is_healthy,
                "description": scan.description,
                "treatment": scan.treatment,
                "treatment_json": scan.treatment_json,
                "prevention_json": scan.prevention_json,
                "alternative_diagnoses": scan.alternative_diagnoses,
                "created_at": (
                    scan.created_at.isoformat() if scan.created_at else None
                ),
                "crop": None,
            }

            if crop is not None:
                scan_dict["crop"] = {
                    "id": str(crop.id),
                    "name": crop.name,
                    "variety": crop.variety,
                    "area_acres": crop.area_acres,
                    "status": crop.status,
                }

            scans_with_context.append(scan_dict)

        return scans_with_context
