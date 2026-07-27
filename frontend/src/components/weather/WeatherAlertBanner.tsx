"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle, X, ChevronRight, Droplets, Wind,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useWeather } from "@/hooks/useWeather";
import { getWeatherEmoji } from "@/types/weather";

interface WeatherAlertBannerProps {
  city: string;
  className?: string;
}

/**
 * Compact weather alert banner for the dashboard.
 * Shows alerts, mini forecast, and quick actions.
 */
export function WeatherAlertBanner({ city, className }: WeatherAlertBannerProps) {
  const { currentWeather, forecast, isLoading } = useWeather(city);
  const [dismissed, setDismissed] = useState(false);

  if (isLoading || !currentWeather) return null;
  if (dismissed) return null;

  const hasAlerts = currentWeather.alerts && currentWeather.alerts.length > 0;
  const hasHighRisk = currentWeather.alerts?.some((a) => a.startsWith("🔴"));

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={className}
    >
      {/* Alert alerts */}
      <AnimatePresence>
        {hasAlerts && (
          <Card
            className={`mb-3 ${
              hasHighRisk
                ? "border-red-300 bg-red-50"
                : "border-amber-300 bg-amber-50"
            }`}
          >
            <CardContent className="p-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2 flex-1">
                  <AlertTriangle
                    className={`h-4 w-4 mt-0.5 shrink-0 ${
                      hasHighRisk ? "text-red-500" : "text-amber-500"
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    {currentWeather.alerts.map((alert, idx) => (
                      <p
                        key={idx}
                        className={`text-xs font-medium leading-tight ${
                          hasHighRisk ? "text-red-700" : "text-amber-700"
                        } ${idx > 0 ? "mt-1" : ""}`}
                      >
                        {alert}
                      </p>
                    ))}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 shrink-0"
                  onClick={() => setDismissed(true)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </AnimatePresence>

      {/* Mini weather + forecast */}
      <Link href="/weather">
        <Card className="border-gray-200 hover:shadow-md transition-shadow cursor-pointer">
          <CardContent className="p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{getWeatherEmoji(currentWeather.icon)}</span>
                <div>
                  <p className="text-sm font-semibold">
                    {Math.round(currentWeather.temperature)}°C
                  </p>
                  <p className="text-[10px] text-gray-500 capitalize">
                    {currentWeather.description}
                  </p>
                </div>
              </div>

              {/* Mini 3-day forecast */}
              {forecast && forecast.days.length > 0 && (
                <div className="flex gap-1.5">
                  {forecast.days.slice(0, 3).map((day) => (
                    <div key={day.date} className="text-center">
                      <p className="text-[9px] text-gray-400">
                        {new Date(day.date + "T00:00:00").toLocaleDateString("en-IN", {
                          weekday: "short",
                        })}
                      </p>
                      <p className="text-xs">
                        {getWeatherEmoji(day.icon)}
                      </p>
                      <p className="text-[10px] font-medium">
                        {Math.round(day.tempMax)}°
                      </p>
                    </div>
                  ))}
                </div>
              )}

              <ChevronRight className="h-4 w-4 text-gray-400" />
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}
