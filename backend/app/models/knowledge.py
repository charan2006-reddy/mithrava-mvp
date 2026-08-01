"""
Knowledge & Document Embedding Models — RAG knowledge base.

Stores agricultural articles organized by categories, and their chunked
vector embeddings for retrieval-augmented generation (RAG). The embedding
dimension (1536) matches OpenAI text-embedding-3-small.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.database import Base


# ---------------------------------------------------------------------------
# Knowledge Category
# ---------------------------------------------------------------------------


class KnowledgeCategory(Base):
    """Categories for organizing agricultural knowledge articles.

    Examples: crop_guides, diseases, government_schemes, fertilizers, weather.
    """

    __tablename__ = "knowledge_categories"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="Category slug"
    )
    name_hi: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Hindi name of the category"
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Short description of the category"
    )
    icon: Mapped[str] = mapped_column(
        String(10), nullable=False, default="📚", comment="Emoji icon"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # ── Relationships ──────────────────────────────────────────────────
    articles: Mapped[List["KnowledgeArticle"]] = relationship(
        "KnowledgeArticle",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<KnowledgeCategory(id={self.id}, name={self.name!r})>"


# ---------------------------------------------------------------------------
# Knowledge Article
# ---------------------------------------------------------------------------


class KnowledgeArticle(Base):
    """Full agricultural knowledge articles linked to a category.

    Each article contains a title, full text content, source attribution,
    and language tag for multi-language support.
    """

    __tablename__ = "knowledge_articles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_categories.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    title_hi: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="Hindi title"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(
        String(200), nullable=False, default="Mithrava Team",
        comment="Source attribution: Mithrava Team, ICAR, Government, etc."
    )
    language: Mapped[str] = mapped_column(
        String(10), nullable=False, default="en",
        comment="ISO 639-1 language code"
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # ── Relationships ──────────────────────────────────────────────────
    category: Mapped["KnowledgeCategory"] = relationship(
        "KnowledgeCategory", back_populates="articles"
    )
    chunks: Mapped[List["KnowledgeChunk"]] = relationship(
        "KnowledgeChunk",
        back_populates="article",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    __table_args__ = (
        Index("ix_knowledge_articles_lang", "language"),
        Index("ix_knowledge_articles_published", "is_published"),
    )

    def __repr__(self) -> str:
        return f"<KnowledgeArticle(id={self.id}, title={self.title!r})>"


# ---------------------------------------------------------------------------
# Knowledge Chunk (embeddings for RAG)
# ---------------------------------------------------------------------------


class KnowledgeChunk(Base):
    """Chunked text segments with vector embeddings for semantic search.

    Each article is split into chunks and embedded for pgvector-based
    retrieval. Requires the PostgreSQL `vector` extension:
        CREATE EXTENSION IF NOT EXISTS vector;

    Dimension must match the embedding model (1536 for text-embedding-3-small).
    """

    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_articles.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Text content of this chunk"
    )
    # pgvector column — raw Column for pgvector compatibility
    embedding = Column(
        Vector(1536),
        nullable=False,
        comment="Vector embedding (1536-dim for text-embedding-3-small)",
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Additional metadata: chunk_index, char_offset, etc."
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # ── Relationships ──────────────────────────────────────────────────
    article: Mapped["KnowledgeArticle"] = relationship(
        "KnowledgeArticle", back_populates="chunks"
    )

    __table_args__ = (
        Index("ix_knowledge_chunks_article", "article_id"),
        # IVFFlat index for cosine similarity — created via migration:
        # CREATE INDEX ix_knowledge_chunks_embedding
        #   ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops)
        #   WITH (lists = 100);
    )

    def __repr__(self) -> str:
        return f"<KnowledgeChunk(id={self.id}, article_id={self.article_id})>"


# ---------------------------------------------------------------------------
# Legacy models (kept for backward compatibility)
# ---------------------------------------------------------------------------


class KnowledgeDocument(Base):
    """Knowledge documents table — chunked source documents for RAG.

    Legacy model kept for backward compatibility. New code should use
    KnowledgeArticle + KnowledgeChunk instead.
    """

    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    chunk_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    embeddings: Mapped[List["DocumentEmbedding"]] = relationship(
        "DocumentEmbedding",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    __table_args__ = (
        Index("ix_knowledge_docs_category", "category"),
        Index("ix_knowledge_docs_language", "language"),
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeDocument(id={self.id}, title={self.title!r}, "
            f"category={self.category!r}, lang={self.language!r})>"
        )


class DocumentEmbedding(Base):
    """Document embeddings table — pgvector vectors for semantic search.

    Legacy model kept for backward compatibility.
    """

    __tablename__ = "document_embeddings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    embedding = Column(
        Vector(1536),
        nullable=False,
        comment="Vector embedding (1536-dim for text-embedding-3-small)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    document: Mapped["KnowledgeDocument"] = relationship(
        "KnowledgeDocument", back_populates="embeddings"
    )

    __table_args__ = (
        Index("ix_doc_embeddings_doc", "document_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<DocumentEmbedding(id={self.id}, document_id={self.document_id})>"
        )
