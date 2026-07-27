"use client";

import { useQuery } from "@tanstack/react-query";
import { weatherService } from "@/services/weatherService";

/**
 * Hook for fetching weather data via React Query.
 * Returns current weather, forecast, and farming advice for a city.
 */
export function useWeather(city: string) {
  /** Current weather query */
  const currentWeather = useQuery({
    queryKey: ["weather", "current", city],
    queryFn: async () => {
      const response = await weatherService.getCurrent(city);
      return response.data;
    },
    enabled: !!city,
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  });

  /** Forecast query */
  const forecast = useQuery({
    queryKey: ["weather", "forecast", city],
    queryFn: async () => {
      const response = await weatherService.getForecast(city, 7);
      return response.data;
    },
    enabled: !!city,
    staleTime: 30 * 60 * 1000, // 30 minutes
    retry: 2,
  });

  /** Farming advice query */
  const advice = useQuery({
    queryKey: ["weather", "advice", city],
    queryFn: async () => {
      const response = await weatherService.getAdvice(city);
      return response.data;
    },
    enabled: !!city,
    staleTime: 30 * 60 * 1000,
    retry: 2,
  });

  return {
    currentWeather: currentWeather.data,
    forecast: forecast.data,
    advice: advice.data,
    isLoading: currentWeather.isLoading || forecast.isLoading,
    isError: currentWeather.isError || forecast.isError,
    error: currentWeather.error || forecast.error,
  };
}
