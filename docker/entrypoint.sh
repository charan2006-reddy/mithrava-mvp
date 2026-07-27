#!/bin/bash
# =============================================================================
# Mithrava Backend — Docker Entrypoint
# Runs database migrations, then starts the application server.
# =============================================================================

set -e

echo "============================================"
echo "  Mithrava Backend — Starting up"
echo "============================================"

# ---------------------------------------------------------------------------
# Step 1: Run Alembic migrations
# ---------------------------------------------------------------------------
echo ""
echo "[1/3] Running database migrations..."

# Wait for database to be ready (max 30 seconds)
MAX_RETRIES=30
RETRY_COUNT=0

until python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
import os

async def check_db():
    url = os.getenv('DATABASE_URL', '')
    if not url:
        return True  # No DB URL, skip check (SQLite mode)
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            return True
    except Exception:
        return False
    finally:
        await engine.dispose()

result = asyncio.run(check_db())
exit(0 if result else 1)
" 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "  WARNING: Database not ready after ${MAX_RETRIES}s — proceeding anyway"
        break
    fi
    echo "  Waiting for database... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 1
done

# Run Alembic migrations (idempotent — applies only pending migrations)
if alembic upgrade head; then
    echo "  Migrations applied successfully"
else
    echo "  WARNING: Migration failed — falling back to create_all()"
    python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
print('  Tables created via create_all()')
"
fi

# ---------------------------------------------------------------------------
# Step 2: Auto-seed knowledge base
# ---------------------------------------------------------------------------
echo ""
echo "[2/3] Seeding knowledge base..."
python -c "
import asyncio, os
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///:memory:')

async def seed():
    try:
        from app.database import async_session_factory
        from app.services.rag_service import RAGService
        async with async_session_factory() as session:
            result = await RAGService.seed_knowledge_base(session)
            if result.get('articles', 0) > 0:
                print(f'  Seeded: {result[\"articles\"]} articles, {result[\"chunks\"]} chunks')
            else:
                print('  Knowledge base already populated — skipping')
    except Exception as e:
        print(f'  Seed skipped: {e}')

asyncio.run(seed())
" 2>/dev/null || echo "  Seed skipped (not critical)"

# ---------------------------------------------------------------------------
# Step 3: Start the application
# ---------------------------------------------------------------------------
echo ""
echo "[3/3] Starting uvicorn server..."
echo "============================================"
echo ""

exec "$@"
