import api from "./api";
import type { ApiResponse, PaginatedResponse } from "@/types/api";
import type { ForumPost, ForumComment, CreatePostRequest, CreateCommentRequest } from "@/types/forum";

export const forumService = {
  /** List forum posts with optional category filter */
  async list(params?: { category?: string; skip?: number; limit?: number }): Promise<ApiResponse<PaginatedResponse<ForumPost>>> {
    const response = await api.get("/api/v1/forum/", { params });
    return response.data;
  },

  /** Create a new post */
  async create(data: CreatePostRequest): Promise<ApiResponse<ForumPost>> {
    const response = await api.post("/api/v1/forum/", data);
    return response.data;
  },

  /** Add a comment to a post */
  async comment(
    postId: string,
    data: CreateCommentRequest
  ): Promise<ApiResponse<ForumComment>> {
    const response = await api.post(`/api/v1/forum/${postId}/comment`, data);
    return response.data;
  },

  /** Like/unlike a post */
  async like(postId: string): Promise<ApiResponse<{ liked: boolean; likes_count: number }>> {
    const response = await api.post(`/api/v1/forum/${postId}/like`);
    return response.data;
  },

  /** List comments for a post */
  async listComments(
    postId: string,
    params?: { skip?: number; limit?: number }
  ): Promise<ApiResponse<{ comments: any[]; total: number; skip: number; limit: number }>> {
    const response = await api.get(`/api/v1/forum/${postId}/comments`, { params });
    return response.data;
  },
};
