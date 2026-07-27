"""RAG (Retrieval-Augmented Generation) service for the knowledge base.

Handles document ingestion, chunking, embedding generation, semantic
search via pgvector, and context-aware answer generation using Ollama/OpenAI.
"""

import logging
import re
from typing import Optional

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm import generate_embeddings, generate_with_context
from app.models.knowledge import (
    KnowledgeArticle,
    KnowledgeCategory,
    KnowledgeChunk,
)

logger = logging.getLogger("mithrava.rag")

# ---------------------------------------------------------------------------
# Chunking configuration
# ---------------------------------------------------------------------------

CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 50     # overlap between consecutive chunks


# ---------------------------------------------------------------------------
# RAG Service
# ---------------------------------------------------------------------------


class RAGService:
    """RAG pipeline service — ingest, search, and generate answers."""

    # ------------------------------------------------------------------
    # Document ingestion
    # ------------------------------------------------------------------

    @staticmethod
    async def ingest_article(
        db: AsyncSession,
        article_id: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> int:
        """Chunk an article's content and store embeddings.

        Splits the article into overlapping chunks, generates an embedding
        for each chunk, and inserts the records into knowledge_chunks.

        Args:
            db: Async database session.
            article_id: The parent article's ID.
            content: Full text content to chunk.
            metadata: Optional metadata dict attached to each chunk.

        Returns:
            Number of chunks created.
        """
        chunks = RAGService._split_text(content, CHUNK_SIZE, CHUNK_OVERLAP)
        if not chunks:
            return 0

        count = 0
        for idx, chunk_text in enumerate(chunks):
            try:
                embedding = await generate_embeddings(chunk_text)
            except Exception as exc:
                logger.error("Embedding failed for chunk %d: %s", idx, exc)
                continue

            chunk_meta = {
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "char_offset": content.find(chunk_text[:50]),
                **(metadata or {}),
            }

            chunk = KnowledgeChunk(
                article_id=article_id,
                content=chunk_text,
                embedding=embedding,
                metadata_json=chunk_meta,
            )
            db.add(chunk)
            count += 1

        await db.flush()
        logger.info(
            "Ingested %d chunks for article %s", count, article_id
        )
        return count

    @staticmethod
    async def ingest_article_full(
        db: AsyncSession,
        article_id: str,
        content: str,
        title: str = "",
        category: str = "",
        source: str = "",
    ) -> int:
        """Ingest an article with metadata (convenience wrapper).

        Args:
            db: Async database session.
            article_id: The parent article's ID.
            content: Full text content.
            title: Article title (added to metadata).
            category: Category slug.
            source: Source attribution.

        Returns:
            Number of chunks created.
        """
        metadata = {
            "article_id": article_id,
            "title": title,
            "category": category,
            "source": source,
        }
        return await RAGService.ingest_article(db, article_id, content, metadata)

    # ------------------------------------------------------------------
    # Semantic search
    # ------------------------------------------------------------------

    @staticmethod
    async def search(
        db: AsyncSession,
        query: str,
        k: int = 5,
        category: Optional[str] = None,
    ) -> list[dict]:
        """Semantic search for relevant knowledge chunks.

        Generates an embedding for the query and performs a cosine
        similarity search against stored chunk embeddings.

        Args:
            db: Async database session.
            query: The search query.
            k: Number of results to return.
            category: Optional category slug to filter by.

        Returns:
            List of dicts with chunk content, article title, score, and metadata.
        """
        try:
            query_embedding = await generate_embeddings(query)
        except Exception as exc:
            logger.error("Query embedding failed: %s", exc)
            return []

        # Build the cosine similarity query using pgvector operator
        # The <=> operator computes cosine distance; 1 - distance = similarity
        similarity_query = text("""
            SELECT
                kc.id AS chunk_id,
                kc.content,
                kc.article_id,
                kc.metadata_json,
                ka.title AS article_title,
                ka.source,
                1.0 - (kc.embedding <=> :query_vec) AS similarity
            FROM knowledge_chunks kc
            JOIN knowledge_articles ka ON ka.id = kc.article_id
            WHERE ka.is_published = true
            ORDER BY kc.embedding <=> :query_vec
            LIMIT :k
        """)

        params = {
            "query_vec": str(query_embedding),
            "k": k,
        }

        try:
            result = await db.execute(similarity_query, params)
            rows = result.fetchall()
        except Exception as exc:
            logger.error("Vector search failed: %s", exc)
            # Fallback: basic text search
            return await RAGService._fallback_text_search(db, query, k)

        search_results = []
        for row in rows:
            score = float(row.similarity) if row.similarity else 0.0
            search_results.append({
                "chunk_id": str(row.chunk_id),
                "article_id": str(row.article_id),
                "article_title": row.article_title,
                "content": row.content,
                "score": round(score, 4),
                "metadata": row.metadata_json or {},
                "source": row.source or "",
            })

        return search_results

    @staticmethod
    async def _fallback_text_search(
        db: AsyncSession, query: str, k: int
    ) -> list[dict]:
        """Fallback text search when vector search is unavailable.

        Uses PostgreSQL ILIKE for basic keyword matching.

        Args:
            db: Async database session.
            query: The search query.
            k: Maximum results.

        Returns:
            List of search result dicts.
        """
        pattern = f"%{query}%"
        result = await db.execute(
            select(KnowledgeChunk, KnowledgeArticle)
            .join(KnowledgeArticle, KnowledgeArticle.id == KnowledgeChunk.article_id)
            .where(
                KnowledgeArticle.is_published == True,  # noqa: E712
                KnowledgeChunk.content.ilike(pattern),
            )
            .limit(k)
        )
        rows = result.all()

        return [
            {
                "chunk_id": str(chunk.id),
                "article_id": str(article.id),
                "article_title": article.title,
                "content": chunk.content,
                "score": 0.5,
                "metadata": chunk.metadata_json or {},
                "source": article.source or "",
            }
            for chunk, article in rows
        ]

    # ------------------------------------------------------------------
    # RAG query (search + generate)
    # ------------------------------------------------------------------

    @staticmethod
    async def rag_query(
        db: AsyncSession,
        question: str,
        k: int = 5,
        category: Optional[str] = None,
    ) -> dict:
        """Full RAG pipeline: search knowledge base and generate an answer.

        1. Search for relevant chunks
        2. Build context from top results
        3. Generate answer using Ollama (with OpenAI fallback)
        4. Return answer + source citations

        Args:
            db: Async database session.
            question: The farmer's question.
            k: Number of chunks to retrieve.
            category: Optional category to search within.

        Returns:
            Dict with answer, sources, and confidence score.
        """
        # Step 1: Search
        results = await RAGService.search(db, question, k=k, category=category)

        if not results:
            return {
                "answer": (
                    "I couldn't find specific information about that in our knowledge base. "
                    "Let me try to answer from general knowledge.\n\n"
                    "For the most accurate advice, please consult your local agricultural "
                    "extension officer or a farming expert."
                ),
                "sources": [],
                "confidence": 0.2,
            }

        # Step 2: Build context
        context_parts = []
        for r in results:
            context_parts.append(
                f"[Source: {r['article_title']}] {r['content']}"
            )
        context = "\n\n".join(context_parts)

        # Step 3: Generate answer
        try:
            answer = await generate_with_context(question, context)
        except Exception as exc:
            logger.error("Answer generation failed: %s", exc)
            answer = (
                "I found some relevant information but couldn't generate a complete "
                "answer right now. Please try again later."
            )

        # Step 4: Calculate confidence
        max_score = max(r["score"] for r in results) if results else 0.0
        avg_score = sum(r["score"] for r in results) / len(results) if results else 0.0
        confidence = round((max_score * 0.7 + avg_score * 0.3), 4)

        # Build source citations
        seen_articles = set()
        sources = []
        for r in results:
            if r["article_id"] not in seen_articles:
                seen_articles.add(r["article_id"])
                sources.append({
                    "article_id": r["article_id"],
                    "title": r["article_title"],
                    "excerpt": r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
                    "relevance": r["score"],
                })

        return {
            "answer": answer,
            "sources": sources[:3],
            "confidence": min(confidence, 1.0),
        }

    # ------------------------------------------------------------------
    # Knowledge base seeding
    # ------------------------------------------------------------------

    @staticmethod
    async def seed_knowledge_base(db: AsyncSession) -> dict:
        """Seed the knowledge base with initial agricultural content.

        Creates categories and articles covering the most important
        farming topics for Indian agriculture. Each article is
        automatically chunked and embedded.

        Args:
            db: Async database session.

        Returns:
            Dict with counts of categories and articles created.
        """
        categories_data = RAGService._get_seed_categories()
        articles_data = RAGService._get_seed_articles()

        cat_count = 0
        art_count = 0
        chunk_count = 0

        # Create categories
        cat_slug_map = {}
        for cat_data in categories_data:
            existing = await db.execute(
                select(KnowledgeCategory).where(
                    KnowledgeCategory.name == cat_data["name"]
                )
            )
            if existing.scalar_one_or_none():
                cat_slug_map[cat_data["name"]] = existing.scalar_one_or_none().id
                continue

            category = KnowledgeCategory(
                name=cat_data["name"],
                name_hi=cat_data.get("name_hi", cat_data["name"]),
                description=cat_data["description"],
                icon=cat_data["icon"],
            )
            db.add(category)
            await db.flush()
            cat_slug_map[cat_data["name"]] = category.id
            cat_count += 1

        # Create articles
        for art_data in articles_data:
            cat_name = art_data.get("category", "crop_guides")
            category_id = cat_slug_map.get(cat_name)
            if not category_id:
                continue

            # Skip if article already exists
            existing = await db.execute(
                select(KnowledgeArticle).where(
                    KnowledgeArticle.title == art_data["title"]
                )
            )
            if existing.scalar_one_or_none():
                continue

            article = KnowledgeArticle(
                category_id=category_id,
                title=art_data["title"],
                title_hi=art_data.get("title_hi"),
                content=art_data["content"],
                source=art_data.get("source", "Mithrava Team"),
                language=art_data.get("language", "en"),
            )
            db.add(article)
            await db.flush()
            art_count += 1

            # Ingest into chunks
            chunks_created = await RAGService.ingest_article_full(
                db,
                article_id=article.id,
                content=art_data["content"],
                title=art_data["title"],
                category=cat_name,
                source=art_data.get("source", "Mithrava Team"),
            )
            chunk_count += chunks_created

        await db.commit()
        logger.info(
            "Seeded KB: %d categories, %d articles, %d chunks",
            cat_count, art_count, chunk_count,
        )
        return {
            "categories": cat_count,
            "articles": art_count,
            "chunks": chunk_count,
        }

    # ------------------------------------------------------------------
    # Text chunking
    # ------------------------------------------------------------------

    @staticmethod
    def _split_text(text_content: str, chunk_size: int, overlap: int) -> list[str]:
        """Split text into overlapping chunks.

        Attempts to split on sentence boundaries. Falls back to word
        boundaries, then character boundaries if needed.

        Args:
            text_content: The text to split.
            chunk_size: Maximum characters per chunk.
            overlap: Overlap between consecutive chunks.

        Returns:
            List of text chunks.
        """
        if not text_content or not text_content.strip():
            return []

        # Clean whitespace
        text_content = re.sub(r"\s+", " ", text_content.strip())

        if len(text_content) <= chunk_size:
            return [text_content]

        chunks = []
        start = 0

        while start < len(text_content):
            end = min(start + chunk_size, len(text_content))

            if end < len(text_content):
                # Try to split at sentence boundary
                for sep in [". ", "! ", "? ", "\n", ", ", " "]:
                    last_sep = text_content.rfind(sep, start, end)
                    if last_sep > start + chunk_size // 2:
                        end = last_sep + len(sep)
                        break

            chunk = text_content[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap
            if start >= len(text_content):
                break

        return chunks

    # ------------------------------------------------------------------
    # Seed data — categories
    # ------------------------------------------------------------------

    @staticmethod
    def _get_seed_categories() -> list[dict]:
        """Return seed category definitions."""
        return [
            {
                "name": "crop_guides",
                "name_hi": "फसल गाइड",
                "description": "Step-by-step guides for growing popular Indian crops",
                "icon": "🌾",
            },
            {
                "name": "disease_database",
                "name_hi": "रोग डेटाबेस",
                "description": "Identify and treat common crop diseases",
                "icon": "🐛",
            },
            {
                "name": "government_schemes",
                "name_hi": "सरकारी योजनाएं",
                "description": "PM-KISAN, crop insurance, subsidies, and more",
                "icon": "🏛️",
            },
            {
                "name": "fertilizer_guide",
                "name_hi": "उर्वरक गाइड",
                "description": "NPK ratios, organic options, and timing tips",
                "icon": "💊",
            },
            {
                "name": "weather_tips",
                "name_hi": "मौसम टिप्स",
                "description": "Farm-friendly weather advice and seasonal planning",
                "icon": "🌤️",
            },
            {
                "name": "market_intelligence",
                "name_hi": "बाज़ार जानकारी",
                "description": "Price trends, best time to sell, mandi info",
                "icon": "💰",
            },
        ]

    # ------------------------------------------------------------------
    # Seed data — articles
    # ------------------------------------------------------------------

    @staticmethod
    def _get_seed_articles() -> list[dict]:
        """Return seed article definitions with full content."""
        return [
            # ── Crop Guides ──────────────────────────────────────────
            {
                "category": "crop_guides",
                "title": "Growing Tomato in India",
                "title_hi": "भारत में टमाटर की खेती",
                "source": "ICAR",
                "content": (
                    "Tomato is one of the most important vegetables grown in India. "
                    "The optimal sowing period is June-July for kharif and November-December for rabi season.\n\n"
                    "Soil Preparation: Well-drained loamy soil with pH 6.0-7.0 is ideal. "
                    "Apply 20-25 tonnes of FYM per hectare before last plowing.\n\n"
                    "Varieties: Pusa Ruby, Arka Rakshak, Arka Vishesh, Rashmi, etc.\n\n"
                    "Sowing: Use raised beds for nursery. Sow seeds 0.5 cm deep. "
                    "Transplant seedlings after 25-30 days when they have 4-5 true leaves.\n\n"
                    "Spacing: 60 cm between rows and 45 cm between plants.\n\n"
                    "Irrigation: Drip irrigation is recommended. Maintain consistent moisture. "
                    "Avoid waterlogging which causes root rot.\n\n"
                    "Fertilizer: Apply NPK 120:60:60 kg/ha. Split nitrogen into 3 doses. "
                    "First dose at transplanting, second at 30 days, third at 60 days.\n\n"
                    "Pest Management: Watch for fruit borer, leaf curl virus, and early blight. "
                    "Use neem oil spray (5ml/L) as organic option. For chemical control, "
                    "use Imidacloprid 17.8 SL for sucking pests.\n\n"
                    "Harvesting: Pick tomatoes when they turn from green to red. "
                    "Harvest every 3-4 days during peak season."
                ),
            },
            {
                "category": "crop_guides",
                "title": "Growing Rice (Paddy) in India",
                "title_hi": "भारत में धान की खेती",
                "source": "ICAR",
                "content": (
                    "Rice is the staple food of India and the country is the second largest producer globally.\n\n"
                    "Season: Kharif crop, sown June-July, harvested October-November.\n\n"
                    "Varieties: IR-64, Samba Mahsuri, Pusa Basmati, Swarna, MTU 7029.\n\n"
                    "Nursery: Prepare wet nursery beds. Sow pre-germinated seeds at 100 kg/ha. "
                    "Keep 2-3 cm water level in nursery.\n\n"
                    "Transplanting: Transplant 20-25 day old seedlings. Use 2 seedlings per hill. "
                    "Spacing: 20 cm x 15 cm.\n\n"
                    "Water Management: Maintain 5 cm standing water during vegetative stage. "
                    "Drain field 10 days before flowering. Re-flood after flowering.\n\n"
                    "Fertilizer: Apply NPK 120:60:60 kg/ha. Apply full phosphorus and potassium "
                    "at basal. Split nitrogen into 3 equal doses: basal, at tillering, and at panicle initiation.\n\n"
                    "Major Diseases: Blast (apply Tricyclazole 75 WP), Brown spot (use resistant varieties), "
                    "Bacterial leaf blight (avoid excess nitrogen).\n\n"
                    "Harvest when 80% of grains turn golden brown. Stubble height: 15-20 cm."
                ),
            },
            {
                "category": "crop_guides",
                "title": "Growing Wheat in India",
                "title_hi": "भारत में गेहूं की खेती",
                "source": "ICAR",
                "content": (
                    "Wheat is India's second most important cereal after rice.\n\n"
                    "Season: Rabi crop, sown October-November, harvested March-April.\n\n"
                    "Varieties: HD-3226, WH-1124, PBW-725, DBW-187.\n\n"
                    "Soil: Well-drained loamy soil, pH 6.0-7.5. Ideal temperature: 10-25°C.\n\n"
                    "Sowing: Broadcast or drill method. Seed rate: 100-125 kg/ha. "
                    "Depth: 5-6 cm. Row spacing: 20-23 cm.\n\n"
                    "Irrigation: 4-6 irrigations needed. Critical stages: crown root initiation "
                    "(20-25 days), jointing (40-45 days), flowering (60-65 days), grain filling (80-85 days).\n\n"
                    "Fertilizer: Apply NPK 120:60:60 kg/ha. Apply full P and K at sowing. "
                    "Split nitrogen: 1/3 at sowing, 1/3 at first irrigation, 1/3 at second irrigation.\n\n"
                    "Pest Control: Watch for termite, aphids, and rust. "
                    "For rust, use Propiconazole 25 EC @ 1ml/L. For aphids, use Imidacloprid.\n\n"
                    "Harvest when grains are hard and golden. Moisture should be below 14%."
                ),
            },
            {
                "category": "crop_guides",
                "title": "Growing Onion in India",
                "title_hi": "भारत में प्याज की खेती",
                "source": "Mithrava Team",
                "content": (
                    "India is the world's largest producer of onions.\n\n"
                    "Season: Kharif (June-July), Rabi (October-November), Late Rabi (January-February).\n\n"
                    "Varieties: Agri-303, Bhima Red, Arka Kirtiman, N-53.\n\n"
                    "Soil: Well-drained fertile loam, pH 6.0-7.0.\n\n"
                    "Nursery: Raise in well-prepared beds. Sow seeds thinly. "
                    "Transplant when seedlings are 10-12 cm tall and pencil thickness.\n\n"
                    "Spacing: 15 cm x 10 cm for bulb onions.\n\n"
                    "Irrigation: Regular irrigation is critical during bulb formation. "
                    "Stop irrigation 2 weeks before harvest for proper curing.\n\n"
                    "Fertilizer: Apply NPK 100:50:50 kg/ha. Full P and K at transplanting. "
                    "Split N into 3 doses.\n\n"
                    "Bolting Prevention: Use proper varieties for the season. "
                    "Avoid exposure to cold temperatures during early growth.\n\n"
                    "Harvest when 50-60% of tops fall over. Cure in field for 5-7 days."
                ),
            },
            # ── Disease Database ──────────────────────────────────────
            {
                "category": "disease_database",
                "title": "Tomato Leaf Blight — Causes and Treatment",
                "title_hi": "टमाटर पत्ती झुलसा — कारण और उपचार",
                "source": "ICAR",
                "content": (
                    "Early Blight (Alternaria solani) and Late Blight (Phytophthora infestans) "
                    "are two major blight diseases affecting tomatoes in India.\n\n"
                    "Early Blight Symptoms: Brown concentric ring spots on older leaves first. "
                    "Spots enlarge and merge. Severe defoliation reduces yield.\n\n"
                    "Late Blight Symptoms: Water-soaked lesions on leaves and stems. "
                    "White fuzzy growth on undersides of leaves in humid conditions. "
                    "Can destroy entire crop within days.\n\n"
                    "Organic Treatment:\n"
                    "- Spray neem oil solution (5ml/L water) every 7 days\n"
                    "- Apply Trichoderma viride (2g/L) as soil drench\n"
                    "- Remove and destroy affected leaves immediately\n"
                    "- Mulch around plants to prevent soil splash\n\n"
                    "Chemical Treatment:\n"
                    "- Mancozeb 75% WP @ 2g/L as foliar spray\n"
                    "- Chlorothalonil 75% WP @ 2g/L — repeat after 10 days\n"
                    "- Metalaxyl + Mancozeb for late blight\n"
                    "- Copper oxychloride 50% WP @ 3g/L as preventive\n\n"
                    "Prevention:\n"
                    "- Use resistant varieties like Roma or Mountain Magic\n"
                    "- Maintain proper plant spacing\n"
                    "- Avoid overhead irrigation\n"
                    "- Practice crop rotation — don't plant tomatoes in same spot for 2 years"
                ),
            },
            {
                "category": "disease_database",
                "title": "Rice Blast Disease — Identification and Control",
                "title_hi": "धान का ब्लास्ट रोग — पहचान और नियंत्रण",
                "source": "ICAR",
                "content": (
                    "Rice blast, caused by Magnaporthe oryzae, is the most destructive disease of rice worldwide.\n\n"
                    "Symptoms:\n"
                    "- Leaf blast: Diamond-shaped lesions with gray centers and brown borders\n"
                    "- Neck blast: Brown lesions on panicle neck, causing grain filling failure\n"
                    "- Severe cases cause complete crop loss\n\n"
                    "Conditions Favoring Disease:\n"
                    "- High humidity (>90%)\n"
                    "- Temperature 25-30°C\n"
                    "- Excess nitrogen fertilizer\n"
                    "- Standing water for prolonged periods\n\n"
                    "Treatment:\n"
                    "- Tricyclazole 75% WP @ 0.6g/L — most effective chemical\n"
                    "- Isoprothiolane 40% EC @ 1.5ml/L\n"
                    "- Carbendazim 50% WP @ 1g/L for early infection\n"
                    "- Neem seed kernel extract (5%) as organic option\n\n"
                    "Prevention:\n"
                    "- Use resistant varieties (Samba Mahsuri, Improved Pusa Basmati)\n"
                    "- Balanced nitrogen application\n"
                    "- Avoid late season nitrogen\n"
                    "- Maintain proper water management"
                ),
            },
            {
                "category": "disease_database",
                "title": "Wheat Rust — Yellow, Brown, and Black Rust",
                "title_hi": "गेहूं का रतुआ — पीला, भूरा और काला रतुआ",
                "source": "ICAR",
                "content": (
                    "Wheat rust is caused by three species of Puccinia fungi and is a major constraint "
                    "to wheat production in India.\n\n"
                    "Yellow Rust (Stripe Rust): Yellow-orange stripes on leaves. "
                    "Favors cool (10-15°C) and moist conditions.\n\n"
                    "Brown Rust: Brown circular pustules scattered on leaves and stems. "
                    "Favors moderate temperatures (15-22°C).\n\n"
                    "Black Rust (Stem Rust): Large dark brown to black pustules on stems and leaf sheaths. "
                    "Favors warm (20-30°C) and humid conditions.\n\n"
                    "Treatment:\n"
                    "- Propiconazole 25 EC @ 1ml/L — effective against all rust types\n"
                    "- Tebuconazole 25.9 EC @ 1ml/L\n"
                    "- Mancozeb 75 WP @ 2.5g/L as preventive spray\n"
                    "- Sulphur 80% WDG @ 3.3 kg/ha\n\n"
                    "Prevention:\n"
                    "- Grow resistant varieties (HD-3226, WH-1124)\n"
                    "- Early sowing reduces rust severity\n"
                    "- Monitor fields regularly during February-March\n"
                    "- Avoid late sowing"
                ),
            },
            # ── Government Schemes ────────────────────────────────────
            {
                "category": "government_schemes",
                "title": "PM-KISAN — Pradhan Mantri Kisan Samman Nidhi",
                "title_hi": "पीएम-किसान — प्रधानमंत्री किसान सम्मान निधि",
                "source": "Government",
                "content": (
                    "PM-KISAN is a Central Sector Scheme providing income support of ₹6,000 per year "
                    "to all landholding farmer families.\n\n"
                    "Key Features:\n"
                    "- ₹6,000 per year in 3 equal installments of ₹2,000\n"
                    "- Direct transfer to farmer's bank account via DBT\n"
                    "- Available to all landholding farmer families\n\n"
                    "Eligibility:\n"
                    "- All farmer families with cultivable land\n"
                    "- Not applicable to institutional landholders\n"
                    "- Not applicable to former/current constitutional post holders\n"
                    "- Not applicable to government employees (retired除外)\n\n"
                    "How to Apply:\n"
                    "- Visit nearest Common Service Center (CSC)\n"
                    "- Or apply online at pmkisan.gov.in\n"
                    "- Submit Aadhaar card, bank account details, and land records\n\n"
                    "Current Status: Over 11 crore farmers enrolled. "
                    "Total disbursal exceeding ₹2.8 lakh crore since 2019."
                ),
            },
            {
                "category": "government_schemes",
                "title": "PMFBY — Pradhan Mantri Fasal Bima Yojana",
                "title_hi": "पीएमएफबीवाई — प्रधानमंत्री फसल बीमा योजना",
                "source": "Government",
                "content": (
                    "PMFBY is the flagship crop insurance scheme providing financial support "
                    "to farmers in case of crop loss due to natural calamities, pests, and diseases.\n\n"
                    "Coverage:\n"
                    "- All food crops, oilseeds, and annual horticultural crops\n"
                    "- Coverage from sowing to post-harvest\n\n"
                    "Premium Rates:\n"
                    "- Kharif: 2% of sum insured\n"
                    "- Rabi: 1.5% of sum insured\n"
                    "- Horticultural: 5% of sum insured\n\n"
                    "Enrollment: Apply through bank, CSC, or insurance company within 7 days of "
                    "sowing start date. Can also enroll at pmfby.gov.in.\n\n"
                    "Claim Process:\n"
                    "- Crop cutting experiments conducted by state government\n"
                    "- If yield loss exceeds notified level, claim is processed automatically\n"
                    "- Farmer can also file individual claim through insurance company\n\n"
                    "Benefits: Government pays remaining premium. "
                    "Quick claim settlement within 2 months of harvest."
                ),
            },
            {
                "category": "government_schemes",
                "title": "Kisan Credit Card (KCC)",
                "title_hi": "किसान क्रेडिट कार्ड (KCC)",
                "source": "Government",
                "content": (
                    "KCC provides affordable credit to farmers for their agricultural needs.\n\n"
                    "Features:\n"
                    "- Short-term crop loans at 4% interest (after subvention)\n"
                    "- Credit limit based on land holding and cropping pattern\n"
                    "- Covers cultivation costs, post-harvest expenses, and consumption\n"
                    "- Insurance coverage under PMFBY\n\n"
                    "Eligibility:\n"
                    "- All farmers (individual or joint)\n"
                    "- Tenant farmers, oral lessees, and sharecroppers\n"
                    "- Self-Help Groups (SHGs) and Joint Liability Groups (JLGs)\n\n"
                    "How to Apply:\n"
                    "- Visit nearest bank branch with: land documents, ID proof, photos\n"
                    "- Processing takes 7-10 working days\n\n"
                    "Interest Subvention: 2% additional subvention for prompt repayment. "
                    "Effective interest rate: 4% per annum for short-term crop loans."
                ),
            },
            # ── Fertilizer Guide ──────────────────────────────────────
            {
                "category": "fertilizer_guide",
                "title": "NPK Fertilizer Usage Guide for Indian Crops",
                "title_hi": "भारतीय फसलों के लिए NPK उर्वरक उपयोग गाइड",
                "source": "ICAR",
                "content": (
                    "Proper NPK (Nitrogen, Phosphorus, Potassium) management is essential for crop health.\n\n"
                    "General NPK Recommendations (kg/ha):\n"
                    "- Tomato: N 120, P 60, K 60\n"
                    "- Rice: N 120, P 60, K 60\n"
                    "- Wheat: N 120, P 60, K 60\n"
                    "- Onion: N 100, P 50, K 50\n"
                    "- Cotton: N 150, P 60, K 60\n"
                    "- Maize: N 120, P 60, K 60\n\n"
                    "Nitrogen Application Tips:\n"
                    "- Split into 2-3 doses for best results\n"
                    "- First dose at sowing/transplanting\n"
                    "- Remaining doses at critical growth stages\n"
                    "- Avoid application before heavy rain (leaching loss)\n\n"
                    "Phosphorus:\n"
                    "- Apply full dose at sowing time\n"
                    "- Mix well with soil in root zone\n"
                    "- DAP (18-46-0) is most common source\n\n"
                    "Potassium:\n"
                    "- Apply full dose at sowing\n"
                    "- MOP (0-0-60) is primary source\n"
                    "- Critical for fruit development and disease resistance\n\n"
                    "Signs of Deficiency:\n"
                    "- Nitrogen: Yellowing of older leaves, stunted growth\n"
                    "- Phosphorus: Purple/dark green leaves, poor root development\n"
                    "- Potassium: Brown leaf edges, weak stems"
                ),
            },
            {
                "category": "fertilizer_guide",
                "title": "Organic Farming Basics for Indian Farmers",
                "title_hi": "भारतीय किसानों के लिए जैविक खेती की मूल बातें",
                "source": "Mithrava Team",
                "content": (
                    "Organic farming avoids synthetic chemicals and focuses on natural inputs.\n\n"
                    "Key Organic Inputs:\n"
                    "- FYM (Farm Yard Manure): 10-15 tonnes/ha, applied before sowing\n"
                    "- Vermicompost: 2-3 tonnes/ha, rich in beneficial microbes\n"
                    "- Green Manure: Dhaincha or sunn hemp, incorporated before flowering\n"
                    "- Neem Cake: 200-250 kg/ha as basal application\n\n"
                    "Bio-Fertilizers:\n"
                    "- Rhizobium for legumes (fixes atmospheric nitrogen)\n"
                    "- Azotobacter for cereals (nitrogen fixation)\n"
                    "- PSB (Phosphate Solubilizing Bacteria) for phosphorus\n"
                    "- Mycorrhiza for improved root uptake\n\n"
                    "Pest Control (Organic):\n"
                    "- Neem oil spray (5ml/L) — effective against most sucking pests\n"
                    "- Trichoderma viride (2g/L) — fungicide for soil-borne diseases\n"
                    "- Pseudomonas fluorescens — for bacterial diseases\n"
                    "- Bt (Bacillus thuringiensis) — for caterpillars\n"
                    "- Yellow sticky traps — for whiteflies and aphids\n\n"
                    "Certification: Get certified through NPOP (National Programme for Organic Production). "
                    "Visit apeda.gov.in for details."
                ),
            },
            # ── Weather Tips ──────────────────────────────────────────
            {
                "category": "weather_tips",
                "title": "Monsoon Farming Tips",
                "title_hi": "मानसून में खेती के टिप्स",
                "source": "Mithrava Team",
                "content": (
                    "The Indian monsoon (June-September) is critical for kharif crops.\n\n"
                    "Before Monsoon:\n"
                    "- Complete land preparation before first rain\n"
                    "- Ensure proper drainage in fields\n"
                    "- Store seeds and fertilizers in dry place\n"
                    "- Repair farm equipment and irrigation channels\n\n"
                    "During Monsoon:\n"
                    "- Sow seeds immediately after first good rain\n"
                    "- Ensure proper drainage to prevent waterlogging\n"
                    "- Monitor for pest and disease outbreaks\n"
                    "- Apply fertilizers after soil moisture stabilizes\n\n"
                    "Excess Rain Management:\n"
                    "- Remove standing water from fields immediately\n"
                    "- Apply light nitrogen dose to help crop recover\n"
                    "- Watch for root rot and fungal diseases\n"
                    "- Consider replanting if damage is severe\n\n"
                    "Drought Management:\n"
                    "- Mulch to conserve soil moisture\n"
                    "- Prioritize irrigation for critical growth stages\n"
                    "- Reduce plant spacing to reduce water demand\n"
                    "- Use drought-tolerant varieties next season"
                ),
            },
            {
                "category": "weather_tips",
                "title": "Heat Wave Protection for Crops",
                "title_hi": "फसलों के लिए लू से बचाव",
                "source": "Mithrava Team",
                "content": (
                    "Heat waves (March-June) can severely damage crops, especially during flowering and grain filling.\n\n"
                    "Protection Measures:\n"
                    "- Irrigate fields during early morning or late evening\n"
                    "- Use mulching to reduce soil temperature\n"
                    "- Provide shade nets for vegetables and nursery\n"
                    "- Increase irrigation frequency during heat wave days\n\n"
                    "Critical Stages Vulnerable to Heat:\n"
                    "- Wheat: Flowering and grain filling (February-March)\n"
                    "- Mustard: Flowering stage\n"
                    "- Vegetables: Fruit setting and fruit development\n\n"
                    "Crop-specific Protection:\n"
                    "- Wheat: Extra irrigation at grain filling stage\n"
                    "- Vegetables: Sprinkle irrigation during noon hours\n"
                    "- Nursery: Use shade net (50% shade)\n\n"
                    "Post Heat Wave Care:\n"
                    "- Apply light irrigation immediately\n"
                    "- Spray seaweed extract (3ml/L) for stress recovery\n"
                    "- Apply foliar spray of potassium (2% KCl)\n"
                    "- Monitor for secondary pest attacks"
                ),
            },
            # ── Market Intelligence ───────────────────────────────────
            {
                "category": "market_intelligence",
                "title": "Best Time to Sell Your Produce",
                "title_hi": "अपनी उपज बेचने का सबसे अच्छा समय",
                "source": "Mithrava Team",
                "content": (
                    "Timing your sale can significantly affect your income.\n\n"
                    "Price Patterns:\n"
                    "- Prices are lowest at peak harvest (oversupply)\n"
                    "- Prices rise 2-4 weeks after peak harvest\n"
                    "- Prices peak during lean season (low supply)\n\n"
                    "Storage Tips for Better Prices:\n"
                    "- Onion: Store in ventilated rooms, sell 2-3 months after harvest\n"
                    "- Potato: Use diffused light storage, sell during off-season\n"
                    "- Grains: Store in gunny bags in dry, ventilated godown\n"
                    "- Pulses: Store in metal bins with neem leaves\n\n"
                    "Mandi Tips:\n"
                    "- Compare prices across 2-3 mandis\n"
                    "- Use e-NAM platform for better price discovery\n"
                    "- Sell directly to retailers when possible\n"
                    "- Form farmer producer organizations (FPOs) for bulk selling\n\n"
                    "Government Support:\n"
                    "- MSP (Minimum Support Price) ensures minimum return\n"
                    "- Price Deficiency Payment Scheme in some states\n"
                    "- e-NAM connects farmers to pan-India buyers"
                ),
            },
            {
                "category": "market_intelligence",
                "title": "Understanding MSP (Minimum Support Price)",
                "title_hi": "MSP (न्यूनतम समर्थन मूल्य) समझना",
                "source": "Government",
                "content": (
                    "MSP is the minimum price guaranteed by the Government of India for 23 crops.\n\n"
                    "Crops Under MSP:\n"
                    "- Cereals: Rice, Wheat, Maize, Bajra, Jowar, Ragi, etc.\n"
                    "- Pulses: Gram, Moong, Masoor, Arhar\n"
                    "- Oilseeds: Groundnut, Soybean, Rapeseed, Sunflower\n"
                    "- Commercial: Cotton, Sugarcane, Jute\n\n"
                    "How MSP Works:\n"
                    "- CACP recommends MSP based on cost of production + 50% margin\n"
                    "- Government announces MSP before each season\n"
                    "- FCI and state agencies procure at MSP\n\n"
                    "Procurement Process:\n"
                    "- Register at nearest procurement center\n"
                    "- Bring Aadhaar, bank details, land records\n"
                    "- Crop is graded and weighed\n"
                    "- Payment within 48 hours of delivery\n\n"
                    "Tips for Farmers:\n"
                    "- Register for procurement before harvest season\n"
                    "- Ensure crop quality meets procurement standards\n"
                    "- Keep all documents ready for quick processing\n"
                    "- Consider FPO registration for collective bargaining"
                ),
            },
        ]
