"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Wallet, ArrowUpRight, ArrowDownRight, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/hooks/useLanguage";
import { useQuery } from "@tanstack/react-query";
import { financeService } from "@/services/financeService";
import { formatCurrency } from "@/lib/utils";

export default function FinanceContent() {
  const { t } = useLanguage();

  const { data: summaryData, isLoading } = useQuery({
    queryKey: ["finance", "summary"],
    queryFn: async () => {
      const res = await financeService.getSummary(6);
      return res.data;
    },
  });

  const { data: expensesData } = useQuery({
    queryKey: ["finance", "expenses"],
    queryFn: async () => {
      const res = await financeService.getExpenses({ skip: 0, limit: 5 });
      return res.data;
    },
  });

  const { data: incomeData } = useQuery({
    queryKey: ["finance", "income"],
    queryFn: async () => {
      const res = await financeService.getIncome({ skip: 0, limit: 5 });
      return res.data;
    },
  });

  if (isLoading) {
    return (
      <div className="p-4 space-y-4">
        <h1 className="text-2xl font-bold">{t("finance.title")}</h1>
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-28 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const sd = summaryData as Record<string, unknown> | undefined;
  const totalExpenses = (sd?.total_expenses as number) ?? 0;
  const totalIncome = (sd?.total_income as number) ?? 0;
  const profit = (sd?.profit as number) ?? 0;
  const monthlyData = (sd?.monthly_data ?? sd?.monthlyData ?? []) as Array<Record<string, unknown>>;
  const expenseBreakdown = (sd?.expense_breakdown ?? sd?.categoryBreakdown ?? {}) as Record<string, number>;

  // Combine expenses and income into recent transactions
  const ed = expensesData as Record<string, unknown> | undefined;
  const expensesList = (ed?.expenses ?? ed?.data ?? []) as Array<Record<string, unknown>>;
  const recentExpenses = expensesList.map((e) => ({
    id: e.id as string,
    type: "expense" as const,
    description: (e.description as string) || (e.category as string),
    amount: e.amount as number,
    date: e.date as string,
    category: e.category as string,
  }));

  const incd = incomeData as Record<string, unknown> | undefined;
  const incomeList = (incd?.income ?? incd?.data ?? []) as Array<Record<string, unknown>>;
  const recentIncome = incomeList.map((i) => ({
    id: i.id as string,
    type: "income" as const,
    description: i.buyer_name ? `Sold to ${i.buyer_name}` : "Crop sale",
    amount: i.amount as number,
    date: i.date as string,
  }));

  const allTransactions = [...recentExpenses, ...recentIncome]
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, 5);

  // Prepare chart data (last 6 months)
  const chartMonths = monthlyData.slice(-6);
  const maxVal = Math.max(
    1,
    ...chartMonths.map((m: any) => Math.max(m.expenses, m.income))
  );

  const CATEGORY_EMOJI: Record<string, string> = {
    seeds: "🌱",
    fertilizer: "🧪",
    pesticide: "🧴",
    irrigation: "💧",
    labor: "👷",
    equipment: "🚜",
    transport: "🚛",
    other: "📦",
  };

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">{t("finance.title")}</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="border-red-200">
            <CardContent className="p-4 text-center">
              <div className="h-10 w-10 mx-auto mb-2 rounded-lg bg-red-100 flex items-center justify-center">
                <TrendingDown className="h-5 w-5 text-red-500" />
              </div>
              <p className="text-sm text-gray-500">{t("finance.totalExpenses")}</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                {formatCurrency(totalExpenses)}
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="border-green-200">
            <CardContent className="p-4 text-center">
              <div className="h-10 w-10 mx-auto mb-2 rounded-lg bg-green-100 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-green-500" />
              </div>
              <p className="text-sm text-gray-500">{t("finance.totalIncome")}</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {formatCurrency(totalIncome)}
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="border-mithrava-200 bg-mithrava-50">
            <CardContent className="p-4 text-center">
              <div className="h-10 w-10 mx-auto mb-2 rounded-lg bg-mithrava-100 flex items-center justify-center">
                <Wallet className="h-5 w-5 text-mithrava-500" />
              </div>
              <p className="text-sm text-gray-500">
                {profit >= 0 ? t("finance.profit") : t("finance.loss")}
              </p>
              <p className="text-2xl font-bold text-mithrava-600 mt-1">
                {formatCurrency(profit)}
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Monthly Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">📊 {t("finance.monthlyOverview")}</CardTitle>
        </CardHeader>
        <CardContent>
          {chartMonths.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-8">No financial data yet. Add expenses and income to see charts.</p>
          ) : (
            <>
              <div className="flex items-end gap-3 h-48">
                {chartMonths.map((month: any, i: number) => {
                  const expenseHeight = (month.expenses / maxVal) * 100;
                  const incomeHeight = (month.income / maxVal) * 100;
                  const monthLabel = new Date(month.month + "-01").toLocaleDateString("en-IN", { month: "short" });

                  return (
                    <div key={month.month} className="flex-1 flex flex-col items-center gap-1">
                      <div className="w-full flex gap-0.5 items-end" style={{ height: "140px" }}>
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: `${expenseHeight}%` }}
                          transition={{ delay: i * 0.1, duration: 0.5 }}
                          className="flex-1 bg-red-300 rounded-t"
                          title={`Expenses: ${formatCurrency(month.expenses)}`}
                        />
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: `${incomeHeight}%` }}
                          transition={{ delay: i * 0.1 + 0.05, duration: 0.5 }}
                          className="flex-1 bg-green-400 rounded-t"
                          title={`Income: ${formatCurrency(month.income)}`}
                        />
                      </div>
                      <span className="text-xs text-gray-500">{monthLabel}</span>
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-center gap-4 mt-4 text-xs">
                <div className="flex items-center gap-1">
                  <div className="h-3 w-3 bg-red-300 rounded" />
                  <span>{t("finance.expenses")}</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="h-3 w-3 bg-green-400 rounded" />
                  <span>{t("finance.income")}</span>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Expense Breakdown */}
      {Object.keys(expenseBreakdown).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">🏷️ Expense Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(expenseBreakdown)
                .sort(([, a], [, b]) => (b as number) - (a as number))
                .map(([category, amount]) => {
                  const pct = totalExpenses > 0 ? ((amount as number) / totalExpenses) * 100 : 0;
                  return (
                    <div key={category} className="flex items-center gap-3">
                      <span className="text-lg w-8 text-center">{CATEGORY_EMOJI[category] || "📦"}</span>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium capitalize">{category}</span>
                          <span className="text-xs text-gray-500">{formatCurrency(amount as number)} ({pct.toFixed(0)}%)</span>
                        </div>
                        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-mithrava-400 rounded-full"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">📝 Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          {allTransactions.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-6">No transactions yet</p>
          ) : (
            <div className="space-y-2">
              {allTransactions.map((tx) => (
                <div key={tx.id} className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
                  <div
                    className={`h-10 w-10 rounded-lg flex items-center justify-center shrink-0 ${
                      tx.type === "income" ? "bg-green-100" : "bg-red-100"
                    }`}
                  >
                    {tx.type === "income" ? (
                      <ArrowUpRight className="h-5 w-5 text-green-600" />
                    ) : (
                      <ArrowDownRight className="h-5 w-5 text-red-600" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{tx.description}</p>
                    <p className="text-xs text-gray-500">{tx.date}</p>
                  </div>
                  <p
                    className={`text-sm font-semibold shrink-0 ${
                      tx.type === "income" ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {tx.type === "income" ? "+" : "-"}
                    {formatCurrency(tx.amount)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
