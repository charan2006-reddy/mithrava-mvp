"use client";

import { useQuery } from "@tanstack/react-query";
import { marketService } from "@/services/marketService";

/**
 * Hook for fetching market price data via React Query.
 * Returns current prices, trends, and summary for selected crop.
 */
export function useMarket(crop: string | null) {
  /** All crops overview */
  const allCrops = useQuery({
    queryKey: ["market", "all-crops"],
    queryFn: async () => {
      const response = await marketService.getAllPrices();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });

  /** Specific crop detail (price + trend + summary) */
  const cropDetail = useQuery({
    queryKey: ["market", "crop", crop],
    queryFn: async () => {
      const response = await marketService.getCropPrice(crop!);
      return response.data;
    },
    enabled: !!crop,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });

  /** Available crop list */
  const availableCrops = useQuery({
    queryKey: ["market", "available-crops"],
    queryFn: async () => {
      const response = await marketService.getAvailableCrops();
      return response.data;
    },
    staleTime: 60 * 60 * 1000, // 1 hour (rarely changes)
    retry: 1,
  });

  return {
    allCrops: allCrops.data,
    cropDetail: cropDetail.data,
    availableCrops: availableCrops.data,
    isLoading: allCrops.isLoading || cropDetail.isLoading,
    isError: allCrops.isError || cropDetail.isError,
    error: allCrops.error || cropDetail.error,
  };
}
