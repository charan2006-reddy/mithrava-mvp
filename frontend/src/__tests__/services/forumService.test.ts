/**
 * Tests for the forum service — list, create, comment, like, listComments.
 *
 * Strategy:
 * - Mock the axios-based API module to return controlled responses.
 * - Verify each method calls the correct HTTP method + endpoint + params.
 * - Verify return values match what the service exposes.
 */

import { forumService } from "@/services/forumService";

// Mock the API module
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

describe("forumService", () => {
  // ── list ───────────────────────────────────────────────────────────────────

  describe("list", () => {
    it("should call GET /api/v1/forum/ with no params when invoked without arguments", async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            items: [
              { id: "post-1", content: "Hello farmers!", likeCount: 5 },
              { id: "post-2", content: "Weather update", likeCount: 3 },
            ],
            total: 2,
            skip: 0,
            limit: 20,
          },
        },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      const result = await forumService.list();

      expect(mockApi.get).toHaveBeenCalledTimes(1);
      expect(mockApi.get).toHaveBeenCalledWith("/api/v1/forum/", { params: undefined });
      expect(result).toEqual(mockResponse.data);
    });

    it("should pass category param when category filter is provided", async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            items: [{ id: "post-3", content: "Pest issue", category: "pest_control" }],
            total: 1,
            skip: 0,
            limit: 20,
          },
        },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      const result = await forumService.list({ category: "pest_control" });

      expect(mockApi.get).toHaveBeenCalledWith("/api/v1/forum/", {
        params: { category: "pest_control" },
      });
      expect(result).toEqual(mockResponse.data);
    });

    it("should pass skip and limit params for pagination", async () => {
      const mockResponse = {
        data: { success: true, data: { items: [], total: 50, skip: 20, limit: 10 } },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      await forumService.list({ skip: 20, limit: 10 });

      expect(mockApi.get).toHaveBeenCalledWith("/api/v1/forum/", {
        params: { skip: 20, limit: 10 },
      });
    });

    it("should pass combined category, skip, and limit params", async () => {
      const mockResponse = {
        data: { success: true, data: { items: [], total: 0, skip: 5, limit: 5 } },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      await forumService.list({ category: "weather", skip: 5, limit: 5 });

      expect(mockApi.get).toHaveBeenCalledWith("/api/v1/forum/", {
        params: { category: "weather", skip: 5, limit: 5 },
      });
    });
  });

  // ── create ─────────────────────────────────────────────────────────────────

  describe("create", () => {
    it("should call POST /api/v1/forum/ with the post body", async () => {
      const postData = {
        title: "Best fertilizer for rice?",
        content: "I need advice on fertilizer for paddy fields.",
        category: "crop_care",
      };
      const mockResponse = {
        data: {
          success: true,
          data: { id: "new-post-1", ...postData, likeCount: 0, commentCount: 0 },
        },
      };
      mockApi.post.mockResolvedValueOnce(mockResponse);

      const result = await forumService.create(postData);

      expect(mockApi.post).toHaveBeenCalledTimes(1);
      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/forum/", postData);
      expect(result).toEqual(mockResponse.data);
    });

    it("should handle create with optional fields omitted", async () => {
      const postData = { content: "Simple question" };
      const mockResponse = {
        data: { success: true, data: { id: "new-post-2", content: "Simple question" } },
      };
      mockApi.post.mockResolvedValueOnce(mockResponse);

      await forumService.create(postData);

      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/forum/", postData);
    });
  });

  // ── comment ────────────────────────────────────────────────────────────────

  describe("comment", () => {
    it("should call POST /api/v1/forum/{postId}/comment with comment data", async () => {
      const postId = "post-abc-123";
      const commentData = { content: "Great advice, thank you!" };
      const mockResponse = {
        data: {
          success: true,
          data: { id: "comment-1", postId, content: "Great advice, thank you!" },
        },
      };
      mockApi.post.mockResolvedValueOnce(mockResponse);

      const result = await forumService.comment(postId, commentData);

      expect(mockApi.post).toHaveBeenCalledTimes(1);
      expect(mockApi.post).toHaveBeenCalledWith(
        `/api/v1/forum/${postId}/comment`,
        commentData,
      );
      expect(result).toEqual(mockResponse.data);
    });

    it("should handle special characters in postId", async () => {
      const postId = "post/with/slashes";
      const commentData = { content: "Test comment" };
      mockApi.post.mockResolvedValueOnce({ data: { success: true, data: {} } });

      await forumService.comment(postId, commentData);

      expect(mockApi.post).toHaveBeenCalledWith(
        "/api/v1/forum/post/with/slashes/comment",
        commentData,
      );
    });
  });

  // ── like ───────────────────────────────────────────────────────────────────

  describe("like", () => {
    it("should call POST /api/v1/forum/{postId}/like without a body", async () => {
      const postId = "post-like-42";
      const mockResponse = {
        data: {
          success: true,
          data: { liked: true, likes_count: 11 },
        },
      };
      mockApi.post.mockResolvedValueOnce(mockResponse);

      const result = await forumService.like(postId);

      expect(mockApi.post).toHaveBeenCalledTimes(1);
      expect(mockApi.post).toHaveBeenCalledWith(`/api/v1/forum/${postId}/like`);
      expect(result).toEqual(mockResponse.data);
      expect(result.data.liked).toBe(true);
      expect(result.data.likes_count).toBe(11);
    });

    it("should return liked:false when the post is unliked", async () => {
      const postId = "post-unlike-7";
      mockApi.post.mockResolvedValueOnce({
        data: { success: true, data: { liked: false, likes_count: 2 } },
      });

      const result = await forumService.like(postId);

      expect(result.data.liked).toBe(false);
      expect(result.data.likes_count).toBe(2);
    });
  });

  // ── listComments ───────────────────────────────────────────────────────────

  describe("listComments", () => {
    it("should call GET /api/v1/forum/{postId}/comments with no params", async () => {
      const postId = "post-comments-99";
      const mockResponse = {
        data: {
          success: true,
          data: {
            comments: [
              { id: "c1", content: "First comment" },
              { id: "c2", content: "Second comment" },
            ],
            total: 2,
            skip: 0,
            limit: 20,
          },
        },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      const result = await forumService.listComments(postId);

      expect(mockApi.get).toHaveBeenCalledTimes(1);
      expect(mockApi.get).toHaveBeenCalledWith(
        `/api/v1/forum/${postId}/comments`,
        { params: undefined },
      );
      expect(result).toEqual(mockResponse.data);
    });

    it("should pass skip and limit pagination params", async () => {
      const postId = "post-comments-page";
      const mockResponse = {
        data: {
          success: true,
          data: { comments: [], total: 45, skip: 20, limit: 10 },
        },
      };
      mockApi.get.mockResolvedValueOnce(mockResponse);

      await forumService.listComments(postId, { skip: 20, limit: 10 });

      expect(mockApi.get).toHaveBeenCalledWith(
        `/api/v1/forum/${postId}/comments`,
        { params: { skip: 20, limit: 10 } },
      );
    });

    it("should return an empty comments array when total is 0", async () => {
      const postId = "post-no-comments";
      mockApi.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: { comments: [], total: 0, skip: 0, limit: 20 },
        },
      });

      const result = await forumService.listComments(postId);

      expect(result.data.comments).toEqual([]);
      expect(result.data.total).toBe(0);
    });
  });
});
