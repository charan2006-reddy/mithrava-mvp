import api from "./api";
import type { ApiResponse } from "@/types/api";

/** Notification model */
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  notificationType: string;
  isRead: boolean;
  actionUrl?: string;
  createdAt: string;
}

/** Backend list response shape (uses "notifications" not "items") */
export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
}

export const notificationService = {
  /** Get all notifications with optional type filter */
  async list(
    page: number = 1,
    pageSize: number = 20,
    type?: string
  ): Promise<ApiResponse<NotificationListResponse>> {
    const params: Record<string, string | number> = { page, pageSize };
    if (type) params.type = type;

    const response = await api.get("/api/v1/notifications", { params });
    return response.data;
  },

  /** Mark a notification as read */
  async markRead(id: string): Promise<ApiResponse<{ message: string }>> {
    const response = await api.put(`/api/v1/notifications/${id}/read`);
    return response.data;
  },

  /** Mark all notifications as read */
  async markAllRead(): Promise<ApiResponse<{ message: string }>> {
    const response = await api.put("/api/v1/notifications/read-all");
    return response.data;
  },

  /** Get unread count */
  async getUnreadCount(): Promise<ApiResponse<{ count: number }>> {
    const response = await api.get("/api/v1/notifications/unread-count");
    return response.data;
  },

  /** Subscribe to push notifications */
  async subscribePush(subscription: PushSubscription): Promise<ApiResponse<{ message: string }>> {
    const json = subscription.toJSON() as Record<string, unknown>;
    const keys = json?.keys as Record<string, string> | undefined;
    const response = await api.post("/api/v1/notifications/subscribe", {
      endpoint: subscription.endpoint,
      p256dh: keys?.p256dh || "",
      auth: keys?.auth || "",
      user_agent: navigator.userAgent,
    });
    return response.data;
  },

  /** Unsubscribe from push notifications */
  async unsubscribePush(endpoint: string): Promise<ApiResponse<{ message: string }>> {
    const response = await api.delete("/api/v1/notifications/subscribe", {
      params: { endpoint },
    });
    return response.data;
  },
};
