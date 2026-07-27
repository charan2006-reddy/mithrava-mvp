import api from "./api";
import type { ApiResponse } from "@/types/api";
import type { FarmerProfile, FarmerProfileUpdate, FarmerStats } from "@/types/farmer";

export const farmerService = {
  /** Get current user's profile */
  async getProfile(): Promise<ApiResponse<FarmerProfile>> {
    const response = await api.get("/api/v1/farmers/me");
    return response.data;
  },

  /** Update profile */
  async updateProfile(data: FarmerProfileUpdate): Promise<ApiResponse<FarmerProfile>> {
    const response = await api.put("/api/v1/farmers/me", data);
    return response.data;
  },

  /** Upload avatar image */
  async uploadAvatar(file: File): Promise<ApiResponse<{ avatarUrl: string }>> {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.put("/api/v1/farmers/me/avatar", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  /** Get dashboard statistics */
  async getStats(): Promise<ApiResponse<FarmerStats>> {
    const response = await api.get("/api/v1/farmers/me/stats");
    return response.data;
  },
};
