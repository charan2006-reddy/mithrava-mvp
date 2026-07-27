"""Finance tracking schemas for expenses, income, and summaries."""

from datetime import date as _date_type, datetime
from typing import Optional

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    """Schema for recording a new expense."""

    category: str = Field(
        ...,
        pattern=r"^(seeds|fertilizer|pesticide|irrigation|labor|equipment|transport|other)$",
        description="Expense category",
    )
    amount: float = Field(..., gt=0, description="Expense amount in INR")
    description: Optional[str] = Field(default=None, max_length=500)
    date: _date_type = Field(default_factory=_date_type.today, description="Date of expense")
    crop_id: Optional[str] = Field(default=None, description="Associated crop")
    receipt_image_url: Optional[str] = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "category": "fertilizer",
                    "amount": 2500.0,
                    "description": "Urea - 50kg bags x 2",
                    "date": "2025-07-10",
                    "crop_id": "crop_123",
                }
            ]
        }
    }


class ExpenseResponse(ExpenseCreate):
    """Schema for expense data in API responses."""

    id: str
    farmer_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class IncomeCreate(BaseModel):
    """Schema for recording income from crop sales."""

    crop_id: Optional[str] = Field(default=None, description="Sold crop")
    amount: float = Field(..., gt=0, description="Income amount in INR")
    quantity_kg: Optional[float] = Field(default=None, ge=0)
    price_per_kg: Optional[float] = Field(default=None, ge=0)
    buyer_name: Optional[str] = Field(default=None, max_length=200)
    date: _date_type = Field(default_factory=_date_type.today)
    notes: Optional[str] = Field(default=None, max_length=500)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "crop_id": "crop_123",
                    "amount": 25000.0,
                    "quantity_kg": 500,
                    "price_per_kg": 50.0,
                    "buyer_name": "Local Mandi",
                    "date": "2025-10-20",
                }
            ]
        }
    }


class IncomeResponse(IncomeCreate):
    """Schema for income data in API responses."""

    id: str
    farmer_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MonthlyFinanceData(BaseModel):
    """Monthly breakdown for financial summary."""

    month: str = Field(..., description="Month identifier (YYYY-MM)")
    expenses: float = Field(default=0.0)
    income: float = Field(default=0.0)
    profit: float = Field(default=0.0)


class FinanceSummary(BaseModel):
    """Overall financial summary for a farmer."""

    total_expenses: float = Field(default=0.0, description="Total expenses")
    total_income: float = Field(default=0.0, description="Total income")
    profit: float = Field(default=0.0, description="Net profit (income - expenses)")
    monthly_data: list[MonthlyFinanceData] = Field(
        default_factory=list,
        description="Month-wise financial breakdown",
    )
    expense_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Category-wise expense breakdown",
    )
