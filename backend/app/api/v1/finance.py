"""Finance tracking API endpoints.

Handles expense recording, income tracking, and financial summaries.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.farmer import Farmer
from app.repositories.finance_repo import FinanceRepository
from app.schemas.finance import ExpenseCreate, IncomeCreate

router = APIRouter(prefix="/finance", tags=["Finance"])


@router.get("/summary")
async def get_finance_summary(
    months: int = Query(default=12, ge=1, le=60, description="Months of history"),
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Get the current farmer's financial summary.

    Includes total expenses, total income, profit, monthly breakdown,
    and expense category breakdown.
    """
    summary = await FinanceRepository.get_summary(
        db, str(current_user.id), months
    )
    return {
        "success": True,
        "message": "OK",
        "data": summary,
    }


@router.get("/expenses")
async def list_expenses(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """List expenses for the current farmer."""
    expenses = await FinanceRepository.get_expenses_by_farmer(
        db, str(current_user.id), skip, limit
    )
    return {
        "success": True,
        "message": "OK",
        "data": {
            "expenses": [
                {
                    "id": str(e.id),
                    "category": e.category,
                    "amount": e.amount,
                    "description": e.description,
                    "date": e.date.isoformat() if e.date else None,
                    "crop_id": str(e.crop_id) if e.crop_id else None,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in expenses
            ],
            "total": len(expenses),
            "skip": skip,
            "limit": limit,
        },
    }


@router.post("/expenses", status_code=status.HTTP_201_CREATED)
async def add_expense(
    body: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Add a new expense record."""
    expense_data = body.model_dump()
    expense_data["farmer_id"] = str(current_user.id)

    expense = await FinanceRepository.add_expense(db, expense_data)
    await db.commit()

    return {
        "success": True,
        "message": "Expense recorded successfully",
        "data": {
            "id": str(expense.id),
            "category": expense.category,
            "amount": expense.amount,
            "description": expense.description,
            "date": expense.date.isoformat() if expense.date else None,
        },
    }


@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Delete an expense record."""
    expense = await FinanceRepository.get_expense_by_id(
        db, expense_id, str(current_user.id)
    )
    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )

    await FinanceRepository.delete_expense(db, expense_id)
    await db.commit()

    return {
        "success": True,
        "message": "Expense deleted successfully",
        "data": None,
    }


@router.get("/income")
async def list_income(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """List income records for the current farmer."""
    incomes = await FinanceRepository.get_income_by_farmer(
        db, str(current_user.id), skip, limit
    )
    return {
        "success": True,
        "message": "OK",
        "data": {
            "income": [
                {
                    "id": str(i.id),
                    "amount": i.amount,
                    "quantity_kg": i.quantity_kg,
                    "price_per_kg": i.price_per_kg,
                    "buyer_name": i.buyer_name,
                    "date": i.date.isoformat() if i.date else None,
                    "notes": i.notes,
                    "created_at": i.created_at.isoformat() if i.created_at else None,
                }
                for i in incomes
            ],
            "total": len(incomes),
            "skip": skip,
            "limit": limit,
        },
    }


@router.post("/income", status_code=status.HTTP_201_CREATED)
async def add_income(
    body: IncomeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Add a new income record."""
    income_data = body.model_dump()
    income_data["farmer_id"] = str(current_user.id)

    income = await FinanceRepository.add_income(db, income_data)
    await db.commit()

    return {
        "success": True,
        "message": "Income recorded successfully",
        "data": {
            "id": str(income.id),
            "amount": income.amount,
            "quantity_kg": income.quantity_kg,
            "price_per_kg": income.price_per_kg,
            "buyer_name": income.buyer_name,
            "date": income.date.isoformat() if income.date else None,
        },
    }


@router.delete("/income/{income_id}")
async def delete_income(
    income_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Delete an income record."""
    income = await FinanceRepository.get_income_by_id(
        db, income_id, str(current_user.id)
    )
    if income is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income record not found.",
        )

    await FinanceRepository.delete_income(db, income_id)
    await db.commit()

    return {
        "success": True,
        "message": "Income record deleted successfully",
        "data": None,
    }
