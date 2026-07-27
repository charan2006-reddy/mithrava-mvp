"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Cloud,
  TrendingUp,
  Sprout,
  Wallet,
  Mic,
  ChevronRight,
  AlertCircle,
} from "lucide-react";
import { useLanguage } from "@/hooks/useLanguage";
import { useAuth } from "@/hooks/useAuth";
import {
  useFarmerStats,
  useDailyActions,
  useMyCrops,
  useMarketSummary,
} from "@/hooks/useDashboard";
import { NAVIGATION_ITEMS } from "@/lib/constants";

/* ─── Stat Card ─── */

function StatCard({
  label,
  value,
  icon,
  color,
  delay,
}: {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      className="rounded-xl border border-gray-100 bg-white p-4 shadow-sm"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-gray-500">{label}</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`rounded-lg p-2 ${color}`}>{icon}</div>
      </div>
    </motion.div>
  );
}

/* ─── Quick Action Card ─── */

function QuickActionCard({
  emoji,
  label,
  href,
  delay,
}: {
  emoji: string;
  label: string;
  href: string;
  delay: number;
}) {
  return (
    <Link href={href}>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay, duration: 0.2 }}
        whileTap={{ scale: 0.95 }}
        className="flex flex-col items-center gap-2 rounded-xl border border-gray-100 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
      >
        <span className="text-3xl">{emoji}</span>
        <span className="text-xs font-medium text-gray-700">{label}</span>
      </motion.div>
    </Link>
  );
}

/* ─── Loading Skeleton ─── */

function DashboardSkeleton() {
  return (
    <div className="p-4 space-y-6 animate-pulse">
      {/* Greeting skeleton */}
      <div className="space-y-2">
        <div className="h-7 w-48 rounded bg-gray-200" />
        <div className="h-4 w-32 rounded bg-gray-100" />
      </div>

      {/* Stats skeleton */}
      <div className="grid grid-cols-2 gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-xl border border-gray-100 bg-white p-4 space-y-3">
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <div className="h-3 w-16 rounded bg-gray-100" />
                <div className="h-7 w-12 rounded bg-gray-200" />
              </div>
              <div className="h-9 w-9 rounded-lg bg-gray-100" />
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions skeleton */}
      <div className="grid grid-cols-4 gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-xl border border-gray-100 bg-white p-4 space-y-2">
            <div className="mx-auto h-8 w-8 rounded bg-gray-200" />
            <div className="mx-auto h-3 w-12 rounded bg-gray-100" />
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Main Dashboard Page ─── */

export default function DashboardPage() {
  const { t } = useLanguage();
  const { user } = useAuth();

  const { stats, isLoading: statsLoading } = useFarmerStats();
  const { actions, isLoading: actionsLoading } = useDailyActions();
  const { crops, isLoading: cropsLoading } = useMyCrops();
  const { crops: marketPrices, isLoading: marketLoading } = useMarketSummary();

  const isLoading = statsLoading || cropsLoading;

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  const greetingName = user?.name?.split(" ")[0] || "Farmer";

  return (
    <div className="p-4 space-y-6 pb-24">
      {/* ── Greeting ── */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold text-gray-900">
          {t("home.greeting") || "Good morning"}, {greetingName} 🌾
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {t("home.subtitle") || "Here's what's happening on your farm today"}
        </p>
      </motion.div>

      {/* ── Stats Grid ── */}
      <div className="grid grid-cols-2 gap-3">
        <StatCard
          label={t("home.activeCrops") || "Active Crops"}
          value={stats?.activeCrops ?? 0}
          icon={<Sprout className="h-5 w-5 text-green-600" />}
          color="bg-green-50"
          delay={0.05}
        />
        <StatCard
          label={t("home.totalLand") || "Total Land"}
          value={stats ? `${stats.totalLand} ${stats.totalLandUnit}` : "0 acres"}
          icon={<Sprout className="h-5 w-5 text-blue-600" />}
          color="bg-blue-50"
          delay={0.1}
        />
        <StatCard
          label={t("home.monthlyProfit") || "Monthly Profit"}
          value={
            stats
              ? `${stats.isProfit ? "+" : ""}₹${stats.monthlyProfit.toLocaleString("en-IN")}`
              : "₹0"
          }
          icon={<Wallet className="h-5 w-5 text-purple-600" />}
          color="bg-purple-50"
          delay={0.15}
        />
        <StatCard
          label={t("home.readyToHarvest") || "Ready to Harvest"}
          value={stats?.readyToHarvest ?? 0}
          icon={<TrendingUp className="h-5 w-5 text-orange-600" />}
          color="bg-orange-50"
          delay={0.2}
        />
      </div>

      {/* ── Quick Actions ── */}
      <div>
        <h2 className="mb-3 text-sm font-semibold text-gray-700">
          {t("home.quickActions") || "Quick Actions"}
        </h2>
        <div className="grid grid-cols-4 gap-3">
          {NAVIGATION_ITEMS.filter((item) => !item.isCenter).map((item, i) => (
            <QuickActionCard
              key={item.id}
              emoji={item.emoji}
              label={item.label}
              href={item.path}
              delay={0.25 + i * 0.05}
            />
          ))}
        </div>
      </div>

      {/* ── Today's Actions ── */}
      {!actionsLoading && actions && actions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
        >
          <h2 className="mb-3 text-sm font-semibold text-gray-700">
            {t("home.todaysActions") || "Today's Actions"}
          </h2>
          <div className="space-y-2">
            {actions.slice(0, 5).map((action) => (
              <div
                key={action.id}
                className="flex items-center gap-3 rounded-xl border border-gray-100 bg-white p-3 shadow-sm"
              >
                <span className="text-2xl">{action.emoji}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {action.actionText}
                  </p>
                  <p className="text-xs text-gray-500">
                    {action.cropName} • {action.timeOfDay}
                  </p>
                </div>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    action.priority === "high"
                      ? "bg-red-100 text-red-700"
                      : action.priority === "medium"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-green-100 text-green-700"
                  }`}
                >
                  {action.priority}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* ── My Crops Summary ── */}
      {!cropsLoading && crops && crops.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-700">
              {t("home.myCrops") || "My Crops"}
            </h2>
            <Link
              href="/crops"
              className="flex items-center gap-1 text-xs font-medium text-mithrava-600 hover:text-mithrava-700"
            >
              View all <ChevronRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="space-y-2">
            {crops.slice(0, 3).map((crop) => (
              <Link
                key={crop.id}
                href={`/crops/${crop.id}`}
                className="flex items-center gap-3 rounded-xl border border-gray-100 bg-white p-3 shadow-sm transition-shadow hover:shadow-md"
              >
                <span className="text-2xl">🌾</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {crop.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {crop.area} acres • {crop.status}
                  </p>
                </div>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    crop.status === "growing"
                      ? "bg-green-100 text-green-700"
                      : crop.status === "planted"
                      ? "bg-blue-100 text-blue-700"
                      : crop.status === "harvested"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {crop.status}
                </span>
              </Link>
            ))}
          </div>
        </motion.div>
      )}

      {/* ── Market Prices Summary ── */}
      {!marketLoading && marketPrices && marketPrices.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45 }}
        >
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-700">
              {t("home.marketPrices") || "Market Prices"}
            </h2>
            <Link
              href="/market"
              className="flex items-center gap-1 text-xs font-medium text-mithrava-600 hover:text-mithrava-700"
            >
              View all <ChevronRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
            <div className="divide-y divide-gray-50">
              {marketPrices.slice(0, 5).map((price, i) => (
                <div key={i} className="flex items-center gap-3 p-3">
                  <span className="text-lg">💰</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {price.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      ₹{price.current_price.toLocaleString("en-IN")}/{price.unit}
                    </p>
                  </div>
                  {price.msp != null && (
                    <span className="text-xs text-gray-400">
                      MSP: ₹{price.msp.toLocaleString("en-IN")}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* ── Empty state when no data ── */}
      {!statsLoading && !cropsLoading && !actionsLoading && (
        (stats?.activeCrops ?? 0) === 0 && (!crops || crops.length === 0) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="rounded-xl border border-dashed border-gray-300 bg-white p-8 text-center"
          >
            <span className="text-4xl">🌱</span>
            <h3 className="mt-3 text-lg font-semibold text-gray-900">
              Welcome to Mithrava!
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Start by adding your first crop to track your farm.
            </p>
            <Link
              href="/crops/add"
              className="mt-4 inline-flex items-center gap-2 rounded-xl bg-mithrava-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-mithrava-600 transition-colors"
            >
              <Sprout className="h-4 w-4" />
              Add Your First Crop
            </Link>
          </motion.div>
        )
      )}

      {/* ── Mitra Hint ── */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="rounded-xl border border-mithrava-100 bg-mithrava-50 p-4"
      >
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-mithrava-100 p-2">
            <Mic className="h-5 w-5 text-mithrava-600" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-semibold text-mithrava-900">
              {t("home.mitraHintTitle") || "Ask Mitra Anything"}
            </p>
            <p className="mt-0.5 text-xs text-mithrava-600">
              {t("home.mitraHintDesc") || "Tap the chat icon or use voice to ask about weather, crops, market prices, or disease detection."}
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
