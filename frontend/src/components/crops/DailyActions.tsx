"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { DailyAction } from "@/types/crop";

interface DailyActionsProps {
  actions: DailyAction[];
  onToggle?: (actionId: string) => void;
  className?: string;
}

const PRIORITY_CONFIG = {
  high: { label: "High", variant: "destructive" as const, bg: "bg-red-50", border: "border-red-200" },
  medium: { label: "Medium", variant: "warning" as const, bg: "bg-amber-50", border: "border-amber-200" },
  low: { label: "Low", variant: "secondary" as const, bg: "bg-gray-50", border: "border-gray-200" },
};

const TIME_ICONS: Record<string, string> = {
  morning: "🌅",
  afternoon: "☀️",
  evening: "🌙",
};

export function DailyActions({ actions, onToggle, className }: DailyActionsProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const allDone = actions.length > 0 && actions.every((a) => a.completed);
  const completedCount = actions.filter((a) => a.completed).length;

  const handleToggle = useCallback(
    (id: string) => {
      onToggle?.(id);
    },
    [onToggle]
  );

  const handleExpand = useCallback((id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  }, []);

  if (actions.length === 0) {
    return (
      <Card className={cn("border-gray-200", className)}>
        <CardContent className="p-6 text-center">
          <span className="text-4xl block mb-3">🎉</span>
          <p className="text-gray-500 text-sm">No actions for today. Enjoy your day!</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("border-gray-200", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            📋 Today&apos;s Actions
          </CardTitle>
          <span className="text-xs text-gray-400 font-medium">
            {completedCount}/{actions.length} done
          </span>
        </div>
        {/* Progress indicator */}
        <div className="w-full bg-gray-100 rounded-full h-1.5 mt-2">
          <motion.div
            className="bg-mithrava-500 h-1.5 rounded-full"
            initial={{ width: 0 }}
            animate={{
              width: `${(completedCount / actions.length) * 100}%`,
            }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
      </CardHeader>
      <CardContent>
        <AnimatePresence>
          {allDone ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="py-8 text-center"
            >
              <motion.span
                className="text-5xl block mb-3"
                animate={{ rotate: [0, -10, 10, -10, 10, 0] }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                🎊
              </motion.span>
              <p className="text-lg font-semibold text-mithrava-700">All done for today!</p>
              <p className="text-sm text-gray-500 mt-1">Great job keeping up with your farm.</p>
            </motion.div>
          ) : (
            <div className="space-y-2">
              {actions.map((action) => {
                const priority = PRIORITY_CONFIG[action.priority];
                const isExpanded = expandedId === action.id;

                return (
                  <motion.div
                    key={action.id}
                    layout
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                  >
                    <div
                      className={cn(
                        "rounded-lg border transition-all duration-200",
                        action.completed
                          ? "bg-green-50 border-green-200 opacity-60"
                          : `${priority.bg} ${priority.border}`,
                        !action.completed && "hover:shadow-sm cursor-pointer"
                      )}
                    >
                      <div
                        className="flex items-center gap-3 p-3"
                        onClick={() => !action.completed && handleExpand(action.id)}
                      >
                        {/* Checkbox */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleToggle(action.id);
                          }}
                          className={cn(
                            "h-6 w-6 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors",
                            action.completed
                              ? "border-green-500 bg-green-500"
                              : "border-gray-300 hover:border-mithrava-500"
                          )}
                          aria-label={`Mark ${action.actionText} as ${action.completed ? "incomplete" : "complete"}`}
                        >
                          {action.completed && (
                            <svg
                              className="h-3.5 w-3.5 text-white"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={3}
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          )}
                        </button>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-lg shrink-0">{action.emoji}</span>
                            <p
                              className={cn(
                                "text-sm font-medium leading-tight",
                                action.completed && "line-through text-gray-400"
                              )}
                            >
                              {action.actionText}
                            </p>
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-gray-400">
                              {TIME_ICONS[action.timeOfDay] || "⏰"} {action.timeOfDay}
                            </span>
                            <Badge variant={priority.variant} className="text-[9px] px-1.5 py-0">
                              {priority.label}
                            </Badge>
                          </div>
                        </div>

                        {/* Expand arrow */}
                        {!action.completed && (
                          <motion.svg
                            className="h-4 w-4 text-gray-400 shrink-0"
                            animate={{ rotate: isExpanded ? 180 : 0 }}
                            transition={{ duration: 0.2 }}
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 9l-7 7-7-7"
                            />
                          </motion.svg>
                        )}
                      </div>

                      {/* Expanded details */}
                      <AnimatePresence>
                        {isExpanded && !action.completed && action.details && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="overflow-hidden"
                          >
                            <div className="px-3 pb-3 pt-0 ml-9">
                              <p className="text-xs text-gray-600 leading-relaxed">
                                {action.details}
                              </p>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
}
