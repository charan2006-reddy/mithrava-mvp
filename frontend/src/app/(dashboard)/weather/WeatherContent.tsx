"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Search, Droplets, Wind, Thermometer, CloudRain, RefreshCw,
  AlertTriangle, Sunrise, Sunset, Eye, Gauge, Loader2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TextToSpeech } from "@/components/voice/TextToSpeech";
import { useLanguage } from "@/hooks/useLanguage";
import { useWeather } from "@/hooks/useWeather";
import {
  getWeatherEmoji,
  getWeatherGradient,
  getDayName,
} from "@/types/weather";
import type { WeatherData, ForecastDay, FarmingAdvice } from "@/types/weather";

// ---------------------------------------------------------------------------
// Loading skeleton
// ---------------------------------------------------------------------------

function WeatherSkeleton() {
  return (
    <div className="p-4 space-y-4 animate-pulse">
      <div className="h-8 w-48 bg-gray-200 rounded" />
      <div className="h-10 bg-gray-200 rounded" />
      <Card>
        <CardContent className="p-6">
          <div className="h-32 bg-gray-100 rounded" />
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-7 gap-2">
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="h-24 bg-gray-100 rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4 space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-16 bg-gray-100 rounded" />
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Error state
// ---------------------------------------------------------------------------

function WeatherError({
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
// Current weather card
// ---------------------------------------------------------------------------

function CurrentWeatherCard({ data }: { data: WeatherData }) {
  const { t } = useLanguage();
  const gradient = getWeatherGradient(data.description);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <Card className={`bg-gradient-to-br ${gradient} text-white border-0`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm">{t("weather.currentWeather")}</p>
              <p className="text-4xl font-bold mt-1">{Math.round(data.temperature)}°C</p>
              <p className="text-white/80 text-sm mt-1">
                {t("weather.feelsLike")} {Math.round(data.feelsLike)}°C
              </p>
              <p className="text-lg mt-1 capitalize">{data.description}</p>
            </div>
            <div className="text-6xl">{getWeatherEmoji(data.icon)}</div>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-white/20">
            <div className="text-center">
              <Droplets className="h-5 w-5 mx-auto mb-1 text-white/70" />
              <p className="text-sm font-medium">{data.humidity}%</p>
              <p className="text-xs text-white/70">{t("weather.humidity")}</p>
            </div>
            <div className="text-center">
              <Wind className="h-5 w-5 mx-auto mb-1 text-white/70" />
              <p className="text-sm font-medium">
                {Math.round(data.windSpeed * 3.6)} km/h
              </p>
              <p className="text-xs text-white/70">{t("weather.windSpeed")}</p>
            </div>
            <div className="text-center">
              <Gauge className="h-5 w-5 mx-auto mb-1 text-white/70" />
              <p className="text-sm font-medium">{data.pressure} hPa</p>
              <p className="text-xs text-white/70">Pressure</p>
            </div>
          </div>

          {/* Sunrise / Sunset */}
          <div className="flex justify-between mt-4 pt-3 border-t border-white/20">
            <div className="flex items-center gap-2">
              <Sunrise className="h-4 w-4 text-white/70" />
              <span className="text-xs text-white/80">
                {new Date(data.sunrise).toLocaleTimeString("en-IN", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Sunset className="h-4 w-4 text-white/70" />
              <span className="text-xs text-white/80">
                {new Date(data.sunset).toLocaleTimeString("en-IN", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Weather alerts
// ---------------------------------------------------------------------------

function WeatherAlerts({ alerts }: { alerts: string[] }) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="space-y-2">
      {alerts.map((alert, idx) => (
        <motion.div
          key={idx}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: idx * 0.1 }}
        >
          <Card
            className={
              alert.startsWith("🔴")
                ? "border-red-300 bg-red-50"
                : "border-amber-300 bg-amber-50"
            }
          >
            <CardContent className="p-3">
              <p
                className={`text-sm font-medium ${
                  alert.startsWith("🔴") ? "text-red-800" : "text-amber-800"
                }`}
              >
                {alert}
              </p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// 7-day forecast
// ---------------------------------------------------------------------------

function ForecastSection({ days }: { days: ForecastDay[] }) {
  const { t } = useLanguage();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">📅 {t("weather.forecast")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-2">
          {days.map((day, index) => (
            <motion.div
              key={day.date}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="text-center p-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <p className="text-xs font-medium text-gray-500">
                {getDayName(day.date)}
              </p>
              <p className="text-2xl my-1">{getWeatherEmoji(day.icon)}</p>
              <p className="text-sm font-semibold">{Math.round(day.tempMax)}°</p>
              <p className="text-xs text-gray-400">{Math.round(day.tempMin)}°</p>
              {day.rainChance > 20 && (
                <Badge variant="secondary" className="text-[8px] mt-1">
                  💧{Math.round(day.rainChance)}%
                </Badge>
              )}
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Farming advice
// ---------------------------------------------------------------------------

function FarmingAdviceCard({ advice }: { advice: FarmingAdvice }) {
  const { t } = useLanguage();

  const riskColors: Record<string, string> = {
    low: "border-green-200 bg-green-50",
    medium: "border-amber-200 bg-amber-50",
    high: "border-red-200 bg-red-50",
  };

  return (
    <Card className={riskColors[advice.riskLevel] || "border-amber-200 bg-amber-50"}>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          🌾 {t("weather.farmingAdvice")}
          <Badge
            variant={advice.riskLevel === "high" ? "destructive" : "secondary"}
            className="text-xs"
          >
            {advice.riskLevel === "high"
              ? "⚠️ High Risk"
              : advice.riskLevel === "medium"
              ? "⚡ Medium Risk"
              : "✅ Low Risk"}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
          {advice.advice}
        </p>
      </CardContent>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Main content
// ---------------------------------------------------------------------------

export default function WeatherContent() {
  const { t } = useLanguage();
  const [city, setCity] = useState("Hyderabad");
  const [searchCity, setSearchCity] = useState("Hyderabad");
  const { currentWeather, forecast, advice, isLoading, isError, error } =
    useWeather(city);

  const handleSearch = useCallback(() => {
    const trimmed = searchCity.trim();
    if (trimmed && trimmed !== city) {
      setCity(trimmed);
    }
  }, [searchCity, city]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") handleSearch();
    },
    [handleSearch]
  );

  if (isLoading) return <WeatherSkeleton />;

  if (isError) {
    return (
      <WeatherError
        message={
          error instanceof Error ? error.message : "Failed to load weather data"
        }
        onRetry={() => setCity(city)}
      />
    );
  }

  // Build a spoken weather summary for TTS
  const weatherSummaryText = currentWeather
    ? [
        `${t("weather.title")}: ${city}.`,
        `${t("weather.temperature")}: ${Math.round(currentWeather.temperature)}°C.`,
        `${currentWeather.description}.`,
        `${t("weather.feelsLike")} ${Math.round(currentWeather.feelsLike)}°C.`,
        `${t("weather.humidity")} ${currentWeather.humidity}%.`,
        `${t("weather.windSpeed")} ${Math.round(currentWeather.windSpeed * 3.6)} km/h.`,
        advice ? `${t("weather.farmingAdvice")}: ${advice.advice}` : "",
      ]
        .filter(Boolean)
        .join(" ")
    : "";

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("weather.title")}</h1>
        <div className="flex items-center gap-1">
          {currentWeather && (
            <TextToSpeech text={weatherSummaryText} size="sm" />
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCity(city)}
            disabled={isLoading}
          >
            <RefreshCw
              className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`}
            />
          </Button>
        </div>
      </div>

      {/* City Input */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <Input
            placeholder={t("weather.enterCity")}
            value={searchCity}
            onChange={(e) => setSearchCity(e.target.value)}
            onKeyDown={handleKeyDown}
            className="pl-10"
          />
        </div>
        <Button onClick={handleSearch}>{t("common.search")}</Button>
      </div>

      {/* Weather Alerts */}
      {currentWeather && (
        <WeatherAlerts alerts={currentWeather.alerts} />
      )}

      {/* Current Weather */}
      {currentWeather && <CurrentWeatherCard data={currentWeather} />}

      {/* 7-Day Forecast */}
      {forecast && forecast.days.length > 0 && (
        <ForecastSection days={forecast.days} />
      )}

      {/* Farming Advice */}
      {advice && <FarmingAdviceCard advice={advice} />}
    </div>
  );
}
