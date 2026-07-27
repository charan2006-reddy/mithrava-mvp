"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getSeverityConfig, timeAgo } from "@/lib/utils";
import type { ScanHistoryItem } from "@/types/disease";

interface ScanHistoryCardProps {
  scan: ScanHistoryItem;
  index?: number;
}

export function ScanHistoryCard({ scan, index = 0 }: ScanHistoryCardProps) {
  const severityConfig = scan.severity ? getSeverityConfig(scan.severity) : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Link href={`/diseases/scan?id=${scan.id}`}>
        <Card className="hover:shadow-md transition-all duration-200 cursor-pointer group border-gray-200 hover:border-mithrava-300">
          <CardContent className="p-3 flex items-center gap-3">
            {/* Thumbnail */}
            <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-lg bg-gray-100">
              {scan.imageUrl ? (
                <img
                  src={scan.imageUrl}
                  alt={scan.diseaseName}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center text-2xl">
                  {scan.isHealthy ? "🌿" : "🔬"}
                </div>
              )}
              {/* Severity dot indicator */}
              {severityConfig && (
                <div
                  className={`absolute top-1 right-1 h-2.5 w-2.5 rounded-full ring-2 ring-white ${severityConfig.bg.replace(
                    "100",
                    "500"
                  )}`}
                />
              )}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="font-semibold text-sm truncate group-hover:text-mithrava-600 transition-colors">
                  {scan.isHealthy ? (
                    <span className="text-green-700">Healthy ✅</span>
                  ) : (
                    scan.diseaseName
                  )}
                </p>
              </div>
              <p className="text-xs text-gray-500 mt-0.5">
                {scan.cropName && (
                  <span>{scan.cropName} • </span>
                )}
                {timeAgo(scan.analyzedAt)}
              </p>
            </div>

            {/* Right side: confidence + severity badge */}
            <div className="flex flex-col items-end gap-1 shrink-0">
              <span className="text-sm font-bold text-gray-700">
                {scan.confidence}%
              </span>
              {severityConfig && (
                <Badge
                  variant="secondary"
                  className={`text-[10px] px-1.5 py-0.5 ${severityConfig.bg} ${severityConfig.text} border-0`}
                >
                  {severityConfig.label}
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}
