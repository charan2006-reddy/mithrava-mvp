"use client";

import { useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, CheckCheck, BellOff, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationService, type Notification } from "@/services/notificationService";
import { NotificationItem } from "@/components/notifications/NotificationItem";

const TABS = [
  { key: "all", label: "All" },
  { key: "weather", label: "🌤️ Weather" },
  { key: "price", label: "💰 Prices" },
  { key: "calendar", label: "📅 Calendar" },
  { key: "system", label: "⚙️ System" },
] as const;

export default function NotificationsPage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<string>("all");
  const [showPushPrompt, setShowPushPrompt] = useState(false);

  // Only show push notification prompt on client after hydration
  useEffect(() => {
    if (typeof window !== "undefined" && "Notification" in window && Notification.permission === "default") {
      setShowPushPrompt(true);
    }
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ["notifications", activeTab],
    queryFn: async () => {
      const typeParam = activeTab === "all" ? undefined : activeTab;
      const res = await notificationService.list(1, 50, typeParam);
      return res.data;
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: () => notificationService.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => notificationService.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const handleNotificationClick = useCallback(
    (notification: Notification) => {
      if (!notification.isRead) {
        markReadMutation.mutate(notification.id);
      }
    },
    [markReadMutation]
  );

  const notifications = data?.notifications ?? [];
  const unreadCount = notifications.filter((n) => !n.isRead).length;

  return (
    <div className="p-4 space-y-4 pb-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="flex h-10 w-10 items-center justify-center rounded-xl hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-xl font-bold">🔔 Notifications</h1>
            {unreadCount > 0 && (
              <p className="text-xs text-gray-500">{unreadCount} unread</p>
            )}
          </div>
        </div>
        {unreadCount > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => markAllReadMutation.mutate()}
            disabled={markAllReadMutation.isPending}
            className="text-xs gap-1"
          >
            <CheckCheck className="h-3.5 w-3.5" />
            Mark all read
          </Button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto pb-1 scrollbar-hide">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-mithrava-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Notification List */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : notifications.length === 0 ? (
        <Card className="border-dashed border-gray-300">
          <CardContent className="p-12 text-center">
            <BellOff className="h-10 w-10 text-gray-300 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-500">No notifications</p>
            <p className="text-xs text-gray-400 mt-1">
              {activeTab === "all"
                ? "Weather alerts, price updates, and reminders will appear here."
                : `No ${activeTab} notifications at the moment.`}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-1">
          {notifications.map((n) => (
            <div key={n.id} className="rounded-xl overflow-hidden bg-white border border-gray-100">
              <NotificationItem
                notification={n}
                onClick={() => handleNotificationClick(n)}
              />
            </div>
          ))}
        </div>
      )}

      {/* Push notification permission CTA — only rendered on client after hydration */}
      {showPushPrompt && (
        <Card className="border-mithrava-200 bg-mithrava-50/50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🔔</span>
              <div className="flex-1">
                <p className="text-sm font-semibold text-mithrava-800">Enable push notifications</p>
                <p className="text-xs text-mithrava-600 mt-1">
                  Get real-time weather alerts, price updates, and calendar reminders even when the app is closed.
                </p>
                <Button
                  size="sm"
                  className="mt-2 text-xs"
                  onClick={async () => {
                    if ("Notification" in window) {
                      await Notification.requestPermission();
                      queryClient.invalidateQueries({ queryKey: ["notifications"] });
                    }
                  }}
                >
                  Enable Notifications
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
