"use client";

import { useRouter, useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Edit3,
  Trash2,
  Droplets,
  Camera,
  Cloud,
  Wallet,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TextToSpeech } from "@/components/voice/TextToSpeech";
import { CropCalendar } from "@/components/crops/CropCalendar";
import { getCropEmoji } from "@/components/crops/CropCard";
import { useCropDetail, useDeleteCrop } from "@/hooks/useCrops";
import { cn, formatDate, formatCurrency } from "@/lib/utils";
import type { CropStatus } from "@/types/crop";

/* ─── Status / Priority Mappings ─── */

const STATUS_BADGE: Record<
  CropStatus,
  { label: string; variant: "success" | "warning" | "destructive" | "secondary" }
> = {
  planted: { label: "Planted", variant: "secondary" },
  growing: { label: "Growing", variant: "success" },
  harvested: { label: "Harvest Ready", variant: "warning" },
  failed: { label: "Failed", variant: "destructive" },
};

/* ─── Loading Skeleton ─── */

function DetailSkeleton() {
  return (
    <div className="p-4 space-y-4 animate-pulse">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="h-4 w-16 rounded bg-gray-200" />
        <div className="flex gap-2">
          <div className="h-8 w-16 rounded-lg bg-gray-200" />
          <div className="h-8 w-16 rounded-lg bg-gray-200" />
        </div>
      </div>
      {/* Hero skeleton */}
      <div className="rounded-2xl bg-gray-200 h-48 w-full" />
      {/* Quick actions skeleton */}
      <div className="grid grid-cols-4 gap-2">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-20 rounded-xl bg-gray-100" />
        ))}
      </div>
      {/* Content skeletons */}
      {[1, 2].map((i) => (
        <div key={i} className="rounded-xl border border-gray-200 p-4 space-y-3">
          <div className="h-4 w-32 rounded bg-gray-200" />
          <div className="h-3 w-full rounded bg-gray-100" />
          <div className="h-3 w-3/4 rounded bg-gray-100" />
        </div>
      ))}
    </div>
  );
}

/* ─── Component ─── */

export default function CropDetailContent() {
  const router = useRouter();
  const params = useParams();
  const cropId = params.id as string;

  const { data: cropDetail, isLoading, isError } = useCropDetail(cropId);
  const deleteCrop = useDeleteCrop();

  const emoji = cropDetail ? getCropEmoji(cropDetail.name) : "🌱";

  if (isLoading) {
    return <DetailSkeleton />;
  }

  if (isError || !cropDetail) {
    return (
      <div className="p-4 text-center py-20">
        <span className="text-5xl block mb-4">🌾</span>
        <p className="text-gray-500">
          {isError ? "Failed to load crop details" : "Crop not found"}
        </p>
        <Button onClick={() => router.back()} className="mt-4">
          Go Back
        </Button>
      </div>
    );
  }

  const stages = cropDetail.stages ?? [];
  const tasks = cropDetail.tasks ?? [];
  const expenses = cropDetail.expenses ?? [];
  const diseaseScans = cropDetail.diseaseScans ?? [];

  const totalExpenses = expenses.reduce((sum, e) => sum + e.amount, 0);

  /* ─── Progress calculation ─── */
  let progress = 0;
  if (cropDetail.sowingDate) {
    const sowing = new Date(cropDetail.sowingDate);
    const now = new Date();
    if (cropDetail.expectedHarvestDate) {
      const harvest = new Date(cropDetail.expectedHarvestDate);
      const total = harvest.getTime() - sowing.getTime();
      const elapsed = now.getTime() - sowing.getTime();
      progress = Math.min(100, Math.max(0, Math.round((elapsed / total) * 100)));
    } else {
      progress = Math.min(100, Math.round((cropDetail.daysSinceSowing / 90) * 100));
    }
  }

  // Build spoken crop summary for TTS
  const cropSummaryText = [
    `${cropDetail.name}${cropDetail.variety ? ` (${cropDetail.variety})` : ""}.`,
    `Status: ${STATUS_BADGE[cropDetail.status]?.label || cropDetail.status}.`,
    `${cropDetail.daysSinceSowing} days since sowing.`,
    `Growth progress: ${progress}%.`,
    totalExpenses > 0 ? `Total expenses: ${formatCurrency(totalExpenses)}.` : "",
    tasks.length > 0 ? `${tasks.length} upcoming tasks.` : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className="p-4 space-y-4 pb-8">
      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 min-h-[44px]"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>
        <div className="flex items-center gap-2">
          <TextToSpeech text={cropSummaryText} size="sm" />
          <Button
            variant="outline"
            size="sm"
            onClick={() => toast.info("Edit coming soon!")}
            className="gap-1"
          >
            <Edit3 className="h-4 w-4" />
            <span className="hidden sm:inline">Edit</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={deleteCrop.isPending}
            onClick={() => {
              if (confirm("Delete this crop? This action cannot be undone.")) {
                deleteCrop.mutate(cropId, {
                  onSuccess: () => {
                    toast.success("Crop deleted successfully");
                    router.push("/crops");
                  },
                  onError: (error: Error) => {
                    toast.error(error.message || "Failed to delete crop");
                  },
                });
              }
            }}
            className="gap-1 text-red-500 border-red-200 hover:bg-red-50"
          >
            {deleteCrop.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
            <span className="hidden sm:inline">Delete</span>
          </Button>
        </div>
      </div>

      {/* ── Hero Section ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-gradient-to-br from-mithrava-500 to-mithrava-700 p-6 text-white"
      >
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-4xl">{emoji}</span>
              <div>
                <h1 className="text-2xl font-bold">{cropDetail.name}</h1>
                {cropDetail.variety && (
                  <p className="text-mithrava-200 text-sm">{cropDetail.variety}</p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2 mt-3">
              <Badge
                variant={STATUS_BADGE[cropDetail.status].variant}
                className="text-xs"
              >
                {STATUS_BADGE[cropDetail.status].label}
              </Badge>
              <span className="text-mithrava-200 text-xs">
                {cropDetail.daysSinceSowing} days since sowing
              </span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">{progress}%</p>
            <p className="text-mithrava-200 text-xs">Growth</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="w-full bg-white/20 rounded-full h-2.5">
            <motion.div
              className="bg-white rounded-full h-2.5"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-mithrava-200 text-[10px]">Sowing</span>
            <span className="text-mithrava-200 text-[10px]">Harvest</span>
          </div>
        </div>
      </motion.div>

      {/* ── Quick Actions ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="grid grid-cols-4 gap-2">
          {[
            { icon: <Wallet className="h-5 w-5" />, label: "Log Expense", color: "bg-blue-50 text-blue-600" },
            { icon: <Camera className="h-5 w-5" />, label: "Scan Disease", color: "bg-red-50 text-red-600" },
            { icon: <Cloud className="h-5 w-5" />, label: "Weather", color: "bg-sky-50 text-sky-600" },
            { icon: <Droplets className="h-5 w-5" />, label: "Irrigation", color: "bg-cyan-50 text-cyan-600" },
          ].map((action) => (
            <motion.button
              key={action.label}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => toast.info(`${action.label} coming soon!`)}
              className="flex flex-col items-center gap-1.5 p-3 rounded-xl border border-gray-200 bg-white hover:shadow-sm transition-all"
            >
              <div className={cn("flex h-10 w-10 items-center justify-center rounded-lg", action.color)}>
                {action.icon}
              </div>
              <span className="text-[10px] font-medium text-gray-600">{action.label}</span>
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* ── Crop Calendar / Timeline ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <CropCalendar
          cropName={cropDetail.name}
          emoji={emoji}
          currentStage={cropDetail.currentStage}
          stages={stages}
          tasks={tasks}
        />
      </motion.div>

      {/* ── Upcoming Tasks ── */}
      {tasks.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="border-gray-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                📋 Upcoming Tasks
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {tasks.map((task, index) => (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.05 }}
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
                >
                  <span className="text-lg">{task.emoji}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{task.activity}</p>
                    <p className="text-xs text-gray-400">{formatDate(task.date)}</p>
                  </div>
                  <Badge
                    variant={
                      task.priority === "high"
                        ? "destructive"
                        : task.priority === "medium"
                        ? "warning"
                        : "secondary"
                    }
                    className="text-[9px]"
                  >
                    {task.priority}
                  </Badge>
                </motion.div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* ── Expense History ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="border-gray-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                💰 Expense History
              </CardTitle>
              <span className="text-sm font-semibold text-gray-700">
                {formatCurrency(totalExpenses)}
              </span>
            </div>
          </CardHeader>
          <CardContent>
            {expenses.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">No expenses recorded yet</p>
            ) : (
              <div className="space-y-2">
                {expenses.map((expense) => (
                  <div
                    key={expense.id}
                    className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-lg">{expense.icon}</span>
                      <div>
                        <p className="text-sm font-medium">{expense.category}</p>
                        <p className="text-xs text-gray-400">{formatDate(expense.date)}</p>
                      </div>
                    </div>
                    <span className="text-sm font-semibold text-red-600">
                      -{formatCurrency(expense.amount)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Disease Scan History ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Card className="border-gray-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              🔬 Disease Scan History
            </CardTitle>
          </CardHeader>
          <CardContent>
            {diseaseScans.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">No scans yet</p>
            ) : (
              <div className="space-y-2">
                {diseaseScans.map((scan) => (
                  <div
                    key={scan.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="text-sm font-medium">
                        {scan.diseaseName || "Unknown"}
                      </p>
                      <p className="text-xs text-gray-400">
                        {formatDate(scan.createdAt)} • {scan.confidence}% confidence
                      </p>
                    </div>
                    <Badge
                      variant={
                        scan.severity === "high"
                          ? "destructive"
                          : scan.severity === "medium"
                          ? "warning"
                          : "secondary"
                      }
                      className="text-[10px]"
                    >
                      {scan.severity}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
