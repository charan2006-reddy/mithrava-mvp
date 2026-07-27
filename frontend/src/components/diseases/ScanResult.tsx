"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp, Leaf, FlaskConical, Shield, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn, getSeverityConfig } from "@/lib/utils";
import type { DiseaseScanDetail, TreatmentPlan, DiseaseSeverity } from "@/types/disease";

interface ScanResultProps {
  result: DiseaseScanDetail;
  onSave?: () => void;
  onAskMitra?: () => void;
}

/** Circular confidence meter */
function ConfidenceMeter({ confidence, severity }: { confidence: number; severity: DiseaseSeverity }) {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (confidence / 100) * circumference;
  const severityConfig = getSeverityConfig(severity);

  return (
    <div className="relative flex items-center justify-center">
      <svg width="100" height="100" className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="8"
        />
        {/* Progress circle */}
        <motion.circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={severity === "critical" ? "#ef4444" : severity === "high" ? "#f97316" : severity === "medium" ? "#f59e0b" : "#22c55e"}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-xl font-bold text-gray-900">{confidence}%</span>
        <span className="text-[10px] text-gray-500">confidence</span>
      </div>
    </div>
  );
}

/** Expandable treatment section */
interface TreatmentSectionProps {
  icon: React.ReactNode;
  title: string;
  color: string;
  items: string[];
  defaultOpen?: boolean;
}

function TreatmentSection({ icon, title, color, items, defaultOpen = false }: TreatmentSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  if (items.length === 0) return null;

  return (
    <div className={cn("rounded-xl border overflow-hidden", color)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center justify-between w-full px-4 py-3 text-left",
          "hover:bg-opacity-80 transition-colors min-h-[48px]"
        )}
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="font-semibold text-sm">{title}</span>
          <Badge variant="secondary" className="text-[10px]">
            {items.length}
          </Badge>
        </div>
        {isOpen ? (
          <ChevronUp className="h-4 w-4 text-gray-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-gray-500" />
        )}
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <ul className="px-4 pb-3 space-y-2">
              {items.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-mithrava-500 mt-0.5 shrink-0">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function ScanResult({ result, onSave, onAskMitra }: ScanResultProps) {
  const severityConfig = getSeverityConfig(result.severity);
  const isUrgent = result.treatmentPlan?.urgency === "immediate";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Urgency Warning */}
      {isUrgent && (
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-xl p-4"
        >
          <motion.div
            animate={{ scale: [1, 1.15, 1] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
          >
            <AlertTriangle className="h-6 w-6 text-red-600 shrink-0" />
          </motion.div>
          <div>
            <p className="font-semibold text-red-800 text-sm">
              ⚠️ This needs immediate attention!
            </p>
            <p className="text-xs text-red-600 mt-0.5">
              Take action today to save your crop
            </p>
          </div>
        </motion.div>
      )}

      {/* Header Card: Disease Name + Confidence */}
      <Card className={cn("overflow-hidden", severityConfig.border)}>
        <CardContent className="p-5">
          <div className="flex items-center gap-4">
            <ConfidenceMeter
              confidence={result.confidence}
              severity={result.severity}
            />
            <div className="flex-1 min-w-0">
              {result.isHealthy ? (
                <h2 className="text-xl font-bold text-green-700">
                  Healthy Plant 🎉
                </h2>
              ) : (
                <h2
                  className={cn(
                    "text-xl font-bold",
                    result.severity === "critical"
                      ? "text-red-700"
                      : result.severity === "high"
                      ? "text-orange-700"
                      : result.severity === "medium"
                      ? "text-amber-700"
                      : "text-green-700"
                  )}
                >
                  {result.diseaseName}
                </h2>
              )}
              <Badge
                variant="secondary"
                className={cn(
                  "mt-2 text-xs",
                  severityConfig.bg,
                  severityConfig.text,
                  "border-0"
                )}
              >
                {severityConfig.label} Severity
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Before / After images */}
      {(result.beforeImageUrl || result.afterImageUrl) && (
        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="grid grid-cols-2 gap-3">
              {result.beforeImageUrl && (
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-2">📸 Captured</p>
                  <div className="rounded-lg overflow-hidden aspect-square bg-gray-100">
                    <img
                      src={result.beforeImageUrl}
                      alt="Before treatment"
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>
              )}
              {result.afterImageUrl && (
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-2">✅ After Treatment</p>
                  <div className="rounded-lg overflow-hidden aspect-square bg-gray-100">
                    <img
                      src={result.afterImageUrl}
                      alt="After treatment"
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* What We See */}
      {result.description && (
        <Card className="border-gray-200">
          <CardContent className="p-4">
            <h3 className="font-semibold text-sm mb-2">🔍 What We See</h3>
            <p className="text-sm text-gray-700 leading-relaxed">
              {result.description}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Treatment Sections */}
      <div className="space-y-3">
        <h3 className="font-semibold text-sm px-1">💊 Treatment Options</h3>

        <TreatmentSection
          icon={<Leaf className="h-4 w-4 text-green-600" />}
          title="Organic Treatment"
          color="bg-green-50 border-green-200"
          items={result.treatmentPlan?.organic || []}
          defaultOpen={!result.isHealthy}
        />

        <TreatmentSection
          icon={<FlaskConical className="h-4 w-4 text-blue-600" />}
          title="Chemical Treatment"
          color="bg-blue-50 border-blue-200"
          items={result.treatmentPlan?.chemical || []}
        />

        <TreatmentSection
          icon={<Shield className="h-4 w-4 text-purple-600" />}
          title="Prevention"
          color="bg-purple-50 border-purple-200"
          items={result.treatmentPlan?.prevention || []}
        />
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-2">
        {onSave && (
          <Button onClick={onSave} variant="outline" className="flex-1">
            💾 Save to History
          </Button>
        )}
        {onAskMitra && (
          <Button onClick={onAskMitra} className="flex-1">
            🤖 Ask Mitra
          </Button>
        )}
      </div>
    </motion.div>
  );
}
