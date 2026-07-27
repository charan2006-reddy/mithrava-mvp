"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/utils";
import type { CropStatus } from "@/types/crop";

/** Crop emoji mapping */
const CROP_EMOJI: Record<string, string> = {
  tomato: "🍅",
  "tomato (paddy)": "🍅",
  wheat: "🌾",
  rice: "🍚",
  "rice (paddy)": "🍚",
  maize: "🌽",
  "maize (corn)": "🌽",
  cotton: "🧶",
  onion: "🧅",
  potato: "🥔",
  chilli: "🌶️",
  turmeric: "🟡",
  ginger: "🫚",
  cardamom: "🫛",
  "black pepper": "⚫",
  coconut: "🥥",
  banana: "🍌",
  mango: "🥭",
  grapes: "🍇",
  pomegranate: "🔴",
  watermelon: "🍉",
  brinjal: "🍆",
  "brinjal (eggplant)": "🍆",
  okra: "🟢",
  "okra (lady finger)": "🟢",
  cabbage: "🥬",
  cauliflower: "🥦",
  carrot: "🥕",
  "green gram": "💚",
  "green gram (moong)": "💚",
  "black gram": "⚫",
  "black gram (urad)": "⚫",
  "bengal gram": "🟤",
  "bengal gram (chana)": "🟤",
  "pigeon pea": "🟠",
  "pigeon pea (toor)": "🟠",
  sugarcane: "🪴",
  groundnut: "🥜",
  soybean: "🫘",
};

/** Get emoji for a crop name */
export function getCropEmoji(cropName: string): string {
  const lower = cropName.toLowerCase();
  if (CROP_EMOJI[lower]) return CROP_EMOJI[lower];
  for (const [key, emoji] of Object.entries(CROP_EMOJI)) {
    if (lower.includes(key)) return emoji;
  }
  return "🌱";
}

/** Status badge color mapping */
const STATUS_CONFIG: Record<
  CropStatus,
  { label: string; variant: "success" | "warning" | "destructive" | "secondary"; dotColor: string }
> = {
  planted: { label: "Planted", variant: "secondary", dotColor: "bg-blue-500" },
  growing: { label: "Growing", variant: "success", dotColor: "bg-green-500" },
  harvested: { label: "Harvest Ready", variant: "warning", dotColor: "bg-amber-500" },
  failed: { label: "Failed", variant: "destructive", dotColor: "bg-red-500" },
};

/** Calculate days since sowing */
function daysSince(dateStr: string): number {
  const sowing = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - sowing.getTime();
  return Math.max(0, Math.floor(diffMs / (1000 * 60 * 60 * 24)));
}

/** Calculate crop lifecycle progress (0-100) */
function calcProgress(sowingDate: string, expectedHarvest?: string): number {
  const sowing = new Date(sowingDate);
  const now = new Date();
  if (expectedHarvest) {
    const harvest = new Date(expectedHarvest);
    const total = harvest.getTime() - sowing.getTime();
    const elapsed = now.getTime() - sowing.getTime();
    return Math.min(100, Math.max(0, Math.round((elapsed / total) * 100)));
  }
  // Estimate based on 90-day lifecycle
  const elapsed = daysSince(sowingDate);
  return Math.min(100, Math.round((elapsed / 90) * 100));
}

interface CropCardProps {
  id: string;
  name: string;
  variety?: string;
  area: number;
  sowingDate: string;
  status: CropStatus;
  expectedHarvestDate?: string;
  nextAction?: string;
  index?: number;
}

export function CropCard({
  id,
  name,
  variety,
  area,
  sowingDate,
  status,
  expectedHarvestDate,
  nextAction,
  index = 0,
}: CropCardProps) {
  const emoji = getCropEmoji(name);
  const daysOld = daysSince(sowingDate);
  const progress = calcProgress(sowingDate, expectedHarvestDate);
  const statusInfo = STATUS_CONFIG[status];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Link href={`/crops/${id}`}>
        <Card className="hover:shadow-md transition-all duration-200 cursor-pointer group border-gray-200 hover:border-mithrava-300">
          <CardContent className="p-4">
            {/* Header: Emoji + Status */}
            <div className="flex items-start justify-between mb-3">
              <motion.span
                className="text-3xl"
                whileHover={{ scale: 1.2 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                {emoji}
              </motion.span>
              <Badge variant={statusInfo.variant} className="text-[10px] px-2 py-0.5">
                <span className={cn("h-1.5 w-1.5 rounded-full mr-1", statusInfo.dotColor)} />
                {statusInfo.label}
              </Badge>
            </div>

            {/* Name & Variety */}
            <h3 className="font-semibold text-base group-hover:text-mithrava-600 transition-colors">
              {name}
            </h3>
            {variety && (
              <p className="text-sm text-gray-500 mt-0.5">{variety}</p>
            )}

            {/* Info Row */}
            <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
              <span className="font-medium">{area} acres</span>
              <span className="flex items-center gap-1">
                <span className="h-1 w-1 rounded-full bg-gray-400" />
                {daysOld} days old
              </span>
            </div>

            {/* Progress Bar */}
            <div className="mt-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-gray-400">Growth</span>
                <span className="text-[10px] font-medium text-mithrava-600">{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>

            {/* Next Action Hint */}
            {nextAction && (status === "planted" || status === "growing") && (
              <div className="mt-3 flex items-center gap-1.5 text-xs text-amber-700 bg-amber-50 rounded-md px-2 py-1.5">
                <span>💡</span>
                <span className="truncate">{nextAction}</span>
              </div>
            )}
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}
