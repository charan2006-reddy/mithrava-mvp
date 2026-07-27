import api from "./api";
import type { ApiResponse, PaginatedResponse, PaginationParams } from "@/types/api";
import type { Vendor, VendorReview, VendorFilter, AddReviewRequest } from "@/types/vendor";

export const vendorService = {
  /** List vendors with filters */
  async list(
    filter?: VendorFilter,
    params?: PaginationParams
  ): Promise<ApiResponse<PaginatedResponse<Vendor>>> {
    const response = await api.get("/api/v1/vendors", { params: { ...filter, ...params } });
    return response.data;
  },

  /** Get vendor detail */
  async getDetail(id: string): Promise<ApiResponse<Vendor>> {
    const response = await api.get(`/api/v1/vendors/${id}`);
    return response.data;
  },

  /** Get vendor reviews */
  async getReviews(
    vendorId: string,
    params?: PaginationParams
  ): Promise<ApiResponse<PaginatedResponse<VendorReview>>> {
    const response = await api.get(`/api/v1/vendors/${vendorId}/reviews`, { params });
    return response.data;
  },

  /** Add a review for a vendor */
  async addReview(
    vendorId: string,
    data: AddReviewRequest
  ): Promise<ApiResponse<VendorReview>> {
    const response = await api.post(`/api/v1/vendors/${vendorId}/review`, data);
    return response.data;
  },
};
