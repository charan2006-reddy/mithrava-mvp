"""Add missing tables + alter existing tables to match current models.

Tables added: knowledge_documents, knowledge_chunks, document_embeddings,
knowledge_categories, lands, market_prices, expert_calls, refresh_tokens,
otp_codes, audit_logs, farmer_settings, device_tokens.

Tables altered: farmers (add role, profile_image_url), disease_scans
(drop treatment_plan/model_used, add treatment/treatment_json/prevention_json
etc.), knowledge_articles (drop old columns, add document_id FK).

Revision ID: 002_add_missing_tables
Revises: 001_initial
Create Date: 2026-07-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "002_add_missing_tables"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -------------------------------------------------------------------
    # 1. ALTER farmers — add role, profile_image_url
    # -------------------------------------------------------------------
    op.add_column(
        "farmers",
        sa.Column("role", sa.String(20), server_default="farmer", nullable=False),
    )
    op.add_column(
        "farmers",
        sa.Column("profile_image_url", sa.String(500), nullable=True),
    )

    # -------------------------------------------------------------------
    # 2. ALTER disease_scans — drop old columns, add new ones
    # -------------------------------------------------------------------
    # SQLite doesn't support DROP COLUMN directly, so we use batch mode
    # via render_as_batch=True in env.py. For PostgreSQL, these work fine.
    with op.batch_alter_table("disease_scans") as batch_op:
        # Drop old columns that no longer exist in the model
        try:
            batch_op.drop_column("treatment_plan")
        except Exception:
            pass
        try:
            batch_op.drop_column("model_used")
        except Exception:
            pass
        # Add new columns
        batch_op.add_column(
            sa.Column("is_healthy", sa.Boolean(), server_default=sa.text("false"), nullable=True)
        )
        batch_op.add_column(
            sa.Column("description", sa.Text(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("treatment", sa.Text(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("alternative_diagnoses", postgresql.JSONB(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("treatment_json", postgresql.JSONB(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("prevention_json", postgresql.JSONB(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("model_version", sa.String(50), server_default="gpt-4o-v1", nullable=True)
        )
        batch_op.add_column(
            sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True)
        )

    # -------------------------------------------------------------------
    # 3. knowledge_documents — track uploaded documents
    # -------------------------------------------------------------------
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("source_type", sa.String(30), nullable=False, comment="file, url, text"),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=True, comment="SHA-256 for dedup"),
        sa.Column("total_chunks", sa.Integer(), server_default=sa.text("0")),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -------------------------------------------------------------------
    # 4. knowledge_chunks — text chunks with embeddings
    # -------------------------------------------------------------------
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_knowledge_chunks_doc", "knowledge_chunks", ["document_id"])

    # -------------------------------------------------------------------
    # 5. document_embeddings — vector embeddings for RAG
    # -------------------------------------------------------------------
    try:
        from pgvector.sqlalchemy import Vector
        op.create_table(
            "document_embeddings",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("chunk_id", sa.String(36), sa.ForeignKey("knowledge_chunks.id", ondelete="CASCADE"), nullable=False),
            sa.Column("embedding", Vector(1536), nullable=False),
            sa.Column("model_name", sa.String(100), server_default="text-embedding-3-small"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_document_embeddings_chunk", "document_embeddings", ["chunk_id"])
    except ImportError:
        # pgvector not available — skip embedding table (dev mode)
        pass

    # -------------------------------------------------------------------
    # 6. knowledge_categories
    # -------------------------------------------------------------------
    op.create_table(
        "knowledge_categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -------------------------------------------------------------------
    # 7. ALTER knowledge_articles — add document_id FK, drop embedding column
    # -------------------------------------------------------------------
    with op.batch_alter_table("knowledge_articles") as batch_op:
        batch_op.add_column(
            sa.Column("document_id", sa.String(36), sa.ForeignKey("knowledge_documents.id", ondelete="SET NULL"), nullable=True)
        )
        try:
            batch_op.drop_column("embedding")
        except Exception:
            pass
        try:
            batch_op.drop_column("tags")
        except Exception:
            pass

    # -------------------------------------------------------------------
    # 8. lands
    # -------------------------------------------------------------------
    op.create_table(
        "lands",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("area_acres", sa.Float(), nullable=False),
        sa.Column("soil_type", sa.String(50), nullable=True),
        sa.Column("location_lat", sa.Float(), nullable=True),
        sa.Column("location_lng", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_lands_farmer_id", "lands", ["farmer_id"])
    op.create_index("ix_lands_farmer_name", "lands", ["farmer_id", "name"])

    # -------------------------------------------------------------------
    # 9. market_prices
    # -------------------------------------------------------------------
    op.create_table(
        "market_prices",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("crop_name", sa.String(100), nullable=False),
        sa.Column("market_name", sa.String(200), nullable=False),
        sa.Column("price_per_kg", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(20), server_default="kg", nullable=False),
        sa.Column("trend", sa.String(10), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_market_prices_crop_date", "market_prices", ["crop_name", "date"])
    op.create_index("ix_market_prices_market", "market_prices", ["market_name"])
    op.create_index("ix_market_prices_date", "market_prices", ["date"])

    # -------------------------------------------------------------------
    # 10. expert_calls
    # -------------------------------------------------------------------
    op.create_table(
        "expert_calls",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("phone", sa.String(15), nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_expert_calls_farmer_id", "expert_calls", ["farmer_id"])
    op.create_index("ix_expert_calls_status", "expert_calls", ["status"])
    op.create_index("ix_expert_calls_created", "expert_calls", ["created_at"])

    # -------------------------------------------------------------------
    # 11. refresh_tokens
    # -------------------------------------------------------------------
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("device_info", sa.String(500), server_default="unknown", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_refresh_tokens_farmer_id", "refresh_tokens", ["farmer_id"])
    op.create_index("ix_refresh_tokens_farmer_active", "refresh_tokens", ["farmer_id", "revoked"])

    # -------------------------------------------------------------------
    # 12. otp_codes
    # -------------------------------------------------------------------
    op.create_table(
        "otp_codes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("phone", sa.String(15), nullable=False),
        sa.Column("code", sa.String(6), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_otp_codes_phone_code", "otp_codes", ["phone", "code"])
    op.create_index("ix_otp_codes_expires", "otp_codes", ["expires_at"])

    # -------------------------------------------------------------------
    # 13. audit_logs
    # -------------------------------------------------------------------
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=True),
        sa.Column("old_value", postgresql.JSONB(), nullable=True),
        sa.Column("new_value", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_farmer_id", "audit_logs", ["farmer_id"])
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created", "audit_logs", ["created_at"])

    # -------------------------------------------------------------------
    # 14. farmer_settings (1:1 with farmers)
    # -------------------------------------------------------------------
    op.create_table(
        "farmer_settings",
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("preferred_language", sa.String(10), server_default="en", nullable=False),
        sa.Column("voice_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("auto_speak", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("notifications_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -------------------------------------------------------------------
    # 15. device_tokens (FCM push notification tokens)
    # -------------------------------------------------------------------
    op.create_table(
        "device_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), nullable=False),
        sa.Column("token", sa.String(500), nullable=False, unique=True),
        sa.Column("platform", sa.String(10), server_default="android", nullable=False),
        sa.Column("device_info", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_device_tokens_farmer_id", "device_tokens", ["farmer_id"])
    op.create_index("ix_device_tokens_token", "device_tokens", ["token"], unique=True)
    op.create_index("ix_device_tokens_farmer_active", "device_tokens", ["farmer_id", "is_active"])


def downgrade() -> None:
    # Drop in reverse order of creation
    op.drop_table("device_tokens")
    op.drop_table("farmer_settings")
    op.drop_table("audit_logs")
    op.drop_table("otp_codes")
    op.drop_table("refresh_tokens")
    op.drop_table("expert_calls")
    op.drop_table("market_prices")
    op.drop_table("lands")
    op.drop_table("knowledge_categories")
    try:
        op.drop_table("document_embeddings")
    except Exception:
        pass
    op.drop_table("knowledge_chunks")
    op.drop_table("knowledge_documents")

    # Revert disease_scans changes
    with op.batch_alter_table("disease_scans") as batch_op:
        for col in ["is_healthy", "description", "treatment", "alternative_diagnoses",
                     "treatment_json", "prevention_json", "model_version", "analyzed_at"]:
            try:
                batch_op.drop_column(col)
            except Exception:
                pass

    # Revert farmers changes
    with op.batch_alter_table("farmers") as batch_op:
        try:
            batch_op.drop_column("profile_image_url")
        except Exception:
            pass
        try:
            batch_op.drop_column("role")
        except Exception:
            pass
