"use client";

import { cn } from "@/lib/utils";
import { MITRA_QUICK_ACTIONS } from "@/lib/constants";

interface MitraQuickActionsProps {
  onAction: (prompt: string) => void;
}

export function MitraQuickActions({ onAction }: MitraQuickActionsProps) {
  return (
    <div className="space-y-2">
      <p className="text-xs text-gray-500 font-medium px-1">Quick actions</p>
      <div className="flex flex-wrap gap-2">
        {MITRA_QUICK_ACTIONS.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction(action.prompt)}
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-white px-4 py-2.5",
              "text-sm font-medium text-gray-700 hover:bg-mithrava-50 hover:border-mithrava-200 hover:text-mithrava-600",
              "transition-all duration-200 active:scale-95",
              "min-h-[44px]"
            )}
          >
            <span className="text-base">{action.emoji}</span>
            <span>{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
