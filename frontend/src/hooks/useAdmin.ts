"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminService } from "@/services/adminService";
import type { AdminStats, AdminFarmer, AdminVendor } from "@/services/adminService";

// ---------------------------------------------------------------------------
// Dashboard Stats
// ---------------------------------------------------------------------------

/** Fetch admin dashboard statistics */
export function useAdminStats() {
  return useQuery({
    queryKey: ["admin", "stats"],
    queryFn: async () => {
      const response = await adminService.getStats();
      return response.data as AdminStats;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  });
}

// ---------------------------------------------------------------------------
// Farmers
// ---------------------------------------------------------------------------

/** Fetch paginated farmer list */
export function useAdminFarmers(skip = 0, limit = 20) {
  return useQuery({
    queryKey: ["admin", "farmers", skip, limit],
    queryFn: async () => {
      const response = await adminService.getFarmers(skip, limit);
      return response.data;
    },
    staleTime: 30 * 1000, // 30 seconds
    retry: 2,
  });
}

/** Create a new farmer (invalidates farmer list) */
export function useCreateAdminFarmer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminService.createFarmer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "farmers"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "stats"] });
    },
  });
}

/** Soft-delete a farmer (invalidates farmer list) */
export function useDeleteAdminFarmer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminService.deleteFarmer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "farmers"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "stats"] });
    },
  });
}

// ---------------------------------------------------------------------------
// Vendors
// ---------------------------------------------------------------------------

/** Fetch paginated vendor list */
export function useAdminVendors(skip = 0, limit = 20) {
  return useQuery({
    queryKey: ["admin", "vendors", skip, limit],
    queryFn: async () => {
      const response = await adminService.getVendors(skip, limit);
      return response.data;
    },
    staleTime: 30 * 1000,
    retry: 2,
  });
}

/** Create a new vendor (invalidates vendor list) */
export function useCreateAdminVendor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminService.createVendor,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "vendors"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "stats"] });
    },
  });
}

/** Soft-delete a vendor (invalidates vendor list) */
export function useDeleteAdminVendor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminService.deleteVendor,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "vendors"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "stats"] });
    },
  });
}

// ---------------------------------------------------------------------------
// Support Calls
// ---------------------------------------------------------------------------

/** Fetch support call requests */
export function useAdminSupportCalls(status?: string) {
  return useQuery({
    queryKey: ["admin", "support-calls", status],
    queryFn: async () => {
      const response = await adminService.getSupportCalls(status);
      return response.data;
    },
    staleTime: 30 * 1000,
    retry: 2,
  });
}
