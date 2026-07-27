"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Plus, ArrowDownRight, Trash2, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useLanguage } from "@/hooks/useLanguage";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { financeService } from "@/services/financeService";
import { formatCurrency } from "@/lib/utils";
import type { ExpenseCategory } from "@/types/finance";
import { EXPENSE_CATEGORIES } from "@/lib/constants";

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

export default function ExpensesPage() {
  const { t } = useLanguage();
  const queryClient = useQueryClient();
  const [showAddModal, setShowAddModal] = useState(false);
  const [formCategory, setFormCategory] = useState("");
  const [formAmount, setFormAmount] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formDate, setFormDate] = useState(new Date().toISOString().split("T")[0]);

  // Fetch expenses
  const { data, isLoading } = useQuery({
    queryKey: ["finance", "expenses"],
    queryFn: async () => {
      const res = await financeService.getExpenses({ skip: 0, limit: 50 });
      return res.data;
    },
  });

  // Add expense mutation
  const addExpenseMutation = useMutation({
    mutationFn: () =>
      financeService.addExpense({
        category: formCategory as ExpenseCategory,
        amount: Number(formAmount),
        description: formDescription.trim() || undefined,
        date: formDate,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["finance"] });
      setFormCategory("");
      setFormAmount("");
      setFormDescription("");
      setFormDate(new Date().toISOString().split("T")[0]);
      setShowAddModal(false);
    },
  });

  // Delete expense mutation
  const deleteExpenseMutation = useMutation({
    mutationFn: (id: string) => financeService.deleteExpense(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["finance"] });
    },
  });

  const ed = data as { expenses?: Array<Record<string, unknown>>; items?: Array<Record<string, unknown>> } | undefined;
  const expenses = ed?.expenses ?? ed?.items ?? [];
  const totalExpenses = expenses.reduce((sum: number, e) => sum + (e.amount as number), 0);

  const handleAdd = () => {
    if (!formCategory || !formAmount || Number(formAmount) <= 0) return;
    addExpenseMutation.mutate();
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("finance.expenses")}</h1>
        <Button onClick={() => setShowAddModal(true)} className="gap-2" size="sm">
          <Plus className="h-5 w-5" />
          {t("finance.addExpense")}
        </Button>
      </div>

      {/* Total */}
      <Card className="bg-red-50 border-red-200">
        <CardContent className="p-4 text-center">
          <p className="text-sm text-gray-500">{t("finance.totalExpenses")}</p>
          <p className="text-3xl font-bold text-red-600 mt-1">
            {formatCurrency(totalExpenses)}
          </p>
          <p className="text-xs text-gray-400 mt-1">{expenses.length} expense{expenses.length !== 1 ? "s" : ""}</p>
        </CardContent>
      </Card>

      {/* Loading */}
      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-20 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      )}

      {/* Empty */}
      {!isLoading && expenses.length === 0 && (
        <Card className="border-dashed border-gray-300">
          <CardContent className="p-8 text-center">
            <span className="text-4xl block mb-2">💸</span>
            <p className="text-sm font-medium text-gray-500">{t("finance.noExpenses")}</p>
            <p className="text-xs text-gray-400 mt-1">{t("finance.noExpensesDesc")}</p>
            <Button onClick={() => setShowAddModal(true)} className="mt-4" size="sm">
              <Plus className="h-4 w-4 mr-1" /> Add First Expense
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Expense List */}
      {!isLoading && expenses.length > 0 && (
        <div className="space-y-2">
          {expenses.map((expense: any, index: number) => (
            <motion.div
              key={expense.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className="hover:shadow-md transition-shadow">
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-red-100 flex items-center justify-center text-lg shrink-0">
                    {CATEGORY_EMOJI[expense.category] || "📦"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">
                      {expense.description || expense.category}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <Badge variant="secondary" className="text-[10px] capitalize">
                        {expense.category}
                      </Badge>
                      <span className="text-xs text-gray-500">{expense.date}</span>
                    </div>
                  </div>
                  <p className="text-sm font-semibold text-red-600 shrink-0">
                    -{formatCurrency(expense.amount)}
                  </p>
                  <button
                    onClick={() => deleteExpenseMutation.mutate(expense.id)}
                    disabled={deleteExpenseMutation.isPending}
                    className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors shrink-0"
                    title="Delete expense"
                  >
                    {deleteExpenseMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </button>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Add Expense Dialog */}
      <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("finance.addExpense")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label>Category *</Label>
              <Select value={formCategory} onValueChange={setFormCategory}>
                <SelectTrigger className="mt-1.5">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {EXPENSE_CATEGORIES.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id}>
                      {cat.icon} {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Amount (₹) *</Label>
              <Input
                type="number"
                placeholder="0"
                min="1"
                value={formAmount}
                onChange={(e) => setFormAmount(e.target.value)}
                className="mt-1.5"
              />
            </div>
            <div>
              <Label>Description</Label>
              <Input
                placeholder="What was it for? (e.g., Urea 50kg bags x2)"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                className="mt-1.5"
              />
            </div>
            <div>
              <Label>Date</Label>
              <Input
                type="date"
                value={formDate}
                onChange={(e) => setFormDate(e.target.value)}
                className="mt-1.5"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddModal(false)}>
              {t("common.cancel")}
            </Button>
            <Button
              onClick={handleAdd}
              disabled={!formCategory || !formAmount || Number(formAmount) <= 0 || addExpenseMutation.isPending}
            >
              {addExpenseMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : null}
              {t("common.save")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
