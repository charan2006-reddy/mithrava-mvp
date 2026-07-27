"use client";

import { useMemo, memo, useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Sprout, MapPin, Wheat, TrendingUp, TrendingDown,
  Cloud, Droplets, ChevronRight, Loader2,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { TextToSpeech } from "@/components/voice/TextToSpeech";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { useWeather } from "@/hooks/useWeather";
import {
  useFarmerStats, useDailyActions, useMyCrops, useMarketSummary,
} from "@/hooks/useDashboard";
import { DailyActions } from "@/components/crops/DailyActions";
import { WeatherAlertBanner } from "@/components/weather/WeatherAlertBanner";
import { cn, formatCurrency } from "@/lib/utils";
import { getWeatherEmoji } from "@/types/weather";
import type { DailyAction } from "@/types/crop";
import type { CropPrice } from "@/services/marketService";
import type { Crop } from "@/types/crop";

/* ─── Crop emoji mapping ─── */

const CROP_EMOJI: Record<string, string> = {
  tomato: "🍅", wheat: "🌾", rice: "🍚", cotton: "☁️",
  maize: "🌽", onion: "🧅", potato: "🥔", chilli: "🌶️",
  sugarcane: "🪴", groundnut: "🥜", soybean: "🫘",
};

function getCropEmoji(name: string): string {
  return CROP_EMOJI[name.toLowerCase()] || "🌱";
}

/* ─── Status badge config ─── */

const STATUS_CONFIG: Record<string, { label: string; className: string }> = {
  planted: { label: "Planted", className: "bg-blue-100 text-blue-800" },
  growing: { label: "Growing", className: "bg-green-100 text-green-800" },
  harvested: { label: "Harvested", className: "bg-amber-100 text-green-800" },
  failed: { label: "Failed", className: "bg-red-100 text-red-800" },
};

/* ─── Empty state component ─── */

function EmptyState({ message }: { message: string }) {
  return (
    <Card className="border-dashed border-gray-300">
      <CardContent className="p-6 text-center">
        <Sprout className="h-8 w-8 text-gray-300 mx-auto mb-2" />
        <p className="text-sm text-gray-500">{message}</p>
      </CardContent>
    </Card>
  );
}

/* ─── Loading skeleton ─── */

function DashboardSkeleton() {
  return (
    <div className="p-4 space-y-6 pb-8 animate-pulse">
      <div className="h-32 bg-gray-200 rounded-2xl" />
      <div className="grid grid-cols-2 gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-28 bg-gray-100 rounded-xl" />
        ))}
      </div>
      <div className="h-48 bg-gray-100 rounded-xl" />
      <div className="grid grid-cols-2 gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-36 bg-gray-100 rounded-xl" />
        ))}
      </div>
    </div>
  );
}

/* ─── Component ─── */

export const DashboardHome = memo(function DashboardHome() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const city = user?.city || "Hyderabad";

  // Real API hooks
  const { currentWeather } = useWeather(city);
  const { stats, isLoading: statsLoading } = useFarmerStats();
  const { actions: rawActions, isLoading: actionsLoading } = useDailyActions();
  const { crops, isLoading: cropsLoading } = useMyCrops();
  const { crops: marketCrops, isLoading: marketLoading } = useMarketSummary();

  // Show skeleton while everything loads
  if (statsLoading && actionsLoading && cropsLoading) {
    return <DashboardSkeleton />;
  }

  // Weather data
  const weatherData = currentWeather
    ? {
        temp: Math.round(currentWeather.temperature),
        description: currentWeather.description,
        humidity: currentWeather.humidity,
        icon: getWeatherEmoji(currentWeather.icon),
      }
    : { temp: "—", description: "Loading...", humidity: "—", icon: "🌤️" };

  // Greeting based on time of day
  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return t("dashboard.goodMorning");
    if (hour < 17) return t("dashboard.goodAfternoon");
    return t("dashboard.goodEvening");
  }, [t]);

  // Client-side stable counter for fallback IDs
  const [idCounter] = useState(() => {
    if (typeof window === "undefined") return 0;
    return Date.now();
  });

  // Map daily actions from backend to DailyActions component format
  const dailyActions = useMemo(() => {
    if (!rawActions || !Array.isArray(rawActions)) return [];
    return (rawActions as unknown as Record<string, unknown>[]).map((a, idx: number) => ({
      id: String(a.id || `fallback-${idCounter + idx}`),
      cropId: String(a.crop_id || a.cropId || ""),
      cropName: String(a.crop_name || a.cropName || "Crop"),
      emoji: getCropEmoji(String(a.crop_name || a.cropName || "")),
      actionText: String(a.action_text || a.actionText || a.task || a.action || ""),
      timeOfDay: (a.time_of_day || a.timeOfDay || "morning") as "morning" | "afternoon" | "evening",
      priority: (a.priority || "medium") as "high" | "medium" | "low",
      completed: Boolean(a.completed),
      details: String(a.details || a.advice || ""),
    }));
  }, [rawActions, idCounter]);

  // Local state for optimistic toggle of daily actions
  const [localActions, setLocalActions] = useState<DailyAction[]>(dailyActions);
  useEffect(() => {
    setLocalActions(dailyActions);
  }, [dailyActions]);

  const handleToggleAction = (actionId: string) => {
    setLocalActions?.(
      localActions.map((a) =>
        a.id === actionId ? { ...a, completed: !a.completed } : a
      )
    );
  };

  // Client-side timestamp to avoid hydration mismatch with Date.now()
  const [now] = useState(() => Date.now());

  // Map crops for display
  const displayCrops = useMemo(() => {
    return (crops as unknown as Record<string, unknown>[]).map((crop) => {
      const plantingDate = (crop.sowing_date || crop.planting_date)
        ? new Date(String(crop.sowing_date || crop.planting_date))
        : null;
      const daysOld = plantingDate
        ? Math.floor((now - plantingDate.getTime()) / (1000 * 60 * 60 * 24))
        : 0;
      return {
        id: String(crop.id),
        name: String(crop.name),
        variety: String(crop.variety || "Standard"),
        status: String(crop.status || "growing"),
        daysOld,
        emoji: getCropEmoji(String(crop.name)),
      };
    });
  }, [crops, now]);

  // Map market data
  const marketItems = useMemo(() => {
    return marketCrops.map((crop: CropPrice) => ({
      name: String(crop.name || ""),
      price: Number(crop.current_price || 0),
      msp: crop.msp ? Number(crop.msp) : null,
      mandi: String(crop.mandi || "Mandi"),
    }));
  }, [marketCrops]);

  // Stats cards
  const statsCards = [
    {
      label: t("dashboard.activeCrops"),
      value: stats?.activeCrops ?? 0,
      icon: <Sprout className="h-5 w-5" />,
      color: "bg-mithrava-50 text-mithrava-600",
      href: "/crops",
    },
    {
      label: t("dashboard.totalLand"),
      value: stats?.totalLand ? `${stats.totalLand} ac` : "0 ac",
      icon: <MapPin className="h-5 w-5" />,
      color: "bg-blue-50 text-blue-600",
      href: "/crops",
    },
    {
      label: t("dashboard.readyToHarvest"),
      value: stats?.readyToHarvest ?? 0,
      icon: <Wheat className="h-5 w-5" />,
      color: "bg-amber-50 text-amber-600",
      href: "/crops",
    },
    {
      label: t("dashboard.monthlyProfit"),
      value: formatCurrency(stats?.monthlyProfit ?? 0),
      icon: (stats?.isProfit ?? true)
        ? <TrendingUp className="h-5 w-5" />
        : <TrendingDown className="h-5 w-5" />,
      color: (stats?.isProfit ?? true)
        ? "bg-green-50 text-green-600"
        : "bg-red-50 text-red-600",
      href: "/finance",
    },
  ];

  return (
    <div className="p-4 space-y-6 pb-8">
      {/* ── Welcome Hero Card ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-gradient-to-br from-mithrava-500 via-mithrava-600 to-mithrava-700 p-6 text-white shadow-lg shadow-mithrava-200"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-mithrava-100 text-sm font-medium">{greeting}</p>
            <h1 className="text-2xl font-bold mt-1">
              {user?.name || "Farmer"} 🙏
            </h1>
            <p className="text-mithrava-200 text-sm mt-1 flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              {user?.city || "Hyderabad"}, {user?.state || "Telangana"}
            </p>
          </div>
          {/* Weather summary + TTS */}
          <div className="flex flex-col items-end shrink-0 ml-4 gap-2">
            <TextToSpeech
              text={[
                `${greeting} ${user?.name || "Farmer"}.`,
                `${t("dashboard.activeCrops")}: ${stats?.activeCrops ?? 0}.`,
                `${t("dashboard.totalLand")}: ${stats?.totalLand ?? 0} acres.`,
                `${t("dashboard.readyToHarvest")}: ${stats?.readyToHarvest ?? 0}.`,
                `${t("dashboard.monthlyProfit")}: ${formatCurrency(stats?.monthlyProfit ?? 0)}.`,
                `${t("dashboard.weatherSummary")}: ${weatherData.temp}°C, ${weatherData.description}.`,
              ]
                .filter(Boolean)
                .join(" ")
              }
              size="sm"
              className="text-white/80 hover:text-white hover:bg-white/10"
              ariaLabel="Read daily summary aloud"
            />
            <div className="flex items-center gap-1.5 text-white">
              <span className="text-3xl">{weatherData.icon}</span>
              <span className="text-2xl font-bold">{weatherData.temp}°</span>
            </div>
            <p className="text-mithrava-200 text-xs mt-0.5">{weatherData.description}</p>
            <p className="text-mithrava-200 text-xs flex items-center justify-end gap-1 mt-0.5">
              <Droplets className="h-3 w-3" />
              {weatherData.humidity}%
            </p>
          </div>
        </div>
      </motion.div>

      {/* ── Weather Alert Banner ── */}
      <WeatherAlertBanner city={city} />

      {/* ── Stats Grid (real data) ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {statsCards.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.08 }}
          >
            <Link href={stat.href}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer border-gray-200">
                <CardContent className="p-4">
                  <div
                    className={cn(
                      "flex h-10 w-10 items-center justify-center rounded-xl mb-3",
                      stat.color
                    )}
                  >
                    {stat.icon}
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{stat.label}</p>
                </CardContent>
              </Card>
            </Link>
          </motion.div>
        ))}
      </div>

      {/* ── Daily Actions (real data) ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {actionsLoading ? (
          <Card>
            <CardContent className="p-6 text-center">
              <Loader2 className="h-6 w-6 text-mithrava-500 mx-auto animate-spin mb-2" />
              <p className="text-sm text-gray-500">Loading today's tasks...</p>
            </CardContent>
          </Card>
        ) : localActions.length > 0 ? (
          <DailyActions actions={localActions} onToggle={handleToggleAction} />
        ) : (
          <EmptyState message="No tasks for today. Add crops to see your schedule." />
        )}
      </motion.div>

      {/* ── Quick Crop Cards (real data) ── */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            🌾 {t("nav.crops")}
          </h2>
          <Link
            href="/crops"
            className="text-sm text-mithrava-600 font-medium flex items-center gap-1 hover:underline"
          >
            {t("common.viewAll")}
            <ChevronRight className="h-4 w-4" />
          </Link>
        </div>
        {cropsLoading ? (
          <div className="grid grid-cols-2 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-36 bg-gray-100 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : displayCrops.length > 0 ? (
          <div className="grid grid-cols-2 gap-3">
            {displayCrops.slice(0, 4).map((crop, index) => (
              <motion.div
                key={crop.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.35 + index * 0.05 }}
              >
                <Link href={`/crops/${crop.id}`}>
                  <Card className="hover:shadow-md transition-all duration-200 cursor-pointer border-gray-200 hover:border-mithrava-300">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <motion.span
                          className="text-3xl"
                          whileHover={{ scale: 1.15 }}
                        >
                          {crop.emoji}
                        </motion.span>
                        <span
                          className={cn(
                            "text-[10px] font-medium px-2 py-0.5 rounded-full",
                            STATUS_CONFIG[crop.status]?.className || "bg-gray-100 text-gray-600"
                          )}
                        >
                          {STATUS_CONFIG[crop.status]?.label || crop.status}
                        </span>
                      </div>
                      <p className="font-semibold text-sm">{crop.name}</p>
                      <p className="text-xs text-gray-500">{crop.variety}</p>
                      <p className="text-xs text-mithrava-500 mt-1 font-medium">
                        {crop.daysOld} days old
                      </p>
                    </CardContent>
                  </Card>
                </Link>
              </motion.div>
            ))}
          </div>
        ) : (
          <EmptyState message="No crops yet. Add your first crop to get started!" />
        )}
      </div>

      {/* ── Weather Mini Card ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Link href="/weather">
          <Card className="border-gray-200 hover:shadow-md transition-shadow cursor-pointer overflow-hidden">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50">
                    <Cloud className="h-6 w-6 text-blue-500" />
                  </div>
                  <div>
                    <p className="font-semibold text-sm">Weather Today</p>
                    <p className="text-xs text-gray-500">{weatherData.description} in your area</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-900">{weatherData.temp}°C</p>
                  <p className="text-xs text-gray-500 flex items-center justify-end gap-1">
                    <Droplets className="h-3 w-3" />
                    {weatherData.humidity}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>
      </motion.div>

      {/* ── Market Price Summary (real data) ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.55 }}
      >
        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-sm flex items-center gap-2">
                💰 {t("dashboard.marketSummary")}
              </h3>
              <Link
                href="/market"
                className="text-xs text-mithrava-600 font-medium flex items-center gap-1 hover:underline"
              >
                {t("common.viewAll")}
                <ChevronRight className="h-3 w-3" />
              </Link>
            </div>
            {marketLoading ? (
              <div className="space-y-2">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="h-10 bg-gray-100 rounded animate-pulse" />
                ))}
              </div>
            ) : marketItems.length > 0 ? (
              <div className="space-y-2">
                {marketItems.map((item) => {
                  const isAboveMSP = item.msp ? item.price >= item.msp : null;
                  return (
                    <div
                      key={item.name}
                      className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="text-xl">{getCropEmoji(item.name)}</span>
                        <span className="text-sm font-medium">{item.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold">
                          ₹{item.price.toLocaleString("en-IN")}
                        </span>
                        {item.msp && (
                          <span
                            className={cn(
                              "text-[10px] font-medium px-1.5 py-0.5 rounded-full",
                              isAboveMSP
                                ? "bg-green-100 text-green-700"
                                : "bg-red-100 text-red-700"
                            )}
                          >
                            {isAboveMSP ? "↑" : "↓"} vs MSP
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center py-4">
                No market data available
              </p>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Mitra Greeting ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Link href="/mitra">
          <Card className="bg-gradient-to-r from-mithrava-50 to-mithrava-100 border-mithrava-200 hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-mithrava-500 text-white text-xl shrink-0 shadow-md">
                🤖
              </div>
              <div>
                <p className="font-semibold text-mithrava-800 text-sm">
                  {t("mitra.greeting")}
                </p>
                <p className="text-xs text-mithrava-600 mt-0.5">
                  💡 Ask me anything about your crops, weather, or market prices!
                </p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </motion.div>
    </div>
  );
});
