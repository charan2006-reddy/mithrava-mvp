/** Transaction type */
export type TransactionType = "expense" | "income";

/** Expense category */
export type ExpenseCategory =
  | "seeds"
  | "fertilizer"
  | "pesticide"
  | "irrigation"
  | "labor"
  | "equipment"
  | "transport"
  | "storage"
  | "land_rent"
  | "other";

/** Expense record */
export interface Expense {
  id: string;
  farmerId: string;
  category: ExpenseCategory;
  amount: number;
  date: string;
  description?: string;
  cropId?: string;
  receiptUrl?: string;
  createdAt: string;
  updatedAt: string;
}

/** Income record */
export interface Income {
  id: string;
  farmerId: string;
  amount: number;
  date: string;
  description?: string;
  cropId?: string;
  buyerName?: string;
  marketLocation?: string;
  createdAt: string;
  updatedAt: string;
}

/** Finance summary */
export interface FinanceSummary {
  totalExpenses: number;
  totalIncome: number;
  profit: number;
  isProfit: boolean;
  monthlyData: MonthlyFinance[];
  categoryBreakdown: CategoryBreakdown[];
}

/** Monthly finance data */
export interface MonthlyFinance {
  month: string;
  expenses: number;
  income: number;
  profit: number;
}

/** Category breakdown */
export interface CategoryBreakdown {
  category: ExpenseCategory;
  amount: number;
  percentage: number;
}

/** Add expense request */
export interface AddExpenseRequest {
  category: ExpenseCategory;
  amount: number;
  date: string;
  description?: string;
  cropId?: string;
}

/** Add income request */
export interface AddIncomeRequest {
  amount: number;
  date: string;
  description?: string;
  cropId?: string;
  buyerName?: string;
  marketLocation?: string;
}
