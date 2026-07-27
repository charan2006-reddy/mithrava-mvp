"use client";

import { useRouter } from "next/navigation";
import { CheckCheck, BellOff, ChevronRight } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationService, type Notification, type NotificationListResponse } from "@/services/notificationService";
import { NotificationItem } from "./NotificationItem";
import type { ApiResponse } from "@/types/api";

interface NotificationPanelProps {
  onClose: () => void;
  onMarkAllRead: () => void;
}

export function NotificationPanel({ onClose, onMarkAllRead }: NotificationPanelProps) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: async () => {
      const res = await notificationService.list(1, 20);
      return res.data;
    },
  });

  const notifications = data?.notifications ?? [];

  const handleViewAll = () => {
    onClose();
    router.push("/notifications");
  };

  const handleNotificationClick = (notification: Notification) => {
    // Mark as read
    queryClient.invalidateQueries({ queryKey: ["notifications"] });
    // Navigate if action_url exists
    if (notification.actionUrl) {
      onClose();
      router.push(notification.actionUrl);
    }
  };

  return (
    <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 overflow-hidden animate-in slide-in-from-top-2 fade-in duration-200">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Notifications</h3>
          {data && data.total > 0 && (
            <p className="text-xs text-gray-500">{data.total} total</p>
          )}
        </div>
        <button
          onClick={onMarkAllRead}
          className="text-xs text-mithrava-600 font-medium hover:text-mithrava-700 flex items-center gap-1"
        >
          <CheckCheck className="h-3.5 w-3.5" />
          Mark all read
        </button>
      </div>

      {/* Notification list */}
      <div className="max-h-80 overflow-y-auto">
        {isLoading ? (
          <div className="p-6 text-center">
            <div className="h-5 w-5 border-2 border-mithrava-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs text-gray-500 mt-2">Loading...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="p-8 text-center">
            <BellOff className="h-8 w-8 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">No notifications yet</p>
            <p className="text-xs text-gray-400 mt-1">
              Weather alerts, price updates, and reminders will appear here
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {notifications.slice(0, 8).map((n) => (
              <NotificationItem
                key={n.id}
                notification={n}
                onClick={() => handleNotificationClick(n)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {notifications.length > 0 && (
        <button
          onClick={handleViewAll}
          className="w-full px-4 py-3 text-center text-sm font-medium text-mithrava-600 hover:bg-mithrava-50 border-t border-gray-100 flex items-center justify-center gap-1"
        >
          View all notifications
          <ChevronRight className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}
