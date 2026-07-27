import api from "./api";
import type { ApiResponse } from "@/types/api";
import type {
  Crop,
  CropCalendar,
  CreateCropRequest,
  UpdateCropRequest,
  CropCalendarResponse,
  CropDetailResponse,
  DailyAction,
  CropListResponse,
} from "@/types/crop";

export const cropService = {
  /** List all crops for the farmer */
  async list(params?: {
    skip?: number;
    limit?: number;
    search?: string;
  }): Promise<ApiResponse<CropListResponse>> {
    const response = await api.get("/api/v1/crops", { params });
    return response.data;
  },

  /** Create a new crop */
  async create(data: CreateCropRequest): Promise<ApiResponse<Crop>> {
    const response = await api.post("/api/v1/crops", data);
    return response.data;
  },

  /** Update a crop */
  async update(id: string, data: UpdateCropRequest): Promise<ApiResponse<Crop>> {
    const response = await api.put(`/api/v1/crops/${id}`, data);
    return response.data;
  },

  /** Delete a crop */
  async remove(id: string): Promise<ApiResponse<{ message: string }>> {
    const response = await api.delete(`/api/v1/crops/${id}`);
    return response.data;
  },

  /** Get crop calendar */
  async getCalendar(cropId: string): Promise<ApiResponse<CropCalendar[]>> {
    const response = await api.get(`/api/v1/crops/${cropId}/calendar`);
    return response.data;
  },

  /** Get crop by ID */
  async getById(id: string): Promise<ApiResponse<Crop>> {
    const response = await api.get(`/api/v1/crops/${id}`);
    return response.data;
  },

  /** Get all calendars for all crops (dashboard) */
  async getAllCalendars(): Promise<ApiResponse<CropCalendarResponse>> {
    const response = await api.get("/api/v1/crops/calendar");
    return response.data;
  },

  /** Get today's priority actions */
  async getDailyActions(): Promise<ApiResponse<DailyAction[]>> {
    const response = await api.get("/api/v1/crops/daily-actions");
    return response.data;
  },

  /** Get full crop detail — alias for getById (same backend endpoint) */
  async getCropDetail(id: string): Promise<ApiResponse<Crop>> {
    return this.getById(id);
  },
};
