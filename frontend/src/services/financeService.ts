import api from "./api";
import type { ApiResponse, PaginatedResponse } from "@/types/api";
import type {
  Expense,
  Income,
  FinanceSummary,
  AddExpenseRequest,
  AddIncomeRequest,
} from "@/types/finance";

export const financeService = {
  /** Get finance summary */
  async getSummary(months?: number): Promise<ApiResponse<FinanceSummary>> {
    const response = await api.get("/api/v1/finance/summary", { params: { months } });
    return response.data;
  },

  /** Get expenses list */
  async getExpenses(params?: { skip?: number; limit?: number }): Promise<ApiResponse<PaginatedResponse<Expense>>> {
    const response = await api.get("/api/v1/finance/expenses", { params });
    return response.data;
  },

  /** Add a new expense */
  async addExpense(data: AddExpenseRequest): Promise<ApiResponse<Expense>> {
    const response = await api.post("/api/v1/finance/expenses", data);
    return response.data;
  },

  /** Delete an expense */
  async deleteExpense(id: string): Promise<ApiResponse<{ message: string }>> {
    const response = await api.delete(`/api/v1/finance/expenses/${id}`);
    return response.data;
  },

  /** Get income list */
  async getIncome(params?: { skip?: number; limit?: number }): Promise<ApiResponse<PaginatedResponse<Income>>> {
    const response = await api.get("/api/v1/finance/income", { params });
    return response.data;
  },

  /** Add a new income record */
  async addIncome(data: AddIncomeRequest): Promise<ApiResponse<Income>> {
    const response = await api.post("/api/v1/finance/income", data);
    return response.data;
  },

  /** Delete an income record */
  async deleteIncome(id: string): Promise<ApiResponse<{ message: string }>> {
    const response = await api.delete(`/api/v1/finance/income/${id}`);
    return response.data;
  },
};
