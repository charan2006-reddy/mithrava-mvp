"use client";

import { useQuery } from "@tanstack/react-query";
import { knowledgeService } from "@/services/knowledgeService";

/**
 * Fetches all knowledge base categories.
 * Returns an array of KnowledgeCategory objects.
 */
export function useKnowledgeCategories() {
  return useQuery({
    queryKey: ["knowledge", "categories"],
    queryFn: async () => {
      const res = await knowledgeService.getCategories();
      return res.data ?? [];
    },
  });
}

/**
 * Fetches articles for a specific knowledge category.
 * Only fires when a valid category slug is provided.
 */
export function useKnowledgeArticles(category: string | null) {
  return useQuery({
    queryKey: ["knowledge", "articles", category],
    queryFn: async () => {
      const res = await knowledgeService.getCategoryArticles(category!);
      return res.data ?? [];
    },
    enabled: !!category,
  });
}

/**
 * Fetches a single knowledge article by its ID.
 * Only fires when a valid article ID is provided.
 */
export function useKnowledgeArticle(id: string | null) {
  return useQuery({
    queryKey: ["knowledge", "article", id],
    queryFn: async () => {
      const res = await knowledgeService.getArticle(id!);
      return res.data;
    },
    enabled: !!id,
  });
}
