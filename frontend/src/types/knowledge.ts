/** Knowledge base category */
export interface KnowledgeCategory {
  id: string;
  name: string;
  nameHi: string;
  description: string;
  icon: string;
  articleCount: number;
}

/** Knowledge base article */
export interface KnowledgeArticle {
  id: string;
  title: string;
  content: string;
  source: "ICAR" | "Mithrava Team" | "Government" | "Research";
  category: string;
  readTimeMinutes: number;
  createdAt: string;
  updatedAt: string;
  tags: string[];
}

/** Search result from semantic search */
export interface KnowledgeSearchResult {
  chunkId: string;
  articleId: string;
  articleTitle: string;
  snippet: string;
  score: number;
  metadata: {
    source: string;
    category: string;
  };
}

/** RAG ask response */
export interface KnowledgeAskResponse {
  answer: string;
  sources: KnowledgeAskSource[];
  confidence: number;
}

/** Source citation from RAG response */
export interface KnowledgeAskSource {
  articleId: string;
  title: string;
  excerpt: string;
  relevance: number;
}

/** Ask feedback request */
export interface AskFeedbackRequest {
  questionId: string;
  helpful: boolean;
}
