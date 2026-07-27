"use client";

import { useQuery } from "@tanstack/react-query";
import { farmerService } from "@/services/farmerService";
import { cropService } from "@/services/cropService";
import { marketService } from "@/services/marketService";

/**
 * Dashboard stats hook — fetches real data from /api/v1/farmers/me/stats.
 */
export function useFarmerStats() {
  const query = useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: async () => {
      const response = await farmerService.getStats();
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1,
  });

  return {
    stats: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}

/**
 * Daily actions hook — fetches real data from /api/v1/crops/daily-actions.
 */
export function useDailyActions() {
  const query = useQuery({
    queryKey: ["dashboard", "daily-actions"],
    queryFn: async () => {
      const response = await cropService.getDailyActions();
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
  });

  return {
    actions: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}

/**
 * My crops hook — fetches real data from /api/v1/crops.
 */
export function useMyCrops() {
  const query = useQuery({
    queryKey: ["dashboard", "my-crops"],
    queryFn: async () => {
      const response = await cropService.list({ skip: 0, limit: 10 });
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  return {
    crops: query.data?.crops ?? [],
    total: query.data?.total ?? 0,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}

/**
 * Market summary hook — fetches top crop prices for the dashboard widget.
 */
export function useMarketSummary() {
  const query = useQuery({
    queryKey: ["dashboard", "market-summary"],
    queryFn: async () => {
      const response = await marketService.getAllPrices();
      // Return top 5 crops for the dashboard
      return response.data?.crops?.slice(0, 5) ?? [];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  return {
    crops: query.data ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
  };
}
