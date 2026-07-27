"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { CropStage } from "@/types/crop";

interface CropStageTimelineProps {
  stages: CropStage[];
  horizontal?: boolean;
  className?: string;
}

export function CropStageTimeline({
  stages,
  horizontal = true,
  className,
}: CropStageTimelineProps) {
  if (stages.length === 0) return null;

  if (horizontal) {
    return (
      <div className={cn("w-full overflow-x-auto pb-2", className)}>
        <div className="flex items-start gap-0 min-w-max">
          {stages.map((stage, index) => {
            const isLast = index === stages.length - 1;
            return (
              <div key={stage.id} className="flex items-start">
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.08 }}
                  className="flex flex-col items-center"
                >
                  {/* Circle / Dot */}
                  <div className="relative">
                    <div
                      className={cn(
                        "w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold border-2 transition-all",
                        stage.completed && "bg-mithrava-500 border-mithrava-500 text-white",
                        stage.current && "bg-white border-mithrava-500 text-mithrava-600 ring-4 ring-mithrava-100",
                        !stage.completed && !stage.current && "bg-gray-50 border-gray-200 text-gray-400"
                      )}
                    >
                      {stage.completed ? (
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        index + 1
                      )}
                    </div>
                    {/* Pulsing indicator for current stage */}
                    {stage.current && (
                      <motion.div
                        className="absolute inset-0 rounded-full border-2 border-mithrava-400"
                        animate={{ scale: [1, 1.3, 1], opacity: [1, 0, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      />
                    )}
                  </div>

                  {/* Label */}
                  <div className="mt-2 text-center max-w-[80px]">
                    <p
                      className={cn(
                        "text-[11px] font-medium leading-tight",
                        stage.current
                          ? "text-mithrava-700"
                          : stage.completed
                          ? "text-gray-700"
                          : "text-gray-400"
                      )}
                    >
                      {stage.name}
                    </p>
                    <p className="text-[9px] text-gray-400 mt-0.5">
                      Week {stage.weekStart}-{stage.weekEnd}
                    </p>
                    {stage.tasksCount > 0 && (
                      <p className="text-[9px] text-gray-400 mt-0.5">
                        {stage.tasksCount} tasks
                      </p>
                    )}
                  </div>
                </motion.div>

                {/* Connector line */}
                {!isLast && (
                  <div className="flex items-center mt-5">
                    <div
                      className={cn(
                        "h-0.5 w-8",
                        stage.completed ? "bg-mithrava-500" : "bg-gray-200"
                      )}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Vertical layout for mobile
  return (
    <div className={cn("relative", className)}>
      {stages.map((stage, index) => {
        const isLast = index === stages.length - 1;
        return (
          <div key={stage.id} className="flex gap-4">
            {/* Vertical line + dot */}
            <div className="flex flex-col items-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="relative"
              >
                <div
                  className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold border-2 shrink-0 z-10",
                    stage.completed && "bg-mithrava-500 border-mithrava-500 text-white",
                    stage.current && "bg-white border-mithrava-500 text-mithrava-600 ring-4 ring-mithrava-100",
                    !stage.completed && !stage.current && "bg-gray-50 border-gray-200 text-gray-400"
                  )}
                >
                  {stage.completed ? "✓" : index + 1}
                </div>
                {stage.current && (
                  <motion.div
                    className="absolute inset-0 rounded-full border-2 border-mithrava-400"
                    animate={{ scale: [1, 1.3, 1], opacity: [1, 0, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                )}
              </motion.div>
              {!isLast && (
                <div
                  className={cn(
                    "w-0.5 flex-1 min-h-[24px]",
                    stage.completed ? "bg-mithrava-500" : "bg-gray-200"
                  )}
                />
              )}
            </div>

            {/* Content */}
            <div className={cn("pb-6", isLast && "pb-0")}>
              <p
                className={cn(
                  "text-sm font-medium",
                  stage.current ? "text-mithrava-700" : stage.completed ? "text-gray-700" : "text-gray-400"
                )}
              >
                {stage.name}
              </p>
              <p className="text-xs text-gray-400 mt-0.5">
                Week {stage.weekStart}-{stage.weekEnd}
                {stage.tasksCount > 0 && ` • ${stage.tasksCount} tasks`}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
