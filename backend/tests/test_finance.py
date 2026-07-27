"""Tests for finance endpoints: expenses, income, summary."""

import pytest
from httpx import AsyncClient


class TestFinanceExpenses:
    """Test expense CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_add_expense(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/finance/expenses",
            json={
                "category": "fertilizer",
                "amount": 3500,
                "description": "Urea 50kg bags x2",
                "date": "2025-01-15",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["category"] == "fertilizer"
        assert data["data"]["amount"] == 3500
        assert "id" in data["data"]

    @pytest.mark.asyncio
    async def test_list_expenses(self, client: AsyncClient, auth_headers: dict):
        # Add an expense first
        await client.post(
            "/api/v1/finance/expenses",
            json={"category": "seeds", "amount": 800, "date": "2025-01-10"},
            headers=auth_headers,
        )

        resp = await client.get("/api/v1/finance/expenses", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]["expenses"]) >= 1

    @pytest.mark.asyncio
    async def test_delete_expense(self, client: AsyncClient, auth_headers: dict):
        # Add an expense
        add_resp = await client.post(
            "/api/v1/finance/expenses",
            json={"category": "labor", "amount": 2000, "date": "2025-01-12"},
            headers=auth_headers,
        )
        expense_id = add_resp.json()["data"]["id"]

        # Delete it
        del_resp = await client.delete(
            f"/api/v1/finance/expenses/{expense_id}", headers=auth_headers
        )
        assert del_resp.status_code == 200
        assert del_resp.json()["success"] is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_expense(self, client: AsyncClient, auth_headers: dict):
        resp = await client.delete(
            "/api/v1/finance/expenses/nonexistent-id", headers=auth_headers
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_add_expense_no_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/finance/expenses",
            json={"category": "seeds", "amount": 100, "date": "2025-01-01"},
        )
        assert resp.status_code in (401, 403)


class TestFinanceIncome:
    """Test income CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_add_income(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/finance/income",
            json={
                "amount": 25000,
                "quantity_kg": 500,
                "price_per_kg": 50,
                "buyer_name": "Hyderabad Mandi",
                "date": "2025-01-20",
                "notes": "Tomato sale",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["amount"] == 25000

    @pytest.mark.asyncio
    async def test_list_income(self, client: AsyncClient, auth_headers: dict):
        # Add an income record
        await client.post(
            "/api/v1/finance/income",
            json={"amount": 15000, "date": "2025-01-18"},
            headers=auth_headers,
        )

        resp = await client.get("/api/v1/finance/income", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]["income"]) >= 1

    @pytest.mark.asyncio
    async def test_delete_income(self, client: AsyncClient, auth_headers: dict):
        add_resp = await client.post(
            "/api/v1/finance/income",
            json={"amount": 10000, "date": "2025-01-15"},
            headers=auth_headers,
        )
        income_id = add_resp.json()["data"]["id"]

        del_resp = await client.delete(
            f"/api/v1/finance/income/{income_id}", headers=auth_headers
        )
        assert del_resp.status_code == 200


class TestFinanceSummary:
    """Test GET /api/v1/finance/summary."""

    @pytest.mark.asyncio
    async def test_get_summary_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/finance/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        # With no data, totals should be 0
        summary = data["data"]
        assert summary["total_expenses"] == 0
        assert summary["total_income"] == 0
        assert summary["profit"] == 0

    @pytest.mark.asyncio
    async def test_get_summary_with_data(self, client: AsyncClient, auth_headers: dict):
        # Use dates within the last 2 months so they fall inside the summary window
        await client.post(
            "/api/v1/finance/expenses",
            json={"category": "fertilizer", "amount": 5000, "date": "2026-06-10"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/finance/income",
            json={"amount": 20000, "date": "2026-06-20"},
            headers=auth_headers,
        )

        resp = await client.get("/api/v1/finance/summary?months=6", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        summary = data["data"]
        assert summary["total_expenses"] == 5000
        assert summary["total_income"] == 20000
        assert summary["profit"] == 15000
