"""Initial schema — all Mithrava tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-07-18
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension (required for VECTOR columns)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # -----------------------------------------------------------------------
    # farmers
    # -----------------------------------------------------------------------
    op.create_table(
        "farmers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("phone", sa.String(20), nullable=False, unique=True),
        sa.Column("email", sa.String(200), nullable=True, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("avatar", sa.String(500), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("pincode", sa.String(10), nullable=True),
        sa.Column("farm_size_acres", sa.Float, nullable=True),
        sa.Column("soil_type", sa.String(50), nullable=True),
        sa.Column("irrigation_type", sa.String(50), nullable=True),
        sa.Column("preferred_language", sa.String(5), server_default="en"),
        sa.Column("hashed_password", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_farmers_phone", "farmers", ["phone"])

    # -----------------------------------------------------------------------
    # crops
    # -----------------------------------------------------------------------
    op.create_table(
        "crops",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("variety", sa.String(100), nullable=True),
        sa.Column("area_acres", sa.Float, nullable=True),
        sa.Column("planting_date", sa.Date, nullable=True),
        sa.Column("expected_harvest_date", sa.Date, nullable=True),
        sa.Column("status", sa.String(20), server_default="planted"),
        sa.Column("soil_type", sa.String(50), nullable=True),
        sa.Column("irrigation_type", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -----------------------------------------------------------------------
    # expenses
    # -----------------------------------------------------------------------
    op.create_table(
        "expenses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("crop_id", sa.String(36), sa.ForeignKey("crops.id"), nullable=True),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("date", sa.Date, server_default=sa.func.current_date()),
        sa.Column("receipt_image_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -----------------------------------------------------------------------
    # income
    # -----------------------------------------------------------------------
    op.create_table(
        "income",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("crop_id", sa.String(36), sa.ForeignKey("crops.id"), nullable=True),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("quantity_kg", sa.Float, nullable=True),
        sa.Column("price_per_kg", sa.Float, nullable=True),
        sa.Column("buyer_name", sa.String(200), nullable=True),
        sa.Column("date", sa.Date, server_default=sa.func.current_date()),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -----------------------------------------------------------------------
    # disease_scans
    # -----------------------------------------------------------------------
    op.create_table(
        "disease_scans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("crop_id", sa.String(36), sa.ForeignKey("crops.id"), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("disease_name", sa.String(200), nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("severity", sa.String(20), nullable=True),
        sa.Column("is_healthy", sa.Boolean, server_default=sa.text("false")),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("treatment_plan", postgresql.JSONB, nullable=True),
        sa.Column("model_used", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -----------------------------------------------------------------------
    # knowledge_articles
    # -----------------------------------------------------------------------
    op.create_table(
        "knowledge_articles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("source", sa.String(200), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -----------------------------------------------------------------------
    # vendors
    # -----------------------------------------------------------------------
    op.create_table(
        "vendors",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("rating", sa.Float, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "vendor_reviews",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("vendor_id", sa.String(36), sa.ForeignKey("vendors.id"), nullable=False, index=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -----------------------------------------------------------------------
    # forum
    # -----------------------------------------------------------------------
    op.create_table(
        "forum_posts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("category", sa.String(30), server_default="general"),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("image_urls", postgresql.JSONB, nullable=True),
        sa.Column("likes_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("comments_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "forum_comments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("post_id", sa.String(36), sa.ForeignKey("forum_posts.id"), nullable=False, index=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "forum_likes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("post_id", sa.String(36), sa.ForeignKey("forum_posts.id"), nullable=False, index=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -----------------------------------------------------------------------
    # mitra conversations & messages
    # -----------------------------------------------------------------------
    op.create_table(
        "mitra_conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("language", sa.String(5), server_default="en"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "mitra_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), sa.ForeignKey("mitra_conversations.id"), nullable=False, index=True),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("intent", sa.String(50), nullable=True),
        sa.Column("actions_taken", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -----------------------------------------------------------------------
    # notifications
    # -----------------------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("notification_type", sa.String(30), nullable=False),
        sa.Column("is_read", sa.Boolean, server_default=sa.text("false")),
        sa.Column("action_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # -----------------------------------------------------------------------
    # push_subscriptions
    # -----------------------------------------------------------------------
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("endpoint", sa.String(500), nullable=False),
        sa.Column("p256dh", sa.String(200), nullable=False),
        sa.Column("auth", sa.String(200), nullable=False),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )

    # -----------------------------------------------------------------------
    # support_calls
    # -----------------------------------------------------------------------
    op.create_table(
        "support_calls",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("farmer_id", sa.String(36), sa.ForeignKey("farmers.id"), nullable=False, index=True),
        sa.Column("call_type", sa.String(30), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("support_calls")
    op.drop_table("push_subscriptions")
    op.drop_table("notifications")
    op.drop_table("mitra_messages")
    op.drop_table("mitra_conversations")
    op.drop_table("forum_likes")
    op.drop_table("forum_comments")
    op.drop_table("forum_posts")
    op.drop_table("vendor_reviews")
    op.drop_table("vendors")
    op.drop_index("ix_knowledge_articles_category", table_name="knowledge_articles") if False else None
    op.drop_table("knowledge_articles")
    op.drop_table("disease_scans")
    op.drop_table("income")
    op.drop_table("expenses")
    op.drop_table("crops")
    op.drop_index("ix_farmers_phone", table_name="farmers")
    op.drop_table("farmers")
