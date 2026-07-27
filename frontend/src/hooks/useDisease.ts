"use client";

import { useQuery } from "@tanstack/react-query";
import { diseaseService } from "@/services/diseaseService";

/**
 * Fetches paginated disease scan history.
 * Defaults to page 1, 20 items per page.
 */
export function useDiseaseHistory(page = 1, limit = 20) {
  return useQuery({
    queryKey: ["disease", "history", page, limit],
    queryFn: async () => {
      const res = await diseaseService.getScanHistory(page, limit);
      return res.data;
    },
  });
}

/**
 * Fetches full disease scan detail by ID.
 * Only fires when a valid scan ID is provided.
 */
export function useDiseaseDetail(id: string | null) {
  return useQuery({
    queryKey: ["disease", "detail", id],
    queryFn: async () => {
      const res = await diseaseService.getScanDetail(id!);
      return res.data;
    },
    enabled: !!id,
  });
}
