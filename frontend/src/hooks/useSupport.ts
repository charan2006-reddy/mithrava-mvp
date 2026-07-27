"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import api from "@/services/api";

/** Shape of a single support call returned by the API */
export interface SupportCallItem {
  id: string;
  topic: string;
  description: string;
  preferred_time: string | null;
  status: string;
  admin_notes: string | null;
  created_at: string | null;
}

/** Response shape from GET /my-calls */
export interface MyCallsResponse {
  calls: SupportCallItem[];
  total: number;
  skip: number;
  limit: number;
}

/**
 * Mutation hook to submit a callback-request to the support endpoint.
 *
 * The backend expects `topic` and `description` as query params
 * on `POST /api/v1/support/request-call`.
 */
export function useRequestCall() {
  return useMutation({
    mutationFn: async (data: { topic: string; description: string; preferredTime?: string }) => {
      const params: Record<string, string> = {
        topic: data.topic,
        description: data.description,
      };
      if (data.preferredTime) {
        params.preferred_time = data.preferredTime;
      }
      const res = await api.post("/api/v1/support/request-call", null, { params });
      return res.data;
    },
  });
}

/** Fetch the current farmer's own support calls */
export function useMyCalls() {
  return useQuery<MyCallsResponse>({
    queryKey: ["support", "my-calls"],
    queryFn: async () => {
      const res = await api.get("/api/v1/support/my-calls", {
        params: { skip: 0, limit: 20 },
      });
      return res.data?.data;
    },
  });
}
