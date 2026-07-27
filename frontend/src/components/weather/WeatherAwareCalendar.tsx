"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CloudRain, Sun, Thermometer, Wind, AlertTriangle, CheckCircle,
  ChevronDown, ChevronUp, Loader2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/hooks/useLanguage";
import api from "@/services/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface WeatherAdjustment {
  type: string;
  icon: string;
  priority: "critical" | "high" | "medium" | "low";
  message: string;
  original_task: string;
  adjusted_task: string;
}

interface WeatherCalendarData {
  calendar: {
    crops: Array<{
      crop_name: string;
      current_stage: string;
      week_number: number;
      tasks: string[];
    }>;
  };
  weather: {
    temperature: number;
    description: string;
    humidity: number;
  };
  forecast: Array<{
    date: string;
    temperature_min: number;
    temperature_max: number;
    description: string;
    rain_chance: number;
  }>;
  adjustments: WeatherAdjustment[];
}

// ---------------------------------------------------------------------------
// Priority styles
// ---------------------------------------------------------------------------

const PRIORITY_STYLES: Record<string, { bg: string; text: string; badge: string }> = {
  critical: {
    bg: "border-red-300 bg-red-50",
    text: "text-red-800",
    badge: "bg-red-100 text-red-700",
  },
  high: {
    bg: "border-amber-300 bg-amber-50",
    text: "text-amber-800",
    badge: "bg-amber-100 text-amber-700",
  },
  medium: {
    bg: "border-blue-200 bg-blue-50",
    text: "text-blue-800",
    badge: "bg-blue-100 text-blue-700",
  },
  low: {
    bg: "border-green-200 bg-green-50",
    text: "text-green-800",
    badge: "bg-green-100 text-green-700",
  },
};

// ---------------------------------------------------------------------------
// Adjustment card
// ---------------------------------------------------------------------------

function AdjustmentCard({ adjustment }: { adjustment: WeatherAdjustment }) {
  const [expanded, setExpanded] = useState(false);
  const styles = PRIORITY_STYLES[adjustment.priority] || PRIORITY_STYLES.medium;

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`rounded-xl border p-3 cursor-pointer transition-all ${styles.bg}`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start gap-3">
        <span className="text-xl shrink-0">{adjustment.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Badge className={`text-[10px] ${styles.badge}`}>
              {adjustment.type.toUpperCase()}
            </Badge>
            <Badge variant="outline" className={`text-[10px] ${styles.badge}`}>
              {adjustment.priority}
            </Badge>
          </div>
          <p className={`text-sm font-medium leading-snug ${styles.text}`}>
            {adjustment.message}
          </p>
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4 shrink-0 text-gray-400" />
        ) : (
          <ChevronDown className="h-4 w-4 shrink-0 text-gray-400" />
        )}
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="mt-3 pt-3 border-t border-gray-200/50 space-y-2">
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider">Original Plan</p>
                <p className="text-xs text-gray-600 line-through">
                  {adjustment.original_task}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider">Weather-Adjusted</p>
                <p className="text-xs font-semibold text-gray-800">
                  → {adjustment.adjusted_task}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface WeatherAwareCalendarProps {
  city: string;
}

export function WeatherAwareCalendar({ city }: WeatherAwareCalendarProps) {
  const { t } = useLanguage();
  const [data, setData] = useState<WeatherCalendarData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWeatherCalendar = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get("/api/v1/crops/weather-calendar", {
        params: { city },
      });
      setData(response.data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load weather calendar");
    } finally {
      setLoading(false);
    }
  };

  if (!data && !loading && !error) {
    return (
      <Card className="border-dashed border-gray-300">
        <CardContent className="p-6 text-center">
          <CloudRain className="h-8 w-8 text-gray-400 mx-auto mb-3" />
          <p className="text-sm font-medium text-gray-600 mb-2">
            Weather-Aware Calendar
          </p>
          <p className="text-xs text-gray-500 mb-3">
            Get weather-adjusted task recommendations for your crops
          </p>
          <Button size="sm" onClick={fetchWeatherCalendar}>
            Load Weather Calendar
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <Loader2 className="h-8 w-8 text-mithrava-500 mx-auto mb-3 animate-spin" />
          <p className="text-sm text-gray-600">Analyzing weather conditions...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-4 text-center">
          <AlertTriangle className="h-6 w-6 text-red-500 mx-auto mb-2" />
          <p className="text-sm text-red-700">{error}</p>
          <Button variant="outline" size="sm" className="mt-2" onClick={fetchWeatherCalendar}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  // data is guaranteed non-null here due to early returns above
  const d = data as WeatherCalendarData;

  return (
    <div className="space-y-3">
      {/* Header with weather summary */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          ⛅ Weather-Aware Calendar
        </h3>
        <Button variant="ghost" size="sm" onClick={fetchWeatherCalendar}>
          🔄
        </Button>
      </div>

      {/* Mini weather strip */}
      {d.forecast && d.forecast.length > 0 && (
        <Card>
          <CardContent className="p-3">
            <div className="flex gap-2 overflow-x-auto">
              {d.forecast.map((day) => (
                <div key={day.date} className="text-center min-w-[60px]">
                  <p className="text-[10px] text-gray-400">
                    {new Date(day.date + "T00:00:00").toLocaleDateString("en-IN", {
                      weekday: "short",
                    })}
                  </p>
                  <p className="text-xs font-medium">
                    {Math.round(day.temperature_max)}° / {Math.round(day.temperature_min)}°
                  </p>
                  {day.rain_chance > 20 && (
                    <p className="text-[10px] text-blue-500">
                      💧{Math.round(day.rain_chance)}%
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Adjustments list */}
      {d.adjustments && d.adjustments.length > 0 && (
        <div className="space-y-2">
          {d.adjustments.map((adj, idx) => (
            <AdjustmentCard key={idx} adjustment={adj} />
          ))}
        </div>
      )}

      {/* No adjustments */}
      {d.adjustments && d.adjustments.length === 0 && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="p-4 flex items-center gap-3">
            <CheckCircle className="h-6 w-6 text-green-500 shrink-0" />
            <div>
              <p className="text-sm font-medium text-green-800">All Clear!</p>
              <p className="text-xs text-green-600">
                Weather conditions are favorable. Proceed with all planned tasks.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
