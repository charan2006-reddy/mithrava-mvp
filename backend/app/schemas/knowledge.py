"""Knowledge base schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------


class KnowledgeCategoryResponse(BaseModel):
    """Knowledge base category with article count."""

    id: str
    name: str
    nameHi: str
    description: str
    icon: str
    articleCount: int = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Article
# ---------------------------------------------------------------------------


class KnowledgeArticleBrief(BaseModel):
    """Simplified article for listing pages."""

    id: str
    title: str
    titleHi: Optional[str] = None
    source: str
    excerpt: str
    readTimeMinutes: int = 1
    createdAt: Optional[str] = None

    model_config = {"from_attributes": True}


class KnowledgeArticleFull(BaseModel):
    """Full article with content."""

    id: str
    title: str
    titleHi: Optional[str] = None
    content: str
    source: str
    category: str
    categoryIcon: str = "📚"
    readTimeMinutes: int = 1
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class KnowledgeSearchRequest(BaseModel):
    """Semantic search request."""

    query: str = Field(..., min_length=2, max_length=500)
    category: Optional[str] = Field(default=None)
    k: int = Field(default=5, ge=1, le=20)


class KnowledgeSearchResult(BaseModel):
    """Single search result chunk."""

    chunkId: str
    articleId: str
    articleTitle: str
    snippet: str
    score: float = Field(ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# RAG Q&A
# ---------------------------------------------------------------------------


class KnowledgeAskRequest(BaseModel):
    """RAG question-answering request."""

    question: str = Field(..., min_length=5, max_length=1000)
    category: Optional[str] = Field(default=None)


class KnowledgeAskSource(BaseModel):
    """Source citation from a RAG answer."""

    articleId: str
    title: str
    excerpt: str
    relevance: float = Field(ge=0.0, le=1.0)


class KnowledgeAskResponse(BaseModel):
    """RAG-generated answer with sources."""

    answer: str
    sources: list[KnowledgeAskSource] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------


class KnowledgeIngestRequest(BaseModel):
    """Request to re-ingest an article into the vector store."""

    articleId: str


class KnowledgeSeedResponse(BaseModel):
    """Response from knowledge base seeding."""

    categories: int = 0
    articles: int = 0
    chunks: int = 0
