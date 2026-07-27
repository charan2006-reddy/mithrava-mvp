"""Knowledge base API endpoints.

Provides category browsing, article retrieval, semantic search,
and RAG-powered question answering for the agricultural knowledge base.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.farmer import Farmer
from app.models.knowledge import KnowledgeArticle, KnowledgeCategory, KnowledgeChunk
from app.services.rag_service import RAGService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


# ---------------------------------------------------------------------------
# Request schemas (local to this module)
# ---------------------------------------------------------------------------


class KnowledgeSearchRequest(BaseModel):
    """Schema for semantic search request."""

    query: str = Field(..., min_length=2, max_length=500, description="Search query")
    category: str | None = Field(default=None, description="Optional category filter")
    k: int = Field(default=5, ge=1, le=20, description="Number of results")


class KnowledgeAskRequest(BaseModel):
    """Schema for RAG question-answering request."""

    question: str = Field(..., min_length=5, max_length=1000, description="Question to ask")
    category: str | None = Field(default=None, description="Optional category context")


class KnowledgeIngestRequest(BaseModel):
    """Schema for ingesting content into the knowledge base (admin only)."""

    article_id: str = Field(..., description="Article ID to ingest")


class SeedRequest(BaseModel):
    """Schema for seeding the knowledge base (admin only)."""
    pass


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """List all knowledge base categories with article counts.

    Returns categories sorted by name, each with the count of
    published articles.
    """
    result = await db.execute(
        select(
            KnowledgeCategory,
            func.count(KnowledgeArticle.id).label("article_count"),
        )
        .outerjoin(
            KnowledgeArticle,
            (KnowledgeArticle.category_id == KnowledgeCategory.id)
            & (KnowledgeArticle.is_published == True),  # noqa: E712
        )
        .where(KnowledgeCategory.is_active == True)  # noqa: E712
        .group_by(KnowledgeCategory.id)
        .order_by(KnowledgeCategory.name)
    )

    categories = []
    for category, count in result.all():
        categories.append({
            "id": category.id,
            "name": category.name,
            "nameHi": category.name_hi,
            "description": category.description,
            "icon": category.icon,
            "articleCount": count,
        })

    return {"success": True, "data": categories}


@router.get("/{category_slug}")
async def get_category_articles(
    category_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get published articles for a specific category.

    Returns articles sorted by title with excerpt (first 200 chars).
    """
    # Find the category
    cat_result = await db.execute(
        select(KnowledgeCategory).where(
            KnowledgeCategory.name == category_slug,
            KnowledgeCategory.is_active == True,  # noqa: E712
        )
    )
    category = cat_result.scalar_one_or_none()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_slug}' not found.",
        )

    # Get articles
    art_result = await db.execute(
        select(KnowledgeArticle)
        .where(
            KnowledgeArticle.category_id == category.id,
            KnowledgeArticle.is_published == True,  # noqa: E712
        )
        .order_by(KnowledgeArticle.title)
    )
    articles = art_result.scalars().all()

    data = {
        "category": {
            "id": category.id,
            "name": category.name,
            "nameHi": category.name_hi,
            "description": category.description,
            "icon": category.icon,
        },
        "articles": [
            {
                "id": article.id,
                "title": article.title,
                "titleHi": article.title_hi,
                "source": article.source,
                "excerpt": article.content[:200] + "..." if len(article.content) > 200 else article.content,
                "readTimeMinutes": max(1, len(article.content.split()) // 200),
                "createdAt": article.created_at.isoformat() if article.created_at else None,
            }
            for article in articles
        ],
    }

    return {"success": True, "data": data}


@router.get("/article/{article_id}")
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the full content of a knowledge base article."""
    result = await db.execute(
        select(KnowledgeArticle, KnowledgeCategory)
        .join(KnowledgeCategory, KnowledgeCategory.id == KnowledgeArticle.category_id)
        .where(
            KnowledgeArticle.id == article_id,
            KnowledgeArticle.is_published == True,  # noqa: E712
        )
    )
    row = result.first()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found.",
        )

    article, category = row

    data = {
        "id": article.id,
        "title": article.title,
        "titleHi": article.title_hi,
        "content": article.content,
        "source": article.source,
        "category": category.name,
        "categoryIcon": category.icon,
        "readTimeMinutes": max(1, len(article.content.split()) // 200),
        "createdAt": article.created_at.isoformat() if article.created_at else None,
        "updatedAt": article.updated_at.isoformat() if article.updated_at else None,
    }

    return {"success": True, "data": data}


@router.post("/search")
async def search_knowledge(
    request: KnowledgeSearchRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: Farmer = Depends(get_current_user),
):
    """Semantic search across the knowledge base.

    Uses pgvector cosine similarity to find the most relevant
    knowledge chunks matching the query.
    """
    results = await RAGService.search(
        db, request.query, k=request.k, category=request.category
    )

    data = [
        {
            "chunkId": r["chunk_id"],
            "articleId": r["article_id"],
            "articleTitle": r["article_title"],
            "snippet": r["content"][:300] + "..." if len(r["content"]) > 300 else r["content"],
            "score": r["score"],
            "metadata": r.get("metadata", {}),
        }
        for r in results
    ]

    return {"success": True, "data": data}


@router.post("/ask")
async def ask_knowledge(
    request: KnowledgeAskRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: Farmer = Depends(get_current_user),
):
    """Ask a question and get a RAG-powered answer.

    Searches the knowledge base for relevant chunks, then generates
    an answer using Ollama (with OpenAI fallback) grounded in the
    retrieved context.
    """
    result = await RAGService.rag_query(
        db, request.question, category=request.category
    )

    return {"success": True, "data": result}


@router.post("/ingest/{article_id}")
async def ingest_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: Farmer = Depends(get_current_user),
):
    """Ingest an article into the RAG vector store.

    Splits the article content into chunks, generates embeddings,
    and stores them for semantic search.
    """
    # Fetch the article
    result = await db.execute(
        select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
    )
    article = result.scalar_one_or_none()

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found.",
        )

    # Get category name for metadata
    cat_result = await db.execute(
        select(KnowledgeCategory.name).where(KnowledgeCategory.id == article.category_id)
    )
    cat_name = cat_result.scalar() or "unknown"

    chunks = await RAGService.ingest_article_full(
        db,
        article_id=article.id,
        content=article.content,
        title=article.title,
        category=cat_name,
        source=article.source,
    )

    await db.commit()

    return {
        "success": True,
        "message": f"Ingested {chunks} chunks for article '{article.title}'",
        "data": {"chunks_created": chunks},
    }


@router.post("/seed")
async def seed_knowledge_base(
    db: AsyncSession = Depends(get_db),
    _current_user: Farmer = Depends(get_current_user),
):
    """Seed the knowledge base with initial agricultural content.

    Creates categories and articles covering common farming topics.
    Skips existing entries. Requires authentication.
    """
    result = await RAGService.seed_knowledge_base(db)

    return {
        "success": True,
        "message": (
            f"Seeded {result['categories']} categories, "
            f"{result['articles']} articles, {result['chunks']} chunks"
        ),
        "data": result,
    }
