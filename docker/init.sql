-- Mithrava Database Initialization
-- This script runs automatically when the PostgreSQL container starts for the first time.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;      -- pgvector for AI / embeddings
CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- trigram similarity for fuzzy text search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- UUID generation

-- Create custom types used across the application
DO $$
BEGIN
    -- Soil type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'soil_type') THEN
        CREATE TYPE soil_type AS ENUM (
            'black', 'red', 'alluvial', 'laterite', 'sandy', 'loamy', 'clay'
        );
    END IF;

    -- Crop status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'crop_status') THEN
        CREATE TYPE crop_status AS ENUM (
            'planned', 'sowing', 'active', 'flowering', 'harvesting',
            'harvested', 'failed', 'abandoned'
        );
    END IF;

    -- Forum post type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'forum_post_type') THEN
        CREATE TYPE forum_post_type AS ENUM (
            'question', 'discussion', 'success_story', 'tip', 'market_query'
        );
    END IF;

    -- Call status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'call_status') THEN
        CREATE TYPE call_status AS ENUM (
            'scheduled', 'in_progress', 'completed', 'cancelled', 'no_show'
        );
    END IF;

    -- Vendor category enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'vendor_category') THEN
        CREATE TYPE vendor_category AS ENUM (
            'seeds', 'fertilizer', 'pesticide', 'tools', 'irrigation', 'general'
        );
    END IF;

    -- Notification type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'notification_type') THEN
        CREATE TYPE notification_type AS ENUM (
            'weather_alert', 'pest_warning', 'price_update',
            'call_reminder', 'forum_reply', 'system'
        );
    END IF;
END $$;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Mithrava database extensions and types initialized successfully.';
END $$;
