"""Database seed script — populates knowledge base + demo data.

Run with:
    python -m app.scripts.seed_all

Idempotent: checks for existing data before inserting.
Safe to run multiple times (no duplicates).
"""

import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta

# Ensure app root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("mithrava.seed")


async def seed_knowledge_base(session) -> dict:
    """Seed the RAG knowledge base with default farming articles."""
    from app.services.rag_service import RAGService

    result = await RAGService.seed_knowledge_base(session)
    articles = result.get("articles", 0)
    chunks = result.get("chunks", 0)
    logger.info(f"  Knowledge: {articles} articles, {chunks} chunks seeded")
    return result


async def seed_demo_farmer(session) -> str | None:
    """Create a demo farmer with profile data. Returns farmer_id."""
    from sqlalchemy import select
    from app.models.farmer import Farmer

    # Check if demo farmer already exists
    result = await session.execute(
        select(Farmer).where(Farmer.phone == "+919999999999")
    )
    existing = result.scalar_one_or_none()
    if existing:
        logger.info(f"  Demo farmer already exists: {existing.id}")
        return str(existing.id)

    farmer_id = str(uuid.uuid4())
    farmer = Farmer(
        id=farmer_id,
        name="Demo Farmer",
        phone="+919999999999",
        email="demo@mithrava.com",
        city="Hyderabad",
        state="Telangana",
        preferred_language="en",
        farm_size_acres=5.0,
        soil_type="red",
        irrigation_type="drip",
        is_active=True,
        is_verified=True,
        role="farmer",
    )
    session.add(farmer)
    await session.flush()

    # Create demo crops
    from app.models.crop import Crop

    crops_data = [
        ("Rice", "Sona Masuri", 2.0, "planted", datetime(2026, 6, 15).date(), datetime(2026, 10, 15).date()),
        ("Cotton", "Bt Cotton", 1.5, "active", datetime(2026, 5, 1).date(), datetime(2026, 11, 30).date()),
        ("Chilli", "Guntur Sannam", 1.0, "flowering", datetime(2026, 5, 20).date(), datetime(2026, 9, 30).date()),
    ]

    crop_ids = []
    for name, variety, area, status, plant_date, harvest_date in crops_data:
        crop = Crop(
            id=str(uuid.uuid4()),
            farmer_id=farmer_id,
            name=name,
            variety=variety,
            area_acres=area,
            status=status,
            planting_date=plant_date,
            expected_harvest_date=harvest_date,
            soil_type="red",
            irrigation_type="drip",
        )
        session.add(crop)
        crop_ids.append(str(crop.id))
    await session.flush()

    # Create demo expenses
    from app.models.finance import Expense

    expenses_data = [
        ("seeds", 15000.0, "Rice and cotton seeds"),
        ("fertilizer", 8000.0, "NPK fertilizer for all crops"),
        ("pesticide", 3500.0, "Neem oil and synthetic pesticide"),
        ("labor", 12000.0, "Planting and weeding labor"),
        ("irrigation", 5000.0, "Drip irrigation maintenance"),
    ]

    for category, amount, desc in expenses_data:
        expense = Expense(
            id=str(uuid.uuid4()),
            farmer_id=farmer_id,
            crop_id=crop_ids[0],
            category=category,
            amount=amount,
            description=desc,
            date=datetime.now(timezone.utc).date() - timedelta(days=30),
        )
        session.add(expense)

    # Create demo income
    from app.models.finance import Income

    income = Income(
        id=str(uuid.uuid4()),
        farmer_id=farmer_id,
        crop_id=crop_ids[0],
        amount=45000.0,
        quantity_kg=2000.0,
        price_per_kg=22.5,
        buyer_name="Hyderabad Mandi",
        date=datetime.now(timezone.utc).date() - timedelta(days=10),
        notes="First harvest of the season",
    )
    session.add(income)
    await session.flush()

    logger.info(f"  Demo farmer created: {farmer_id} (3 crops, 5 expenses, 1 income)")
    return farmer_id


async def main():
    """Run all seed tasks."""
    # Load .env
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except ImportError:
        pass

    # Use SQLite if no DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
        logger.info("No DATABASE_URL set — using in-memory SQLite (dev mode)")

    from app.database import Base, init_db, async_session_factory

    # Initialize database
    logger.info("Initializing database...")
    await init_db()

    async with async_session_factory() as session:
        logger.info("")
        logger.info("Seeding knowledge base...")
        await seed_knowledge_base(session)

        logger.info("")
        logger.info("Creating demo data...")
        await seed_demo_farmer(session)

        await session.commit()

    logger.info("")
    logger.info("Seed complete!")
    logger.info("")


if __name__ == "__main__":
    asyncio.run(main())
