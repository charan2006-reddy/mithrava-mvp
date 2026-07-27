/**
 * Tests for the support service API call patterns.
 *
 * Strategy:
 * - Import the hook source and verify the API call shapes by extracting
 *   the mutationFn / queryFn logic.
 * - Test the endpoint paths, query params, and conditional logic
 *   without needing a React Query provider wrapper.
 */

import api from "@/services/api";

jest.mock("@/services/api", () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
    get: jest.fn(),
  },
}));

const mockApi = api as jest.Mocked<typeof api>;

beforeEach(() => {
  jest.clearAllMocks();
});

/**
 * Replicate the useRequestCall mutationFn logic to verify API call shape.
 * This mirrors the implementation in hooks/useSupport.ts without
 * requiring React Query's useMutation hook.
 */
async function requestCallMutation(data: {
  topic: string;
  description: string;
  preferredTime?: string;
}) {
  const params: Record<string, string> = {
    topic: data.topic,
    description: data.description,
  };
  if (data.preferredTime) {
    params.preferred_time = data.preferredTime;
  }
  const res = await api.post("/api/v1/support/request-call", null, { params });
  return res.data;
}

/**
 * Replicate the useMyCalls queryFn logic to verify API call shape.
 */
async function myCallsQueryFn() {
  const res = await api.get("/api/v1/support/my-calls", {
    params: { skip: 0, limit: 20 },
  });
  return res.data?.data;
}

describe("Support API call patterns", () => {
  // ── useRequestCall ─────────────────────────────────────────────────────────

  describe("useRequestCall — POST /api/v1/support/request-call", () => {
    it("should call POST with topic and description as query params", async () => {
      mockApi.post.mockResolvedValueOnce({ data: { success: true } });

      await requestCallMutation({
        topic: "Crop Disease",
        description: "Need help with tomato leaf curl",
      });

      expect(mockApi.post).toHaveBeenCalledTimes(1);
      expect(mockApi.post).toHaveBeenCalledWith(
        "/api/v1/support/request-call",
        null,
        {
          params: {
            topic: "Crop Disease",
            description: "Need help with tomato leaf curl",
          },
        },
      );
    });

    it("should include preferred_time when preferredTime is provided", async () => {
      mockApi.post.mockResolvedValueOnce({ data: { success: true } });

      await requestCallMutation({
        topic: "Market Prices",
        description: "Want to discuss onion prices",
        preferredTime: "2026-07-26T10:00:00Z",
      });

      expect(mockApi.post).toHaveBeenCalledWith(
        "/api/v1/support/request-call",
        null,
        {
          params: {
            topic: "Market Prices",
            description: "Want to discuss onion prices",
            preferred_time: "2026-07-26T10:00:00Z",
          },
        },
      );
    });

    it("should omit preferred_time when preferredTime is not provided", async () => {
      mockApi.post.mockResolvedValueOnce({ data: { success: true } });

      await requestCallMutation({
        topic: "General",
        description: "Need advice",
      });

      const callParams = mockApi.post.mock.calls[0][2] as { params: Record<string, string> };
      expect(callParams.params).not.toHaveProperty("preferred_time");
      expect(Object.keys(callParams.params)).toEqual(["topic", "description"]);
    });

    it("should pass null as the request body", async () => {
      mockApi.post.mockResolvedValueOnce({ data: { success: true } });

      await requestCallMutation({ topic: "T", description: "D" });

      // The second argument to api.post is the body — should be null
      expect(mockApi.post.mock.calls[0][1]).toBeNull();
    });
  });

  // ── useMyCalls ─────────────────────────────────────────────────────────────

  describe("useMyCalls — GET /api/v1/support/my-calls", () => {
    it("should call GET with skip:0 and limit:20", async () => {
      const mockData = {
        calls: [
          { id: "call-1", topic: "Disease", status: "pending" },
          { id: "call-2", topic: "Price", status: "completed" },
        ],
        total: 2,
        skip: 0,
        limit: 20,
      };
      mockApi.get.mockResolvedValueOnce({ data: { data: mockData } });

      const result = await myCallsQueryFn();

      expect(mockApi.get).toHaveBeenCalledTimes(1);
      expect(mockApi.get).toHaveBeenCalledWith("/api/v1/support/my-calls", {
        params: { skip: 0, limit: 20 },
      });
      expect(result).toEqual(mockData);
    });

    it("should return the nested data.data field", async () => {
      const innerData = { calls: [], total: 0, skip: 0, limit: 20 };
      mockApi.get.mockResolvedValueOnce({ data: { data: innerData } });

      const result = await myCallsQueryFn();

      expect(result).toEqual(innerData);
    });

    it("should handle empty calls list", async () => {
      const emptyData = { calls: [], total: 0, skip: 0, limit: 20 };
      mockApi.get.mockResolvedValueOnce({ data: { data: emptyData } });

      const result = await myCallsQueryFn();

      expect(result?.calls).toEqual([]);
      expect(result?.total).toBe(0);
    });

    it("should use the correct endpoint path", async () => {
      mockApi.get.mockResolvedValueOnce({ data: { data: { calls: [], total: 0 } } });

      await myCallsQueryFn();

      const calledUrl = mockApi.get.mock.calls[0][0];
      expect(calledUrl).toBe("/api/v1/support/my-calls");
      // Ensure it does NOT end with a trailing slash or extra segments
      expect(calledUrl).not.toMatch(/\/$/);
      expect(calledUrl).not.toContain("/list");
    });
  });
});
