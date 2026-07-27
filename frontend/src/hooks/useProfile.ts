"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { farmerService } from "@/services/farmerService";
import type { FarmerProfileUpdate } from "@/types/farmer";

/**
 * Mutation hook to update the current farmer's profile via
 * `PUT /api/v1/farmers/me`.
 *
 * On success the `["farmer", "me"]` query cache is invalidated so any
 * consuming component that fetches the profile will refetch.
 */
export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: FarmerProfileUpdate) => farmerService.updateProfile(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["farmer", "me"] }),
  });
}
