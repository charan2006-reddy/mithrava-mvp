#!/usr/bin/env python3
"""
Mithrava Database Seed Script
==============================
Populates the database with realistic Indian farming data for development
and demonstration purposes.

Usage:
    python scripts/seed_db.py          # Run against default DATABASE_URL
    python scripts/seed_db.py --reset  # Drop and recreate all tables first

Requirements:
    pip install asyncpg sqlalchemy python-dotenv
"""

import asyncio
import argparse
import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Bootstrap: add project root to path so we can import app models
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / "backend" / ".env")
except ImportError:
    pass

try:
    import asyncpg
except ImportError:
    print("ERROR: asyncpg is required. Install with: pip install asyncpg")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://mithrava:mithrava@localhost:5432/mithrava",
)

# For raw SQL we need the plain asyncpg URL
ASYNC_PG_URL = DATABASE_URL.replace("+asyncpg", "")


# ---------------------------------------------------------------------------
# SQL Helpers
# ---------------------------------------------------------------------------
CREATE_TABLES_SQL = """
-- Farmers
CREATE TABLE IF NOT EXISTS farmers (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    phone           VARCHAR(20) UNIQUE NOT NULL,
    district        VARCHAR(100),
    state           VARCHAR(100),
    preferred_lang  VARCHAR(20) DEFAULT 'hindi',
    avatar_url      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Lands
CREATE TABLE IF NOT EXISTS lands (
    id              SERIAL PRIMARY KEY,
    farmer_id       INTEGER REFERENCES farmers(id) ON DELETE CASCADE,
    name            VARCHAR(255),
    area_acres      DECIMAL(6,2) NOT NULL,
    soil_type       VARCHAR(30),
    latitude        DECIMAL(10,7),
    longitude       DECIMAL(10,7),
    irrigation_type VARCHAR(50),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Crops
CREATE TABLE IF NOT EXISTS crops (
    id              SERIAL PRIMARY KEY,
    land_id         INTEGER REFERENCES lands(id) ON DELETE CASCADE,
    farmer_id       INTEGER REFERENCES farmers(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    variety         VARCHAR(100),
    status          VARCHAR(30) DEFAULT 'planned',
    sowing_date     DATE,
    expected_harvest DATE,
    actual_harvest  DATE,
    area_acres      DECIMAL(6,2),
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Vendors
CREATE TABLE IF NOT EXISTS vendors (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    district        VARCHAR(100),
    state           VARCHAR(100),
    category        VARCHAR(50),
    phone           VARCHAR(20),
    rating          DECIMAL(2,1),
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Market Prices
CREATE TABLE IF NOT EXISTS market_prices (
    id              SERIAL PRIMARY KEY,
    crop_name       VARCHAR(100) NOT NULL,
    mandi           VARCHAR(150) NOT NULL,
    state           VARCHAR(100),
    price_min       DECIMAL(10,2),
    price_max       DECIMAL(10,2),
    price_modal     DECIMAL(10,2),
    unit            VARCHAR(20) DEFAULT 'per_quintal',
    date            DATE DEFAULT CURRENT_DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Forum Posts
CREATE TABLE IF NOT EXISTS forum_posts (
    id              SERIAL PRIMARY KEY,
    farmer_id       INTEGER REFERENCES farmers(id) ON DELETE SET NULL,
    title           VARCHAR(500) NOT NULL,
    body            TEXT NOT NULL,
    post_type       VARCHAR(30) DEFAULT 'question',
    tags            TEXT[],
    upvotes         INTEGER DEFAULT 0,
    reply_count     INTEGER DEFAULT 0,
    is_solved       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Forum Replies
CREATE TABLE IF NOT EXISTS forum_replies (
    id              SERIAL PRIMARY KEY,
    post_id         INTEGER REFERENCES forum_posts(id) ON DELETE CASCADE,
    farmer_id       INTEGER REFERENCES farmers(id) ON DELETE SET NULL,
    body            TEXT NOT NULL,
    is_accepted     BOOLEAN DEFAULT FALSE,
    upvotes         INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Expert Calls
CREATE TABLE IF NOT EXISTS expert_calls (
    id              SERIAL PRIMARY KEY,
    farmer_id       INTEGER REFERENCES farmers(id) ON DELETE SET NULL,
    expert_name     VARCHAR(255),
    topic           VARCHAR(500) NOT NULL,
    description     TEXT,
    status          VARCHAR(30) DEFAULT 'scheduled',
    scheduled_at    TIMESTAMPTZ,
    started_at      TIMESTAMPTZ,
    ended_at        TIMESTAMPTZ,
    duration_min    INTEGER,
    rating          INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Notifications (for reference)
CREATE TABLE IF NOT EXISTS notifications (
    id              SERIAL PRIMARY KEY,
    farmer_id       INTEGER REFERENCES farmers(id) ON DELETE CASCADE,
    notif_type      VARCHAR(30),
    title           VARCHAR(500),
    body            TEXT,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
"""


# ---------------------------------------------------------------------------
# Seed Data
# ---------------------------------------------------------------------------
FARMERS = [
    ("Raju Patil", "9876543210", "Pune", "Maharashtra", "telugu"),
    ("Lakshmi Devi", "9876543211", "Hyderabad", "Telangana", "telugu"),
    ("Kiran Gowda", "9876543212", "Dharwad", "Karnataka", "kannada"),
    ("Suresh Kumar", "9876543213", "Jaipur", "Rajasthan", "hindi"),
    ("Priya Sharma", "9876543214", "Lucknow", "Uttar Pradesh", "hindi"),
]

LANDS = [
    # Raju Patil (id=1)
    (1, "Patil Farm - Pune", Decimal("3.5"), "black", Decimal("18.5204"), Decimal("73.8567"), "drip"),
    (1, "Patil Field - Baramati", Decimal("2.0"), "black", Decimal("18.1500"), Decimal("74.5800"), "sprinkler"),
    (1, "Patil Orchard - Shirur", Decimal("1.5"), "black", Decimal("18.6000"), Decimal("74.3700"), "flood"),

    # Lakshmi Devi (id=2)
    (2, "Devi Gardens - Shamirpet", Decimal("4.0"), "red", Decimal("17.5900"), Decimal("78.2800"), "drip"),
    (2, "Devi Fields - Medchal", Decimal("2.5"), "red", Decimal("17.6300"), Decimal("78.4700"), "drip"),

    # Kiran Gowda (id=3)
    (3, "Gowda Farm - Dharwad", Decimal("3.0"), "black", Decimal("15.4589"), Decimal("75.0078"), "drip"),
    (3, "Gowda Fields - Haveri", Decimal("5.0"), "laterite", Decimal("14.7936"), Decimal("75.3364"), "sprinkler"),

    # Suresh Kumar (id=4)
    (4, "Kumar Farm - Jaipur", Decimal("4.5"), "sandy", Decimal("26.9124"), Decimal("75.7873"), "drip"),
    (4, "Kumar Fields - Ajmer", Decimal("3.0"), "sandy", Decimal("26.4499"), Decimal("74.6399"), "sprinkler"),

    # Priya Sharma (id=5)
    (5, "Sharma Farm - Lucknow", Decimal("2.5"), "alluvial", Decimal("26.8467"), Decimal("80.9462"), "flood"),
    (5, "Sharma Fields - Kanpur", Decimal("3.0"), "alluvial", Decimal("26.4499"), Decimal("80.3319"), "drip"),
]

CROPS = [
    # Raju Patil's crops
    (1, 1, "Tomato", "Pusa Ruby", "active", "2025-06-15", "2025-10-15", None, Decimal("2.5"), "Good growth, using drip irrigation"),
    (1, 1, "Onion", "Nashik Red", "harvested", "2025-01-10", "2025-05-10", "2025-05-08", Decimal("3.5"), "Harvested 2 days early, good price"),
    (1, 2, "Cotton", "Bt Cotton", "active", "2025-07-01", "2025-12-15", None, Decimal("2.0"), None),

    # Lakshmi Devi's crops
    (2, 4, "Rice", "Samba Mahsuri", "active", "2025-07-10", "2025-11-20", None, Decimal("3.0"), "Kharif season, transplanted"),
    (2, 4, "Groundnut", "TMV 7", "harvested", "2025-02-01", "2025-06-01", "2025-05-28", Decimal("4.0"), "Excellent yield this season"),
    (2, 5, "Maize", "HQPM 1", "sowing", "2025-08-01", "2025-11-15", None, Decimal("2.5"), "Just sown, awaiting germination"),

    # Kiran Gowda's crops
    (3, 6, "Sugarcane", "Co 86032", "active", "2024-12-15", "2025-12-15", None, Decimal("3.0"), "Long duration crop, doing well"),
    (3, 6, "Tomato", "Arka Rakshak", "failed", "2025-04-01", "2025-08-01", None, Decimal("3.0"), "Lost to late blight disease"),
    (3, 7, "Rice", "Jyothi", "harvested", "2025-01-05", "2025-05-05", "2025-05-03", Decimal("2.0"), "Good yield in rainfed conditions"),

    # Suresh Kumar's crops
    (4, 8, "Wheat", "HD 3226", "active", "2025-11-15", "2026-03-20", None, Decimal("4.5"), "Rabi season, irrigated wheat"),
    (4, 9, "Cotton", "F 1861", "harvested", "2024-07-15", "2025-01-15", "2025-01-12", Decimal("3.0"), "Picked 3 rounds of cotton"),
    (4, 8, "Maize", "Bio 9681", "active", "2025-06-20", "2025-10-10", None, Decimal("4.5"), "Monsoon crop, just vegetative stage"),

    # Priya Sharma's crops
    (5, 10, "Wheat", "K-910", "harvested", "2025-11-20", "2026-03-15", "2026-03-13", Decimal("2.5"), "Excellent yield, 28 quintals/acre"),
    (5, 10, "Onion", "Arkansas Sweet", "active", "2025-07-05", "2025-11-05", None, Decimal("2.5"), "Transplanting done, needs weeding"),
    (5, 11, "Rice", "Pusa Basmati 1121", "active", "2025-07-15", "2025-11-25", None, Decimal("3.0"), "Basmati, premium variety"),
]

VENDORS = [
    ("Krishi Bhandar", "Pune", "Maharashtra", "seeds", "020-25678901", Decimal("4.3"), "Wide range of hybrid and open-pollinated seeds. Authorized dealer for major seed companies."),
    ("Agro Supplies Plus", "Pune", "Maharashtra", "fertilizer", "020-25678902", Decimal("4.5"), "Premium fertilizers and micronutrients. Home delivery available for orders above Rs. 5000."),
    ("Green Farm Store", "Pune", "Maharashtra", "pesticide", "020-25678903", Decimal("4.1"), "Organic and chemical pesticides. Free consultation for pest management."),
    ("Karnataka Seeds Hub", "Dharwad", "Karnataka", "seeds", "0836-2445566", Decimal("4.4"), "Specializes in Karnataka-adapted varieties. KAU and UAS varieties available."),
    ("Sahyadri Agro", "Hubli", "Karnataka", "general", "0836-2789012", Decimal("4.2"), "One-stop shop for farming supplies. Seeds, fertilizers, tools, and equipment."),
    ("Deccan Agri Tools", "Hyderabad", "Telangana", "tools", "040-23456789", Decimal("4.0"), "Agricultural tools, implements, and machinery. Repair services available."),
    ("Rajasthan Farm Supplies", "Jaipur", "Rajasthan", "seeds", "0141-2345678", Decimal("3.9"), "Desert farming specialists. Drought-resistant varieties and organic inputs."),
]

MARKET_PRICES = [
    # (crop_name, mandi, state, price_min, price_max, price_modal, date)
    ("Onion", "Pune APMC", "Maharashtra", Decimal("1800"), Decimal("2800"), Decimal("2200"), "2025-07-15"),
    ("Onion", "Nashik APMC", "Maharashtra", Decimal("1600"), Decimal("2600"), Decimal("2100"), "2025-07-15"),
    ("Onion", "Lasalgaon APMC", "Maharashtra", Decimal("1900"), Decimal("2900"), Decimal("2400"), "2025-07-15"),

    ("Tomato", "Pune APMC", "Maharashtra", Decimal("1500"), Decimal("3500"), Decimal("2400"), "2025-07-15"),
    ("Tomato", "Hyderabad Market", "Telangana", Decimal("1800"), Decimal("3200"), Decimal("2500"), "2025-07-15"),
    ("Tomato", "Dharwad Mandi", "Karnataka", Decimal("1600"), Decimal("3000"), Decimal("2200"), "2025-07-15"),

    ("Rice (Paddy)", "Hyderabad Market", "Telangana", Decimal("2800"), Decimal("3800"), Decimal("3200"), "2025-07-15"),
    ("Rice (Paddy)", "Lucknow Mandi", "Uttar Pradesh", Decimal("2600"), Decimal("3600"), Decimal("3000"), "2025-07-15"),
    ("Rice (Paddy)", "Dharwad Mandi", "Karnataka", Decimal("2700"), Decimal("3500"), Decimal("3100"), "2025-07-15"),

    ("Wheat", "Jaipur Mandi", "Rajasthan", Decimal("2200"), Decimal("3000"), Decimal("2500"), "2025-07-15"),
    ("Wheat", "Lucknow Mandi", "Uttar Pradesh", Decimal("2300"), Decimal("3100"), Decimal("2600"), "2025-07-15"),
    ("Wheat", "Pune APMC", "Maharashtra", Decimal("2400"), Decimal("3200"), Decimal("2700"), "2025-07-15"),

    ("Maize", "Jaipur Mandi", "Rajasthan", Decimal("1600"), Decimal("2400"), Decimal("2000"), "2025-07-15"),
    ("Maize", "Hyderabad Market", "Telangana", Decimal("1700"), Decimal("2300"), Decimal("1950"), "2025-07-15"),
    ("Maize", "Dharwad Mandi", "Karnataka", Decimal("1650"), Decimal("2350"), Decimal("1900"), "2025-07-15"),

    ("Cotton", "Pune APMC", "Maharashtra", Decimal("5500"), Decimal("7000"), Decimal("6200"), "2025-07-15"),
    ("Cotton", "Jaipur Mandi", "Rajasthan", Decimal("5800"), Decimal("6800"), Decimal("6300"), "2025-07-15"),

    ("Sugarcane", "Pune APMC", "Maharashtra", Decimal("300"), Decimal("400"), Decimal("350"), "2025-07-15"),
    ("Sugarcane", "Dharwad Mandi", "Karnataka", Decimal("280"), Decimal("380"), Decimal("330"), "2025-07-15"),

    ("Groundnut", "Hyderabad Market", "Telangana", Decimal("4500"), Decimal("6500"), Decimal("5500"), "2025-07-15"),
    ("Groundnut", "Pune APMC", "Maharashtra", Decimal("4800"), Decimal("6200"), Decimal("5300"), "2025-07-15"),
]

FORUM_POSTS = [
    # (farmer_id, title, body, post_type, tags, upvotes, reply_count, is_solved)
    (
        1,
        "Drip irrigation pressure dropping - need help!",
        "Namaste farmers! I installed drip irrigation on my tomato farm 6 months ago. "
        "Recently the water pressure has been dropping and some emitters are not working properly. "
        "I've cleaned the filter but the issue persists. Has anyone faced this? "
        "Should I check the main pipe or is it a pump issue? My farm is in Shirur, Pune.",
        "question",
        '{"irrigation", "drip", "tomato", "technical"}',
        12,
        3,
        True,
    ),
    (
        3,
        "Tomato leaves turning yellow with brown spots - what disease is this?",
        "My tomato plants in Dharwad are showing yellow leaves with brown spots on the lower leaves. "
        "The spots are circular with concentric rings. It started from the bottom and is moving up. "
        "I'm losing about 5-10 plants daily. Please help identify the disease and suggest treatment. "
        "I have about 1.5 acres of tomatoes.",
        "question",
        '{"disease", "tomato", "plant-health", "urgent"}',
        25,
        7,
        True,
    ),
    (
        5,
        "Sold Basmati at record price this season - my journey!",
        "I want to share my success story. This year I grew Pusa Basmati 1121 on 3 acres in Lucknow. "
        "Followed ICAR guidelines strictly - proper spacing, balanced fertilization, and timely pest management. "
        "Yielded 28 quintals per acre and sold at Rs. 3,800/quintal at the Lucknow mandi. "
        "Total revenue was over Rs. 3.2 lakhs from just 3 acres. "
        "Key tips: transplant seedlings at 25 days, maintain water level, and don't skip the last fertilizer dose.",
        "success_story",
        '{"basmati", "rice", "success", "lucknow", "high-yield"}',
        45,
        12,
        False,
    ),
    (
        2,
        "Current onion prices in Hyderabad mandi?",
        "Can someone share today's onion prices at the Hyderabad market? "
        "I'm planning to sell my Nashik Red variety next week. "
        "Also heard the government imposed export restrictions - will it affect local prices?",
        "market_query",
        '{"onion", "prices", "market", "hyderabad"}',
        8,
        5,
        False,
    ),
    (
        4,
        "Best drip irrigation system for sandy soil in Rajasthan?",
        "I have 4.5 acres of sandy soil near Jaipur. Planning to install drip irrigation. "
        "Which brand is good for our conditions? Netafim, Jain, or Rivulis? "
        "Also, what emitter spacing would work best for cotton and wheat? "
        "Budget is around Rs. 60,000-80,000.",
        "question",
        '{"irrigation", "drip", "rajasthan", "sandy-soil", "cotton"}',
        18,
        4,
        True,
    ),
    (
        2,
        "Groundnut harvesting tips for red soil?",
        "I'm harvesting groundnut for the first time on red soil in Medchal. "
        "What's the right time to harvest? How do I know when the pods are mature? "
        "Should I uproot the entire plant or just pick the pods? Any drying tips?",
        "question",
        '{"groundnut", "harvesting", "red-soil", "first-time"}',
        10,
        6,
        False,
    ),
]

EXPERT_CALLS = [
    # (farmer_id, expert_name, topic, description, status, scheduled_at, duration_min, rating, feedback)
    (
        1,
        "Dr. Anand Kulkarni",
        "Drip irrigation troubleshooting",
        "Raju Patil reported pressure drops in drip system. Expert inspected remotely via video call. "
        "Identified clogged secondary filter and recommended back-flushing the mainline.",
        "completed",
        "2025-07-10 10:00:00+05:30",
        25,
        5,
        "Very helpful! Dr. Kulkarni identified the issue in minutes and gave clear step-by-step instructions.",
    ),
    (
        3,
        "Dr. Savita Biradar",
        "Tomato late blight management",
        "Kiran Gowda's tomato crop affected by Phytophthora infestans (late blight). "
        "Expert recommended immediate fungicide application (Metalaxyl + Mancozeb) and cultural practices.",
        "completed",
        "2025-07-05 14:30:00+05:30",
        30,
        4,
        "Good advice on fungicide mix. Would have liked more details on organic alternatives.",
    ),
    (
        4,
        "Prof. Ravi Sharma",
        "Drip irrigation for cotton in sandy soil",
        "Suresh Kumar wanted expert opinion on drip system selection for sandy loam soil in Rajasthan. "
        "Expert recommended Netafim Uniram with 1.6 LPH emitters at 60cm spacing for cotton.",
        "completed",
        "2025-07-12 11:00:00+05:30",
        20,
        5,
        "Excellent recommendations. Ordered the suggested system the same day.",
    ),
    (
        2,
        "Dr. Priya Reddy",
        "Groundnut harvest timing",
        "Lakshmi Devi needed guidance on determining groundnut maturity and optimal harvest timing. "
        "Expert advised the hull color test and scratch test methods.",
        "scheduled",
        "2025-07-20 09:30:00+05:30",
        None,
        None,
        None,
    ),
]

FORUM_REPLIES = [
    # (post_id, farmer_id, body, is_accepted, upvotes)
    (1, 3,
     "I faced the same issue last month. Check your main filter first - sometimes sand particles block it. "
     "Also check if there's air in the pipeline. Open the end valves and flush for 10 minutes.",
     True, 8),
    (1, 5,
     "Could be a pressure regulator issue. What's the operating pressure of your system? "
     "Tomato needs 1.0-1.5 bar at the emitter.",
     False, 5),
    (1, 2,
     "Also check the source water. If you've switched from borewell to tanker water, "
     "the tanker water might have more sediment. Install a 150-mesh filter.",
     False, 3),
    (2, 1,
     "This is definitely late blight. Spray Metalaxyl-MZ (Ridomil Gold) 2.5g/litre immediately. "
     "Also remove and destroy the affected plants. Don't compost them!",
     True, 15),
    (2, 4,
     "I use a copper-based spray (Bordeaux mixture) for prevention. Mix 10g copper sulphate "
     "and 10g hydrated lime in 1 litre water. Spray weekly during humid weather.",
     False, 10),
    (2, 5,
     "In my farm in Lucknow, we prevent this by ensuring good air circulation. "
     "Prune lower leaves and maintain proper spacing between plants.",
     False, 6),
]


# ---------------------------------------------------------------------------
# Seed Function
# ---------------------------------------------------------------------------
async def seed():
    """Insert all seed data into the database."""
    print(f"Connecting to database...")

    try:
        conn = await asyncpg.connect(ASYNC_PG_URL)
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        print(f"Make sure PostgreSQL is running and accessible at:")
        print(f"  {ASYNC_PG_URL}")
        sys.exit(1)

    print("Connected successfully!")

    try:
        # -----------------------------------------------------------------
        # Create tables
        # -----------------------------------------------------------------
        print("Creating tables...")
        await conn.execute(CREATE_TABLES_SQL)
        print("  Tables created (or already exist).")

        # -----------------------------------------------------------------
        # Seed Farmers
        # -----------------------------------------------------------------
        print("Seeding farmers...")
        farmer_ids = []
        for name, phone, district, state, lang in FARMERS:
            row = await conn.fetchrow(
                """
                INSERT INTO farmers (name, phone, district, state, preferred_lang)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (phone) DO UPDATE SET
                    name = EXCLUDED.name,
                    district = EXCLUDED.district,
                    state = EXCLUDED.state,
                    preferred_lang = EXCLUDED.preferred_lang
                RETURNING id
                """,
                name, phone, district, state, lang,
            )
            farmer_ids.append(row["id"])
        print(f"  Inserted {len(farmer_ids)} farmers.")

        # -----------------------------------------------------------------
        # Seed Lands
        # -----------------------------------------------------------------
        print("Seeding lands...")
        land_ids = []
        for farmer_id, name, area, soil, lat, lng, irr in LANDS:
            row = await conn.fetchrow(
                """
                INSERT INTO lands (farmer_id, name, area_acres, soil_type, latitude, longitude, irrigation_type)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """,
                farmer_id, name, area, soil, lat, lng, irr,
            )
            land_ids.append(row["id"])
        print(f"  Inserted {len(land_ids)} lands.")

        # -----------------------------------------------------------------
        # Seed Crops
        # -----------------------------------------------------------------
        print("Seeding crops...")
        crop_count = 0
        for land_id, farmer_id, name, variety, status, sowing, expected, actual, area, notes in CROPS:
            sowing_date = date.fromisoformat(sowing) if sowing else None
            expected_date = date.fromisoformat(expected) if expected else None
            actual_date = date.fromisoformat(actual) if actual else None
            await conn.execute(
                """
                INSERT INTO crops (land_id, farmer_id, name, variety, status,
                                   sowing_date, expected_harvest, actual_harvest, area_acres, notes)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                land_id, farmer_id, name, variety, status,
                sowing_date, expected_date, actual_date, area, notes,
            )
            crop_count += 1
        print(f"  Inserted {crop_count} crops.")

        # -----------------------------------------------------------------
        # Seed Vendors
        # -----------------------------------------------------------------
        print("Seeding vendors...")
        for name, district, state, cat, phone, rating, desc in VENDORS:
            await conn.execute(
                """
                INSERT INTO vendors (name, district, state, category, phone, rating, description)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                name, district, state, cat, phone, rating, desc,
            )
        print(f"  Inserted {len(VENDORS)} vendors.")

        # -----------------------------------------------------------------
        # Seed Market Prices
        # -----------------------------------------------------------------
        print("Seeding market prices...")
        price_count = 0
        for crop, mandi, state, pmin, pmax, pmodal, dt in MARKET_PRICES:
            await conn.execute(
                """
                INSERT INTO market_prices (crop_name, mandi, state, price_min, price_max, price_modal, date)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                crop, mandi, state, pmin, pmax, pmodal,
                date.fromisoformat(dt),
            )
            price_count += 1
        print(f"  Inserted {price_count} market prices.")

        # -----------------------------------------------------------------
        # Seed Forum Posts
        # -----------------------------------------------------------------
        print("Seeding forum posts...")
        post_ids = []
        for fid, title, body, ptype, tags, upvotes, replies, solved in FORUM_POSTS:
            row = await conn.fetchrow(
                """
                INSERT INTO forum_posts (farmer_id, title, body, post_type, tags, upvotes, reply_count, is_solved)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
                """,
                fid, title, body, ptype, tags, upvotes, replies, solved,
            )
            post_ids.append(row["id"])
        print(f"  Inserted {len(post_ids)} forum posts.")

        # -----------------------------------------------------------------
        # Seed Forum Replies
        # -----------------------------------------------------------------
        print("Seeding forum replies...")
        reply_count = 0
        for pid, fid, body, accepted, upvotes in FORUM_REPLIES:
            await conn.execute(
                """
                INSERT INTO forum_replies (post_id, farmer_id, body, is_accepted, upvotes)
                VALUES ($1, $2, $3, $4, $5)
                """,
                pid, fid, body, accepted, upvotes,
            )
            reply_count += 1
        print(f"  Inserted {reply_count} forum replies.")

        # -----------------------------------------------------------------
        # Seed Expert Calls
        # -----------------------------------------------------------------
        print("Seeding expert calls...")
        for fid, expert, topic, desc, status, sched, dur, rating, feedback in EXPERT_CALLS:
            sched_dt = datetime.fromisoformat(sched) if sched else None
            await conn.execute(
                """
                INSERT INTO expert_calls
                    (farmer_id, expert_name, topic, description, status,
                     scheduled_at, duration_min, rating, feedback)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                fid, expert, topic, desc, status, sched_dt, dur, rating, feedback,
            )
        print(f"  Inserted {len(EXPERT_CALLS)} expert calls.")

        # -----------------------------------------------------------------
        # Summary
        # -----------------------------------------------------------------
        print("\n" + "=" * 60)
        print("SEED COMPLETE!")
        print("=" * 60)
        print(f"  Farmers:       {len(FARMERS)}")
        print(f"  Lands:         {len(LANDS)}")
        print(f"  Crops:         {crop_count}")
        print(f"  Vendors:       {len(VENDORS)}")
        print(f"  Market Prices: {price_count}")
        print(f"  Forum Posts:   {len(FORUM_POSTS)}")
        print(f"  Forum Replies: {reply_count}")
        print(f"  Expert Calls:  {len(EXPERT_CALLS)}")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR during seeding: {e}")
        raise
    finally:
        await conn.close()
        print("Database connection closed.")


# ---------------------------------------------------------------------------
# Reset Function
# ---------------------------------------------------------------------------
async def reset():
    """Drop all tables and recreate them."""
    print("Resetting database...")
    conn = await asyncpg.connect(ASYNC_PG_URL)
    try:
        tables = [
            "notifications", "expert_calls", "forum_replies", "forum_posts",
            "market_prices", "vendors", "crops", "lands", "farmers",
        ]
        for table in tables:
            await conn.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            print(f"  Dropped {table}")
        print("All tables dropped.")
    finally:
        await conn.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Seed the Mithrava database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all tables before seeding",
    )
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    try:
        if args.reset:
            loop.run_until_complete(reset())
        loop.run_until_complete(seed())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
