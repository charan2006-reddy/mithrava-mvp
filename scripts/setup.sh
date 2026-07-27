#!/usr/bin/env bash
# =============================================================================
# Mithrava — Linux / macOS Setup Script
# Sets up the full development environment with Docker.
# Usage: ./scripts/setup.sh
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helpers
info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
success() { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }
divider() { echo ""; echo -e "${BLUE}============================================================${NC}"; }

divider
echo -e "  ${GREEN}Mithrava — Development Environment Setup${NC}"
divider
echo ""

# -------------------------------------------------------------------------
# Detect Docker Compose command (v1 vs v2)
# -------------------------------------------------------------------------
detect_compose() {
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        error "Docker Compose is not installed."
        echo "  Install from: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# -------------------------------------------------------------------------
# Step 1: Check prerequisites
# -------------------------------------------------------------------------
info "[1/6] Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    error "Docker is not installed or not in PATH."
    echo "  Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

detect_compose

success "Docker: $(docker --version)"
success "Compose: $($COMPOSE_CMD version 2>/dev/null || echo 'OK')"
echo ""

# -------------------------------------------------------------------------
# Step 2: Create .env files if they don't exist
# -------------------------------------------------------------------------
info "[2/6] Setting up environment files..."

if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        success "Created backend/.env from .env.example"
    else
        warn "backend/.env.example not found. Creating minimal backend/.env..."
        cat > backend/.env << 'ENVEOF'
DATABASE_URL=postgresql+asyncpg://mithrava:mithrava@localhost:5432/mithrava
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
OPENAI_API_KEY=sk-your-key-here
ENVEOF
        success "Created backend/.env with defaults"
    fi
else
    info "  backend/.env already exists, skipping."
fi

if [ ! -f "frontend/.env.local" ]; then
    if [ -f "frontend/.env.example" ]; then
        cp frontend/.env.example frontend/.env.local
        success "Created frontend/.env.local from .env.example"
    else
        warn "Creating frontend/.env.local with defaults..."
        cat > frontend/.env.local << 'ENVEOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
ENVEOF
        success "Created frontend/.env.local"
    fi
else
    info "  frontend/.env.local already exists, skipping."
fi
echo ""

# -------------------------------------------------------------------------
# Step 3: Create required directories
# -------------------------------------------------------------------------
info "[3/6] Creating required directories..."

mkdir -p backend/app/uploads backend/logs frontend/.next

success "Directories created."
echo ""

# -------------------------------------------------------------------------
# Step 4: Start Docker services
# -------------------------------------------------------------------------
info "[4/6] Starting Docker services (this may take a few minutes on first run)..."
echo ""

$COMPOSE_CMD up -d --build

success "Docker services started."
echo ""

# -------------------------------------------------------------------------
# Step 5: Wait for services to be healthy
# -------------------------------------------------------------------------
info "[5/6] Waiting for services to become healthy..."
echo "     (This may take 1-3 minutes on first run)"
echo ""

MAX_RETRIES=60
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # Check if backend container reports healthy
    HEALTHY=$($COMPOSE_CMD ps --format json 2>/dev/null | grep -c '"healthy"' || true)
    RUNNING=$($COMPOSE_CMD ps --format json 2>/dev/null | grep -c '"running"' || true)

    if [ "$HEALTHY" -ge 2 ] 2>/dev/null; then
        success "All services are healthy!"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    printf "\r     Waiting... (%d/%d)" $RETRY_COUNT $MAX_RETRIES
    sleep 5
done

if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo ""
    warn "Services may not be fully healthy yet."
    warn "Run '$COMPOSE_CMD ps' to check status."
    warn "Run '$COMPOSE_CMD logs' to check logs."
fi
echo ""

# -------------------------------------------------------------------------
# Step 6: Seed the database
# -------------------------------------------------------------------------
info "[6/6] Seeding database with sample data..."

$COMPOSE_CMD exec -T backend python scripts/seed_db.py || {
    warn "Seed script encountered an error."
    warn "You may need to run it manually:"
    warn "  $COMPOSE_CMD exec backend python scripts/seed_db.py"
}

echo ""
divider
echo -e "  ${GREEN}Setup Complete!${NC}"
divider
echo ""
echo "  Services:"
echo "    Frontend:  http://localhost:3000"
echo "    Backend:   http://localhost:8000"
echo "    API Docs:  http://localhost:8000/docs"
echo "    Nginx:     http://localhost:80"
echo ""
echo "  Useful Commands:"
echo "    View logs:     $COMPOSE_CMD logs -f"
echo "    Stop services: $COMPOSE_CMD down"
echo "    Restart:       $COMPOSE_CMD restart"
echo "    Seed DB:       $COMPOSE_CMD exec backend python scripts/seed_db.py"
echo ""

# Open browser (platform-aware)
if command -v xdg-open &> /dev/null; then
    info "Opening browser..."
    xdg-open http://localhost:3000 2>/dev/null &
elif command -v open &> /dev/null; then
    info "Opening browser..."
    open http://localhost:3000 2>/dev/null &
fi
