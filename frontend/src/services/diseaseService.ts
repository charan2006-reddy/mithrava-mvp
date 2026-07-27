import api from "./api";
import type { ApiResponse, PaginatedResponse } from "@/types/api";
import type {
  DiseaseScan,
  DiseaseResult,
  DiseaseScanDetail,
  ScanHistoryItem,
} from "@/types/disease";

export const diseaseService = {
  /** Upload and analyze a crop image for disease detection */
  async analyze(file: File, cropId?: string): Promise<ApiResponse<DiseaseScanDetail>> {
    const formData = new FormData();
    formData.append("file", file);
    if (cropId) formData.append("crop_id", cropId);
    const response = await api.post("/api/v1/disease/analyze", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  /** Scan a specific crop's image (alias for analyze) */
  async scanImage(file: File, cropId?: string): Promise<ApiResponse<DiseaseScanDetail>> {
    const formData = new FormData();
    formData.append("file", file);
    if (cropId) formData.append("crop_id", cropId);
    const response = await api.post("/api/v1/disease/analyze", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  /** Get scan history */
  async getScanHistory(
    page: number = 1,
    pageSize: number = 20
  ): Promise<ApiResponse<PaginatedResponse<ScanHistoryItem>>> {
    const response = await api.get("/api/v1/disease/history", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  /** Get full scan detail by ID */
  async getScanDetail(id: string): Promise<ApiResponse<DiseaseScanDetail>> {
    const response = await api.get(`/api/v1/disease/${id}`);
    return response.data;
  },

  /** Get scan by ID (legacy alias) */
  async getScanById(id: string): Promise<ApiResponse<DiseaseScan>> {
    const response = await api.get(`/api/v1/disease/${id}`);
    return response.data;
  },

  /** Delete a scan */
  async deleteScan(id: string): Promise<ApiResponse<{ message: string }>> {
    const response = await api.delete(`/api/v1/disease/${id}`);
    return response.data;
  },

  /** Get paginated scan history (legacy alias) */
  async getHistory(
    page: number = 1,
    pageSize: number = 20
  ): Promise<ApiResponse<PaginatedResponse<DiseaseScan>>> {
    const response = await api.get("/api/v1/disease/history", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
};
