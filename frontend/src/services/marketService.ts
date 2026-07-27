import api from "./api";
import type { ApiResponse } from "@/types/api";

// ---------------------------------------------------------------------------
// Types matching backend responses
// ---------------------------------------------------------------------------

/** Single crop price data */
export interface CropPrice {
  name: string;
  unit: string;
  current_price: number;
  msp: number | null;
  min_price: number;
  max_price: number;
  mandi: string;
  updated_at: string;
}

/** Price trend data point */
export interface PriceTrendPoint {
  date: string;
  price: number;
}

/** Trend summary */
export interface TrendSummary {
  best_day_to_sell: string;
  weekly_avg: number;
  monthly_avg: number;
}

/** All crops prices response */
export interface AllCropsResponse {
  crops: CropPrice[];
  updated_at: string;
  note: string;
}

/** Single crop response (prices + trend) */
export interface CropDetailResponse {
  crops: CropPrice[];
  trend: PriceTrendPoint[];
  summary: TrendSummary;
  updated_at: string;
  note: string;
}

/** Trend response */
export interface TrendResponse {
  crop: string;
  market: string;
  days: number;
  trend: PriceTrendPoint[];
  summary: TrendSummary;
}

/** Available crop item */
export interface AvailableCrop {
  key: string;
  name: string;
}

// ---------------------------------------------------------------------------
// Market service
// ---------------------------------------------------------------------------

export const marketService = {
  /** Get current prices for all crops */
  async getAllPrices(): Promise<ApiResponse<AllCropsResponse>> {
    const response = await api.get("/api/v1/market/prices");
    return response.data;
  },

  /** Get price data for a specific crop (includes trend + summary) */
  async getCropPrice(crop: string): Promise<ApiResponse<CropDetailResponse>> {
    const response = await api.get("/api/v1/market/prices", {
      params: { crop: crop.toLowerCase() },
    });
    return response.data;
  },

  /** Get price trend for a crop */
  async getPriceTrend(
    crop: string,
    market?: string,
    days: number = 30
  ): Promise<ApiResponse<TrendResponse>> {
    const params: Record<string, string | number> = {
      crop: crop.toLowerCase(),
      days,
    };
    if (market) params.market = market;
    const response = await api.get("/api/v1/market/trend", { params });
    return response.data;
  },

  /** Get all available crops with market data */
  async getAvailableCrops(): Promise<ApiResponse<AvailableCrop[]>> {
    const response = await api.get("/api/v1/market/crops");
    return response.data;
  },

  /** Get all available markets */
  async getMarkets(): Promise<ApiResponse<string[]>> {
    const response = await api.get("/api/v1/market/markets");
    return response.data;
  },
};
