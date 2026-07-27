"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, Minus,
  RefreshCw, AlertTriangle, Loader2, BarChart3, Store,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { TextToSpeech } from "@/components/voice/TextToSpeech";
import { useLanguage } from "@/hooks/useLanguage";
import { useMarket } from "@/hooks/useMarket";
import { formatCurrency } from "@/lib/utils";
import type { CropPrice, PriceTrendPoint, TrendSummary } from "@/services/marketService";

// ---------------------------------------------------------------------------
// Market overview skeleton
// ---------------------------------------------------------------------------

function MarketSkeleton() {
  return (
    <div className="p-4 space-y-4 animate-pulse">
      <div className="h-8 w-48 bg-gray-200 rounded" />
      <div className="h-10 bg-gray-200 rounded" />
      <Card>
        <CardContent className="p-6">
          <div className="h-28 bg-gray-100 rounded" />
        </CardContent>
      </Card>
      <div className="grid grid-cols-2 gap-4">
        <div className="h-24 bg-gray-100 rounded" />
        <div className="h-24 bg-gray-100 rounded" />
      </div>
      <div className="h-64 bg-gray-100 rounded" />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Error state
// ---------------------------------------------------------------------------

function MarketError({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  const { t } = useLanguage();
  return (
    <div className="p-4 space-y-4">
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-6 text-center space-y-3">
          <AlertTriangle className="h-10 w-10 text-red-500 mx-auto" />
          <p className="font-semibold text-red-700">{t("common.error")}</p>
          <p className="text-sm text-red-600">{message}</p>
          <Button variant="outline" onClick={onRetry} size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            {t("common.retry")}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Price bar chart (pure CSS, no chart library)
// ---------------------------------------------------------------------------

function PriceTrendChart({
  trend,
  label,
}: {
  trend: PriceTrendPoint[];
  label: string;
}) {
  if (!trend || trend.length === 0) return null;

  const prices = trend.map((p) => p.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const range = maxPrice - minPrice || 1;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <BarChart3 className="h-4 w-4" />
          📈 {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-48 flex items-end gap-[2px]">
          {trend.map((point, i) => {
            const heightPct = ((point.price - minPrice) / range) * 80 + 20;
            return (
              <motion.div
                key={i}
                initial={{ height: 0 }}
                animate={{ height: `${heightPct}%` }}
                transition={{ delay: i * 0.03, duration: 0.4 }}
                className="flex-1 bg-gradient-to-t from-mithrava-500 to-mithrava-400 rounded-t relative group cursor-pointer min-w-0"
                title={`${point.date}: ₹${point.price}`}
              >
                <div className="absolute -top-7 left-1/2 -translate-x-1/2 text-[10px] font-medium bg-gray-800 text-white px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                  ₹{point.price}
                </div>
              </motion.div>
            );
          })}
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span>{trend[0]?.date}</span>
          <span>{trend[trend.length - 1]?.date}</span>
        </div>
      </CardContent>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Crop price card
// ---------------------------------------------------------------------------

function CropPriceCard({ crop }: { crop: CropPrice }) {
  const isAboveMSP = crop.msp ? crop.current_price >= crop.msp : null;
  const priceChange = crop.current_price - (crop.msp || crop.current_price);
  const changePct = crop.msp
    ? ((crop.current_price - crop.msp) / crop.msp) * 100
    : 0;

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Current Price</p>
            <div className="flex items-end gap-2 mt-1">
              <span className="text-2xl font-bold">
                {formatCurrency(crop.current_price)}
              </span>
              {crop.msp && (
                <Badge
                  variant={isAboveMSP ? "success" : "destructive"}
                  className="mb-0.5"
                >
                  {isAboveMSP ? (
                    <ArrowUpRight className="h-3 w-3 mr-0.5" />
                  ) : (
                    <ArrowDownRight className="h-3 w-3 mr-0.5" />
                  )}
                  {isAboveMSP ? "+" : ""}
                  {changePct.toFixed(1)}% vs MSP
                </Badge>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1">per {crop.unit}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-400">Mandi</p>
            <p className="text-sm font-medium">{crop.mandi}</p>
          </div>
        </div>

        {/* MSP comparison bar */}
        {crop.msp && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>MSP: {formatCurrency(crop.msp)}</span>
              <span>Range: {formatCurrency(crop.min_price)} - {formatCurrency(crop.max_price)}</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  isAboveMSP ? "bg-green-500" : "bg-red-400"
                }`}
                style={{
                  width: `${Math.min(
                    100,
                    ((crop.current_price - crop.min_price) /
                      (crop.max_price - crop.min_price)) *
                      100
                  )}%`,
                }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Main content
// ---------------------------------------------------------------------------

export default function MarketContent() {
  const { t } = useLanguage();
  const [selectedCrop, setSelectedCrop] = useState("tomato");
  const {
    allCrops,
    cropDetail,
    availableCrops,
    isLoading,
    isError,
    error,
  } = useMarket(selectedCrop);

  const trend = cropDetail?.trend;
  const summary: TrendSummary | undefined = cropDetail?.summary;
  const currentCropData = cropDetail?.crops?.[0];

  if (isLoading) return <MarketSkeleton />;

  if (isError) {
    return (
      <MarketError
        message={
          error instanceof Error ? error.message : "Failed to load market data"
        }
        onRetry={() => setSelectedCrop(selectedCrop)}
      />
    );
  }

  // Build spoken market summary for TTS
  const marketSummaryText = [
    `${t("market.title")}:`,
    currentCropData
      ? `${currentCropData.name}: ${formatCurrency(currentCropData.current_price)} per ${currentCropData.unit}.`
      : "",
    summary
      ? `${t("market.weeklyAvg")}: ${formatCurrency(summary.weekly_avg)}. ${t("market.monthlyAvg")}: ${formatCurrency(summary.monthly_avg)}.`
      : "",
    summary
      ? `${t("market.bestDayToSell")}: ${summary.best_day_to_sell}.`
      : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("market.title")}</h1>
        <div className="flex items-center gap-1">
          <TextToSpeech text={marketSummaryText} size="sm" />
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedCrop(selectedCrop)}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Crop Selector */}
      <Select value={selectedCrop} onValueChange={setSelectedCrop}>
        <SelectTrigger>
          <SelectValue placeholder={t("market.selectCrop")} />
        </SelectTrigger>
        <SelectContent>
          {availableCrops?.map((crop) => (
            <SelectItem key={crop.key} value={crop.key}>
              {crop.name}
            </SelectItem>
          )) ||
            // Fallback if availableCrops hasn't loaded yet
            ["tomato", "rice", "wheat", "cotton", "chilli", "groundnut", "soybean", "maize", "onion", "potato"].map(
              (key) => (
                <SelectItem key={key} value={key}>
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                </SelectItem>
              )
            )}
        </SelectContent>
      </Select>

      {/* Current Price */}
      {currentCropData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <CropPriceCard crop={currentCropData} />
        </motion.div>
      )}

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-2 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-sm text-gray-500">{t("market.weeklyAvg")}</p>
              <p className="text-xl font-bold mt-1">
                {formatCurrency(summary.weekly_avg)}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-sm text-gray-500">{t("market.monthlyAvg")}</p>
              <p className="text-xl font-bold mt-1">
                {formatCurrency(summary.monthly_avg)}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Best Day to Sell */}
      {summary && (
        <Card className="bg-mithrava-50 border-mithrava-200">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-mithrava-500 text-white flex items-center justify-center text-xl shrink-0">
              💡
            </div>
            <div>
              <p className="font-semibold text-mithrava-800">
                {t("market.bestDayToSell")}
              </p>
              <p className="text-sm text-mithrava-600">
                Based on historical data,{" "}
                <strong>{summary.best_day_to_sell}</strong> is usually the best
                day to sell.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Price Trend Chart */}
      {trend && trend.length > 0 && (
        <PriceTrendChart
          trend={trend}
          label={`${currentCropData?.name || selectedCrop} — 30 Days`}
        />
      )}

      {/* All Crops Overview */}
      {allCrops?.crops && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Store className="h-4 w-4" />
              All Crop Prices
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {allCrops.crops.map((crop) => (
              <div
                key={crop.name}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => {
                  const key = crop.name
                    .toLowerCase()
                    .replace(/[^a-z]/g, "")
                    .replace("paddy", "")
                    .replace("corn", "");
                  // Map display name to key
                  const keyMap: Record<string, string> = {
                    "rice (paddy)": "rice",
                    "wheat": "wheat",
                    "cotton": "cotton",
                    "red chilli": "chilli",
                    "tomato": "tomato",
                    "groundnut": "groundnut",
                    "soybean": "soybean",
                    "maize (corn)": "maize",
                    "onion": "onion",
                    "potato": "potato",
                  };
                  const cropKey = keyMap[crop.name.toLowerCase()] || key;
                  setSelectedCrop(cropKey);
                }}
              >
                <div>
                  <p className="text-sm font-medium">{crop.name}</p>
                  <p className="text-xs text-gray-500">{crop.mandi}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold">
                    {formatCurrency(crop.current_price)}
                  </p>
                  {crop.msp && (
                    <p
                      className={`text-xs ${
                        crop.current_price >= crop.msp
                          ? "text-green-600"
                          : "text-red-500"
                      }`}
                    >
                      MSP: {formatCurrency(crop.msp)}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Disclaimer */}
      <p className="text-xs text-gray-400 text-center">
        Prices are indicative. Actual mandi prices may vary. Data refreshed
        periodically.
      </p>
    </div>
  );
}
