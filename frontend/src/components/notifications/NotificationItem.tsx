"use client";

import { cn } from "@/lib/utils";
import type { Notification } from "@/services/notificationService";

interface NotificationItemProps {
  notification: Notification;
  onClick: () => void;
}

const TYPE_CONFIG: Record<string, { icon: string; color: string }> = {
  weather: { icon: "🌤️", color: "bg-blue-50" },
  price: { icon: "💰", color: "bg-green-50" },
  calendar: { icon: "📅", color: "bg-purple-50" },
  system: { icon: "⚙️", color: "bg-gray-50" },
  info: { icon: "ℹ️", color: "bg-blue-50" },
  warning: { icon: "⚠️", color: "bg-amber-50" },
  success: { icon: "✅", color: "bg-green-50" },
  error: { icon: "❌", color: "bg-red-50" },
};

function formatTimeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60_000);
  const diffHr = Math.floor(diffMs / 3_600_000);
  const diffDay = Math.floor(diffMs / 86_400_000);

  if (diffMin < 1) return "Just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return date.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

export function NotificationItem({ notification, onClick }: NotificationItemProps) {
  const config = TYPE_CONFIG[notification.type] || TYPE_CONFIG.info;

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left px-4 py-3 flex items-start gap-3 transition-colors",
        "hover:bg-gray-50",
        !notification.isRead && "bg-mithrava-50/40"
      )}
    >
      {/* Icon */}
      <div
        className={cn(
          "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-base",
          config.color
        )}
      >
        {config.icon}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p
            className={cn(
              "text-sm leading-tight",
              !notification.isRead ? "font-semibold text-gray-900" : "font-medium text-gray-700"
            )}
          >
            {notification.title}
          </p>
          {!notification.isRead && (
            <span className="h-2 w-2 shrink-0 rounded-full bg-mithrava-500 mt-1.5" />
          )}
        </div>
        <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
          {notification.message}
        </p>
        <p className="text-[10px] text-gray-400 mt-1">
          {formatTimeAgo(notification.createdAt)}
        </p>
      </div>
    </button>
  );
}
