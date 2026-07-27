"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn, formatDateShort } from "@/lib/utils";
import type { CropStage, CropTask } from "@/types/crop";
import { CropStageTimeline } from "./CropStageTimeline";

interface CropCalendarProps {
  cropName: string;
  emoji: string;
  currentStage: string;
  stages: CropStage[];
  tasks: CropTask[];
  className?: string;
}

const PRIORITY_COLORS = {
  high: "bg-red-50 border-red-200 text-red-700",
  medium: "bg-amber-50 border-amber-200 text-amber-700",
  low: "bg-gray-50 border-gray-200 text-gray-600",
};

const PRIORITY_BADGE = {
  high: "destructive" as const,
  medium: "warning" as const,
  low: "secondary" as const,
};

export function CropCalendar({
  cropName,
  emoji,
  currentStage,
  stages,
  tasks,
  className,
}: CropCalendarProps) {
  const upcomingTasks = tasks.filter((t) => !t.completed).slice(0, 5);

  return (
    <Card className={cn("border-gray-200", className)}>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          {emoji} {cropName} Calendar
        </CardTitle>
        <p className="text-xs text-gray-500 mt-1">
          Current stage: <span className="font-medium text-mithrava-600">{currentStage}</span>
        </p>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Stage Timeline */}
        <div>
          <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
            Crop Stages
          </h4>
          {/* Desktop: horizontal */}
          <div className="hidden sm:block">
            <CropStageTimeline stages={stages} horizontal />
          </div>
          {/* Mobile: vertical */}
          <div className="sm:hidden">
            <CropStageTimeline stages={stages} horizontal={false} />
          </div>
        </div>

        {/* Upcoming Tasks */}
        {upcomingTasks.length > 0 && (
          <div>
            <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
              Upcoming Tasks
            </h4>
            <div className="space-y-2">
              {upcomingTasks.map((task, index) => (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={cn(
                    "flex items-center gap-3 rounded-lg border p-3 transition-all",
                    task.completed
                      ? "bg-green-50 border-green-200 opacity-60"
                      : PRIORITY_COLORS[task.priority]
                  )}
                >
                  <span className="text-lg shrink-0">{task.emoji}</span>
                  <div className="flex-1 min-w-0">
                    <p
                      className={cn(
                        "text-sm font-medium leading-tight",
                        task.completed && "line-through text-gray-400"
                      )}
                    >
                      {task.activity}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {formatDateShort(task.date)}
                    </p>
                  </div>
                  <Badge variant={PRIORITY_BADGE[task.priority]} className="text-[9px] shrink-0">
                    {task.priority}
                  </Badge>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
