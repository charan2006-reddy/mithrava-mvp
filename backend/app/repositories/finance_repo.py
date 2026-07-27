"""Repository for finance-related database operations.

Handles expenses, income records, and financial summaries.
"""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finance import Expense, Income


class FinanceRepository:
    """Repository class for Expense and Income CRUD and aggregation."""

    # -----------------------------------------------------------------------
    # Expenses
    # -----------------------------------------------------------------------

    @staticmethod
    async def add_expense(db: AsyncSession, expense_data: dict) -> Expense:
        """Create a new expense record.

        Args:
            db: Async database session.
            expense_data: Dict of expense field values.

        Returns:
            The created Expense instance.
        """
        expense = Expense(**expense_data)
        db.add(expense)
        await db.flush()
        await db.refresh(expense)
        return expense

    @staticmethod
    async def get_expenses_by_farmer(
        db: AsyncSession,
        farmer_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Expense]:
        """List expenses for a farmer with pagination.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of Expense instances, newest first.
        """
        result = await db.execute(
            select(Expense)
            .where(Expense.farmer_id == farmer_id)
            .offset(skip)
            .limit(limit)
            .order_by(Expense.date.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_expense_by_id(
        db: AsyncSession, expense_id: str, farmer_id: str
    ) -> Optional[Expense]:
        """Fetch a single expense by ID, scoped to farmer.

        Args:
            db: Async database session.
            expense_id: Expense unique identifier.
            farmer_id: The owning farmer's ID.

        Returns:
            Expense instance if found, None otherwise.
        """
        result = await db.execute(
            select(Expense).where(
                Expense.id == expense_id,
                Expense.farmer_id == farmer_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_expense(db: AsyncSession, expense_id: str) -> bool:
        """Delete an expense record.

        Args:
            db: Async database session.
            expense_id: The expense to delete.

        Returns:
            True if deleted, False if not found.
        """
        expense = await db.execute(
            select(Expense).where(Expense.id == expense_id)
        )
        record = expense.scalar_one_or_none()
        if record is None:
            return False
        await db.delete(record)
        await db.flush()
        return True

    # -----------------------------------------------------------------------
    # Income
    # -----------------------------------------------------------------------

    @staticmethod
    async def add_income(db: AsyncSession, income_data: dict) -> Income:
        """Create a new income record.

        Args:
            db: Async database session.
            income_data: Dict of income field values.

        Returns:
            The created Income instance.
        """
        income = Income(**income_data)
        db.add(income)
        await db.flush()
        await db.refresh(income)
        return income

    @staticmethod
    async def get_income_by_farmer(
        db: AsyncSession,
        farmer_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Income]:
        """List income records for a farmer with pagination.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of Income instances, newest first.
        """
        result = await db.execute(
            select(Income)
            .where(Income.farmer_id == farmer_id)
            .offset(skip)
            .limit(limit)
            .order_by(Income.date.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_income_by_id(
        db: AsyncSession, income_id: str, farmer_id: str
    ) -> Optional[Income]:
        """Fetch a single income record by ID, scoped to farmer.

        Args:
            db: Async database session.
            income_id: Income unique identifier.
            farmer_id: The owning farmer's ID.

        Returns:
            Income instance if found, None otherwise.
        """
        result = await db.execute(
            select(Income).where(
                Income.id == income_id,
                Income.farmer_id == farmer_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_income(db: AsyncSession, income_id: str) -> bool:
        """Delete an income record.

        Args:
            db: Async database session.
            income_id: The income to delete.

        Returns:
            True if deleted, False if not found.
        """
        income = await db.execute(
            select(Income).where(Income.id == income_id)
        )
        record = income.scalar_one_or_none()
        if record is None:
            return False
        await db.delete(record)
        await db.flush()
        return True

    # -----------------------------------------------------------------------
    # Summary & Aggregation
    # -----------------------------------------------------------------------

    @staticmethod
    async def get_summary(
        db: AsyncSession, farmer_id: str, months: int = 12
    ) -> dict:
        """Compute financial summary for a farmer.

        Includes total expenses, total income, profit, and monthly breakdown.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.
            months: Number of past months to include.

        Returns:
            Dict with total_expenses, total_income, profit, monthly_data,
            and expense_breakdown.
        """
        cutoff = date.today() - timedelta(days=months * 30)

        # Total expenses
        exp_result = await db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
                Expense.farmer_id == farmer_id,
                Expense.date >= cutoff,
            )
        )
        total_expenses = exp_result.scalar() or 0.0

        # Total income
        inc_result = await db.execute(
            select(func.coalesce(func.sum(Income.amount), 0.0)).where(
                Income.farmer_id == farmer_id,
                Income.date >= cutoff,
            )
        )
        total_income = inc_result.scalar() or 0.0

        # Monthly breakdown
        monthly_data: list[dict] = []
        today = date.today()
        for i in range(months):
            month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            if i == 0:
                month_end = today
            else:
                next_month = month_start.replace(month=month_start.month % 12 + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
                month_end = next_month - timedelta(days=1)

            # Monthly expenses
            m_exp = await db.execute(
                select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
                    Expense.farmer_id == farmer_id,
                    Expense.date >= month_start,
                    Expense.date <= month_end,
                )
            )
            month_expenses = m_exp.scalar() or 0.0

            # Monthly income
            m_inc = await db.execute(
                select(func.coalesce(func.sum(Income.amount), 0.0)).where(
                    Income.farmer_id == farmer_id,
                    Income.date >= month_start,
                    Income.date <= month_end,
                )
            )
            month_income = m_inc.scalar() or 0.0

            monthly_data.append({
                "month": month_start.strftime("%Y-%m"),
                "expenses": float(month_expenses),
                "income": float(month_income),
                "profit": float(month_income - month_expenses),
            })

        # Expense breakdown by category
        cat_result = await db.execute(
            select(Expense.category, func.sum(Expense.amount)).where(
                Expense.farmer_id == farmer_id,
                Expense.date >= cutoff,
            ).group_by(Expense.category)
        )
        expense_breakdown = {row[0]: float(row[1]) for row in cat_result.all()}

        return {
            "total_expenses": float(total_expenses),
            "total_income": float(total_income),
            "profit": float(total_income - total_expenses),
            "monthly_data": list(reversed(monthly_data)),
            "expense_breakdown": expense_breakdown,
        }
