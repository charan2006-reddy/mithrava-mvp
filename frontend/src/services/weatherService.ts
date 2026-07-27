import api from "./api";
import type { ApiResponse } from "@/types/api";
import type {
  WeatherData,
  WeatherForecast,
  FarmingAdvice,
  RawWeatherData,
  RawForecastResponse,
  RawFarmingAdviceResponse,
  mapWeatherData,
  mapForecastResponse,
  mapFarmingAdvice,
} from "@/types/weather";

/** Import mapping functions */
import {
  mapWeatherData as _mapWeather,
  mapForecastResponse as _mapForecast,
  mapFarmingAdvice as _mapAdvice,
} from "@/types/weather";

export const weatherService = {
  /** Get current weather for a city */
  async getCurrent(city: string): Promise<ApiResponse<WeatherData>> {
    const response = await api.get(
      `/api/v1/weather/current/${encodeURIComponent(city)}`
    );
    const raw: ApiResponse<RawWeatherData> = response.data;
    return {
      ...raw,
      data: _mapWeather(raw.data),
    };
  },

  /** Get multi-day forecast */
  async getForecast(
    city: string,
    days: number = 7
  ): Promise<ApiResponse<WeatherForecast>> {
    const response = await api.get(
      `/api/v1/weather/forecast/${encodeURIComponent(city)}`,
      { params: { days } }
    );
    const raw: ApiResponse<RawForecastResponse> = response.data;
    return {
      ...raw,
      data: _mapForecast(raw.data),
    };
  },

  /** Get farming advice based on weather */
  async getAdvice(
    city: string,
    cropType?: string
  ): Promise<ApiResponse<FarmingAdvice>> {
    const params: Record<string, string> = { city };
    if (cropType) params.crop_type = cropType;
    const response = await api.get("/api/v1/weather/advice", { params });
    const raw: ApiResponse<RawFarmingAdviceResponse> = response.data;
    return {
      ...raw,
      data: _mapAdvice(raw.data),
    };
  },
};
