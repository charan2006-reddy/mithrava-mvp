import api from "./api";
import type { ApiResponse } from "@/types/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Admin dashboard statistics */
export interface AdminStats {
  total_farmers: number;
  total_crops: number;
  active_crops: number;
  disease_scans: number;
  total_vendors: number;
}

/** Farmer list item (admin view) */
export interface AdminFarmer {
  id: string;
  name: string;
  phone: string;
  email: string | null;
  city: string | null;
  state: string | null;
  is_active: boolean;
  is_verified: boolean;
  role: string;
  created_at: string | null;
}

/** Vendor list item (admin view) */
export interface AdminVendor {
  id: string;
  name: string;
  vendor_type: string;
  phone: string;
  city: string;
  rating: number | null;
  is_active: boolean;
  is_verified: boolean;
}

/** Support call request (admin view) */
export interface AdminSupportCall {
  id: string;
  farmer_id: string;
  topic: string;
  description: string;
  preferred_time: string | null;
  status: string;
  created_at: string | null;
}

/** Paginated farmer list response */
export interface FarmerListResponse {
  farmers: AdminFarmer[];
  total: number;
  skip: number;
  limit: number;
}

/** Paginated vendor list response */
export interface VendorListResponse {
  vendors: AdminVendor[];
  total: number;
  skip: number;
  limit: number;
}

/** Support calls list response */
export interface SupportCallsResponse {
  calls: AdminSupportCall[];
  total: number;
  skip: number;
  limit: number;
}

// ---------------------------------------------------------------------------
// Admin service
// ---------------------------------------------------------------------------

export const adminService = {
  /** Get dashboard statistics */
  async getStats(): Promise<ApiResponse<AdminStats>> {
    const response = await api.get("/api/v1/admin/stats");
    return response.data;
  },

  /** List all farmers with pagination */
  async getFarmers(skip = 0, limit = 20): Promise<ApiResponse<FarmerListResponse>> {
    const response = await api.get("/api/v1/admin/farmers", {
      params: { skip, limit },
    });
    return response.data;
  },

  /** Create a new farmer (admin) */
  async createFarmer(data: {
    name: string;
    phone: string;
    email?: string;
    city?: string;
    state?: string;
  }): Promise<ApiResponse<{ id: string; name: string; phone: string; role: string }>> {
    const response = await api.post("/api/v1/admin/farmers", null, { params: data });
    return response.data;
  },

  /** Deactivate a farmer (soft delete) */
  async deleteFarmer(farmerId: string): Promise<ApiResponse<null>> {
    const response = await api.delete(`/api/v1/admin/farmers/${farmerId}`);
    return response.data;
  },

  /** List all vendors with pagination */
  async getVendors(skip = 0, limit = 20): Promise<ApiResponse<VendorListResponse>> {
    const response = await api.get("/api/v1/admin/vendors", {
      params: { skip, limit },
    });
    return response.data;
  },

  /** Create a new vendor (admin) */
  async createVendor(data: {
    name: string;
    vendor_type: string;
    phone: string;
    city: string;
    state?: string;
  }): Promise<ApiResponse<{ id: string; name: string; vendor_type: string }>> {
    const response = await api.post("/api/v1/admin/vendors", null, { params: data });
    return response.data;
  },

  /** Deactivate a vendor (soft delete) */
  async deleteVendor(vendorId: string): Promise<ApiResponse<null>> {
    const response = await api.delete(`/api/v1/admin/vendors/${vendorId}`);
    return response.data;
  },

  /** List all support call requests */
  async getSupportCalls(
    status?: string,
    skip = 0,
    limit = 20
  ): Promise<ApiResponse<SupportCallsResponse>> {
    const params: Record<string, string | number> = { skip, limit };
    if (status) params.call_status = status;
    const response = await api.get("/api/v1/support/calls", { params });
    return response.data;
  },
};
