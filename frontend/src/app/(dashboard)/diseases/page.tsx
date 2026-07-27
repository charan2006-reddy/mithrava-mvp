"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Camera } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ScanHistoryCard } from "@/components/diseases/ScanHistoryCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { ListSkeleton } from "@/components/shared/LoadingSkeleton";
import { useDiseaseHistory } from "@/hooks/useDisease";
import { cn } from "@/lib/utils";
import type { ScanHistoryItem } from "@/types/disease";

type FilterType = "all" | "healthy" | "diseased";

const FILTER_OPTIONS: { value: FilterType; label: string }[] = [
  { value: "all", label: "All" },
  { value: "healthy", label: "Healthy ✅" },
  { value: "diseased", label: "Diseased 🔬" },
];

export default function DiseasesPage() {
  const router = useRouter();
  const { data: historyData, isLoading, isError } = useDiseaseHistory(1, 20);
  const [activeFilter, setActiveFilter] = useState<FilterType>("all");

  const scans: ScanHistoryItem[] = historyData?.items ?? [];

  /** Filter scans based on active filter */
  const filteredScans = scans.filter((scan) => {
    if (activeFilter === "all") return true;
    if (activeFilter === "healthy") return scan.isHealthy;
    if (activeFilter === "diseased") return !scan.isHealthy;
    return true;
  });

  return (
    <div className="p-4 space-y-6 pb-8">
      {/* ── Hero Section ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-gradient-to-br from-mithrava-500 via-mithrava-600 to-mithrava-700 p-6 text-white shadow-lg shadow-mithrava-200"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              Plant Doctor 🩺
            </h1>
            <p className="text-mithrava-100 text-sm mt-1">
              Take a photo of your plant. We&apos;ll tell you what&apos;s wrong and how to fix it.
            </p>
          </div>
          <span className="text-4xl">🌿</span>
        </div>

        {/* Scan Now Button */}
        <Link href="/diseases/scan">
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="mt-4"
          >
            <Button
              className="w-full h-14 bg-white text-mithrava-600 hover:bg-mithrava-50 font-bold text-base shadow-lg gap-2"
            >
              <Camera className="h-6 w-6" />
              Scan Now
            </Button>
          </motion.div>
        </Link>
      </motion.div>

      {/* ── Filter Tabs ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1"
      >
        {FILTER_OPTIONS.map((filter) => (
          <button
            key={filter.value}
            onClick={() => setActiveFilter(filter.value)}
            className={cn(
              "px-4 py-2.5 rounded-full text-sm font-medium whitespace-nowrap transition-all min-h-[40px]",
              activeFilter === filter.value
                ? "bg-mithrava-500 text-white shadow-md"
                : "bg-white text-gray-600 border border-gray-200 hover:border-mithrava-300"
            )}
          >
            {filter.label}
          </button>
        ))}
      </motion.div>

      {/* ── Recent Scans Section ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
      >
        <h2 className="text-lg font-semibold mb-3">📋 Recent Scans</h2>

        {isLoading ? (
          <ListSkeleton items={4} />
        ) : isError || filteredScans.length === 0 ? (
          <EmptyState
            icon={<span className="text-3xl">🩺</span>}
            title="No scans yet"
            description="Scan your first plant to get started. Just take a photo and we'll tell you what's happening."
            actionLabel="Scan First Plant"
            onAction={() => router.push("/diseases/scan")}
          />
        ) : (
          <div className="space-y-3">
            {filteredScans.slice(0, 6).map((scan, index) => (
              <ScanHistoryCard key={scan.id} scan={scan} index={index} />
            ))}
          </div>
        )}
      </motion.div>

      {/* ── Quick Tips ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
      >
        <Card className="border-amber-200 bg-amber-50/50">
          <CardContent className="p-4">
            <h3 className="font-semibold text-sm mb-2">💡 Quick Tips</h3>
            <ul className="space-y-1.5">
              <li className="text-xs text-gray-600 flex items-start gap-2">
                <span className="text-mithrava-500">•</span>
                Take photos in good daylight for best results
              </li>
              <li className="text-xs text-gray-600 flex items-start gap-2">
                <span className="text-mithrava-500">•</span>
                Focus on the affected leaves or stem
              </li>
              <li className="text-xs text-gray-600 flex items-start gap-2">
                <span className="text-mithrava-500">•</span>
                Our AI can detect 50+ common crop diseases
              </li>
            </ul>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
