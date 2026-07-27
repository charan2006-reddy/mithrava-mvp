"""Disease detection and scanning schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DiseaseScanResponse(BaseModel):
    """Schema for a single disease scan result."""

    id: str = Field(..., description="Unique scan ID")
    farmer_id: str
    crop_id: Optional[str] = Field(default=None)
    image_url: str = Field(..., description="URL of the uploaded image")
    disease_name: str = Field(..., description="Detected disease name")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Detection confidence (0-1)"
    )
    severity: str = Field(
        ...,
        pattern=r"^(low|medium|high|critical)$",
        description="Disease severity level",
    )
    treatment: str = Field(..., description="Recommended treatment advice")
    alternative_diagnoses: Optional[list[dict]] = Field(
        default=None,
        description="Other possible diagnoses with confidence scores",
    )
    created_at: datetime

    model_config = {"from_attributes": True}


class DiseaseHistoryResponse(BaseModel):
    """Paginated disease scan history."""

    scans: list[DiseaseScanResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
    summary: Optional[dict] = Field(
        default=None,
        description="Summary statistics of scans",
    )
