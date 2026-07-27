import api from "./api";
import type { ApiResponse } from "@/types/api";
import type {
  KnowledgeCategory,
  KnowledgeArticle,
  KnowledgeSearchResult,
  KnowledgeAskResponse,
} from "@/types/knowledge";

export const knowledgeService = {
  /** Get all knowledge base categories */
  async getCategories(): Promise<ApiResponse<KnowledgeCategory[]>> {
    const response = await api.get("/api/v1/knowledge");
    return response.data;
  },

  /** Get articles for a specific category */
  async getCategoryArticles(
    category: string
  ): Promise<ApiResponse<KnowledgeArticle[]>> {
    const response = await api.get(`/api/v1/knowledge/${category}`);
    return response.data;
  },

  /** Get a single article by ID */
  async getArticle(id: string): Promise<ApiResponse<KnowledgeArticle>> {
    const response = await api.get(`/api/v1/knowledge/article/${id}`);
    return response.data;
  },

  /** Semantic search across knowledge base */
  async search(
    query: string,
    category?: string
  ): Promise<ApiResponse<KnowledgeSearchResult[]>> {
    const response = await api.post("/api/v1/knowledge/search", {
      query,
      category,
    });
    return response.data;
  },

  /** Ask a question using RAG (Mitra Knowledge) */
  async ask(
    question: string,
    category?: string
  ): Promise<ApiResponse<KnowledgeAskResponse>> {
    const response = await api.post("/api/v1/knowledge/ask", {
      question,
      category,
    });
    return response.data;
  },
};
