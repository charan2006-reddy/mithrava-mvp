/**
 * Tests for the vendor service — list, getDetail, addReview.
 *
 * Strategy:
 * - Mock the axios-based API module.
 * - Verify each method calls the correct HTTP method + endpoint + params.
 * - Test with and without optional filters / body fields.
 */

import { vendorService } from "@/services/vendorService";

jest.mock("@/services/api", () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
    delete: jest.fn(),
  },
}));

import api from "@/services/api";
const mockApi = api as jest.Mocked<typeof api>;

beforeEach(() => {
  jest.clearAllMocks();
});

describe("vendorService", () => {
  // ── list ───────────────────────────────────────────────────────────────────

  describe("list", () => {
    it("should call GET /api/v1/vendors with no filters when invoked without arguments", async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            items: [
              { id: "v1", name: "Farm Supply Co", vendor_type: "fertilizer_shop" },
              { id: "v2", name: "Green Seeds", vendor_type: "seed_shop" },
            ],
            total: 2,
            skip: 0,
            limit: 20,
          },
        },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      const result = await vendorService.list();

      expect(mockApi.get).toHaveBeenCalledTimes(1);
      expect(mockApi.get).toHaveBeenCalledWith("/api/v1/vendors", {
        params: { ...undefined, ...undefined },
      });
      expect(result).toEqual(mockResponse.data);
    });

    it("should pass city filter param", async () => {
      const mockResponse = {
        data: {
          success: true,
          data: { items: [{ id: "v3", name: "Hyderabad Agro", city: "Hyderabad" }], total: 1, skip: 0, limit: 20 },
        },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      const result = await vendorService.list({ city: "Hyderabad" });

      expect(mockApi.get).toHaveBeenCalledWith("/api/v1/vendors", {
        params: { city: "Hyderabad" },
      });
      expect(result).toEqual(mockResponse.data);
    });

    it("should pass vendor_type filter param", async () => {
      const mockResponse = {
        data: {
          success: true,
          data: { items: [{ id: "v4", name: "Rent Tractors", vendor_type: "equipment_rental" }], total: 1, skip: 0, limit: 20 },
        },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      await vendorService.list({ vendor_type: "equipment_rental" });

      expect(mockApi.get).toHaveBeenCalledWith("/api/v1/vendors", {
        params: { vendor_type: "equipment_rental" },
      });
    });

    it("should merge filter and pagination params", async () => {
      mockApi.get.mockResolvedValueOnce({
        data: { success: true, data: { items: [], total: 0, skip: 10, limit: 5 } },
      });

      await vendorService.list({ city: "Pune" }, { skip: 10, limit: 5 });

      expect(mockApi.get).toHaveBeenCalledWith("/api/v1/vendors", {
        params: { city: "Pune", skip: 10, limit: 5 },
      });
    });

    it("should return the API response data", async () => {
      const expectedData = {
        success: true,
        data: { items: [], total: 0, skip: 0, limit: 20 },
      };
      mockApi.get.mockResolvedValueOnce({ data: expectedData });

      const result = await vendorService.list();

      expect(result).toEqual(expectedData);
    });
  });

  // ── getDetail ──────────────────────────────────────────────────────────────

  describe("getDetail", () => {
    it("should call GET /api/v1/vendors/{id}", async () => {
      const vendorId = "vendor-xyz-789";
      const mockResponse = {
        data: {
          success: true,
          data: {
            id: vendorId,
            name: "Sunrise Fertilizers",
            vendor_type: "fertilizer_shop",
            city: "Nagpur",
            rating: 4.5,
            review_count: 12,
          },
        },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      const result = await vendorService.getDetail(vendorId);

      expect(mockApi.get).toHaveBeenCalledTimes(1);
      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/vendors/${vendorId}`);
      expect(result).toEqual(mockResponse.data);
      expect(result.data.name).toBe("Sunrise Fertilizers");
    });

    it("should handle vendor with reviews array", async () => {
      const vendorId = "vendor-reviews-1";
      const mockResponse = {
        data: {
          success: true,
          data: {
            id: vendorId,
            name: "Quality Seeds",
            reviews: [
              { id: "r1", rating: 5, comment: "Excellent!" },
              { id: "r2", rating: 4, comment: "Good quality" },
            ],
          },
        },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      const result = await vendorService.getDetail(vendorId);

      expect(result.data.reviews).toHaveLength(2);
    });
  });

  // ── addReview ──────────────────────────────────────────────────────────────

  describe("addReview", () => {
    it("should call POST /api/v1/vendors/{id}/review (singular) with rating and comment", async () => {
      const vendorId = "vendor-review-55";
      const reviewData = { rating: 5, comment: "Best vendor in town!" };
      const mockResponse = {
        data: {
          success: true,
          data: { id: "new-review-1", vendorId, rating: 5, comment: "Best vendor in town!" },
        },
      };
      mockApi.post.mockResolvedValueOnce(mockResponse);

      const result = await vendorService.addReview(vendorId, reviewData);

      expect(mockApi.post).toHaveBeenCalledTimes(1);
      // Verify it's the singular "/review" not "/reviews"
      expect(mockApi.post).toHaveBeenCalledWith(
        `/api/v1/vendors/${vendorId}/review`,
        reviewData,
      );
      expect(result).toEqual(mockResponse.data);
    });

    it("should work when comment is an empty string", async () => {
      const vendorId = "vendor-review-empty";
      const reviewData = { rating: 3, comment: "" };
      mockApi.post.mockResolvedValueOnce({
        data: { success: true, data: { id: "r-empty", rating: 3 } },
      });

      await vendorService.addReview(vendorId, reviewData);

      expect(mockApi.post).toHaveBeenCalledWith(
        `/api/v1/vendors/${vendorId}/review`,
        reviewData,
      );
    });

    it("should handle different rating values", async () => {
      const vendorId = "vendor-rating-check";
      const reviewData = { rating: 1, comment: "Poor service" };
      mockApi.post.mockResolvedValueOnce({
        data: { success: true, data: { id: "r-low", rating: 1 } },
      });

      const result = await vendorService.addReview(vendorId, reviewData);

      expect(mockApi.post).toHaveBeenCalledWith(
        `/api/v1/vendors/${vendorId}/review`,
        { rating: 1, comment: "Poor service" },
      );
      expect(result.data.rating).toBe(1);
    });
  });

  // ── getReviews ─────────────────────────────────────────────────────────────

  describe("getReviews", () => {
    it("should call GET /api/v1/vendors/{id}/reviews", async () => {
      const vendorId = "vendor-rev-list";
      const mockResponse = {
        data: {
          success: true,
          data: {
            items: [
              { id: "r1", rating: 5, comment: "Great!" },
              { id: "r2", rating: 4, comment: "Good" },
            ],
            total: 2,
            skip: 0,
            limit: 20,
          },
        },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      const result = await vendorService.getReviews(vendorId);

      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/vendors/${vendorId}/reviews`, {
        params: undefined,
      });
      expect(result.data.items).toHaveLength(2);
    });

    it("should pass pagination params for reviews", async () => {
      const vendorId = "vendor-rev-page";
      mockApi.get.mockResolvedValueOnce({
        data: { success: true, data: { items: [], total: 50, skip: 10, limit: 10 } },
      });

      await vendorService.getReviews(vendorId, { skip: 10, limit: 10 });

      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/vendors/${vendorId}/reviews`, {
        params: { skip: 10, limit: 10 },
      });
    });
  });
});
