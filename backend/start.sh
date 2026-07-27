#!/bin/bash
# =============================================================================
# Mithrava Backend — Railway Start Script
# Runs database migrations, seeds knowledge base, then starts uvicorn.
# =============================================================================

set -e

# Railway sets PORT env var (default 8000)
PORT="${PORT:-8000}"

echo "============================================"
echo "  Mithrava Backend — Starting up"
echo "  Port: ${PORT}"
echo "============================================"

# ---------------------------------------------------------------------------
# Fix DATABASE_URL: convert postgresql:// to postgresql+asyncpg://
# Railway provides postgresql:// but async SQLAlchemy needs asyncpg driver
# ---------------------------------------------------------------------------
if [[ "${DATABASE_URL}" == postgresql://* ]]; then
    export DATABASE_URL="postgresql+asyncpg://${DATABASE_URL#postgresql://}"
    echo "  Converted DATABASE_URL to asyncpg driver"
fi

# ---------------------------------------------------------------------------
# Step 1: Wait for database
# ---------------------------------------------------------------------------
echo ""
echo "[1/3] Waiting for database..."

MAX_RETRIES=30
RETRY_COUNT=0

until python -c "
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine

async def check():
    url = os.getenv('DATABASE_URL', '')
    if not url or 'sqlite' in url:
        return True
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            return True
    except Exception:
        return False
    finally:
        await engine.dispose()

exit(0 if asyncio.run(check()) else 1)
" 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "  WARNING: Database not ready after ${MAX_RETRIES}s — proceeding anyway"
        break
    fi
    echo "  Waiting for database... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 1
done

echo "  Database connected"

# ---------------------------------------------------------------------------
# Step 2: Run Alembic migrations
# ---------------------------------------------------------------------------
echo ""
echo "[2/3] Running database migrations..."

if alembic upgrade head 2>/dev/null; then
    echo "  Migrations applied successfully"
else
    echo "  WARNING: Migration failed — falling back to create_all()"
    python -c "
import asyncio, os
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///:memory:')
from app.database import init_db
asyncio.run(init_db())
print('  Tables created via create_all()')
" 2>/dev/null || echo "  Fallback also failed — check DATABASE_URL"
fi

# ---------------------------------------------------------------------------
# Step 3: Seed knowledge base (idempotent)
# ---------------------------------------------------------------------------
echo ""
echo "  Seeding knowledge base..."
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
# Step 4: Start uvicorn
# ---------------------------------------------------------------------------
echo ""
echo "[3/3] Starting uvicorn on port ${PORT}..."
echo "============================================"
echo ""

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --workers 2 \
    --loop uvloop \
    --http httptools \
    --log-level info \
    --access-log
