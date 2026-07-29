#!/bin/bash
# =============================================================================
# Mithrava — One-Click Deploy Script
# Run: bash deploy.sh
# You just paste your credentials when prompted
# =============================================================================

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║        Mithrava — Free Deployment ($0/month)           ║"
echo "║        Vercel + Fly.io + Supabase                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ─── Step 0: Check prerequisites ────────────────────────────────────────────
echo "▶ Checking prerequisites..."

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install: https://git-scm.com"
    exit 1
fi

if ! command -v flyctl &> /dev/null && ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI not found."
    echo "   Install: curl -L https://fly.io/install.sh | sh"
    echo "   Then run: fly auth login"
    exit 1
fi

echo "✅ Git found"
echo "✅ Fly CLI found"
echo ""

# ─── Step 1: Collect credentials ────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  STEP 1: Enter your credentials                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "If you don't have these yet, press Ctrl+C to stop,"
echo "get them first, then run this script again."
echo ""

read -p "Supabase connection string (postgresql+asyncpg://...): " DATABASE_URL
read -p "OpenWeather API key: " OPENWEATHER_API_KEY
read -p "Gemini API key (FREE — from aistudio.google.com): " GEMINI_API_KEY


# Generate secret key automatically
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || head -c 64 /dev/urandom | xxd -p | tr -d '\n' | head -c 64)

if [ -z "$SECRET_KEY" ]; then
    read -p "Secret key (or press Enter to generate): " SECRET_KEY
fi

echo ""
echo "✅ Credentials collected"
echo ""

# ─── Step 2: Git push ────────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  STEP 2: Pushing code to GitHub                         ║"
echo "╚══════════════════════════════════════════════════════════╝"

git add -A
git commit -m "Deploy: Fly.io + Supabase + Vercel" --allow-empty 2>/dev/null || true

# Check if remote exists
if git remote get-url origin &>/dev/null; then
    git push origin HEAD 2>/dev/null || echo "⚠ Push failed — push manually: git push"
else
    echo "⚠ No git remote set. Push manually:"
    echo "   git remote add origin https://github.com/YOU/mithrava-mvp.git"
    echo "   git push -u origin main"
fi

echo "✅ Code pushed"
echo ""

# ─── Step 3: Deploy to Fly.io ────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  STEP 3: Deploying backend to Fly.io                    ║"
echo "╚══════════════════════════════════════════════════════════╝"

# Login (opens browser)
echo "▶ Logging into Fly.io (browser will open)..."
fly auth login 2>/dev/null || flyctl auth login

# Launch app (first time) or use existing
if fly status --app mithrava-api &>/dev/null; then
    echo "▶ App 'mithrava-api' already exists"
else
    echo "▶ Creating new Fly.io app..."
    fly launch --copy-config --name mithrava-api --no-deploy --yes 2>/dev/null || \
    flyctl launch --copy-config --name mithrava-api --no-deploy --yes
fi

# Set secrets
echo "▶ Setting environment variables..."
fly secrets set DATABASE_URL="$DATABASE_URL" --app mithrava-api
fly secrets set SECRET_KEY="$SECRET_KEY" --app mithrava-api
fly secrets set OPENWEATHER_API_KEY="$OPENWEATHER_API_KEY" --app mithrava-api

if [ -n "$GEMINI_API_KEY" ]; then
    fly secrets set GEMINI_API_KEY="$GEMINI_API_KEY" --app mithrava-api
    echo "  ✅ Gemini API key set (primary LLM + voice + embeddings)"
fi

# Deploy
echo "▶ Deploying (this takes 5-8 minutes)..."
fly deploy --app mithrava-api

# Get the URL
BACKEND_URL="https://mithrava-api.fly.dev"
echo ""
echo "✅ Backend deployed: $BACKEND_URL"
echo ""

# ─── Step 4: Vercel (manual — needs browser) ────────────────────────────────
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  STEP 4: Deploy frontend to Vercel (2 minutes)          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  1. Go to: https://vercel.com/new"
echo "  2. Import your GitHub repo"
echo  "  3. Root Directory: ./frontend"
echo "  4. Install Command: npm install --legacy-peer-deps"
echo "  5. Environment Variables:"
echo "     NEXT_PUBLIC_API_URL = ${BACKEND_URL}/api/v1"
echo "  6. Click Deploy"
echo "  7. In Settings → General → rename to: mithrava-mvp"
echo ""
echo "  Your frontend URL will be: https://mithrava-mvp.vercel.app"
echo ""

# ─── Step 5: Update CORS ────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  STEP 5: After Vercel deploy, run this command:         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  fly secrets set CORS_ORIGINS='https://mithrava-mvp.vercel.app' --app mithrava-api"
echo ""

# ─── Done! ──────────────────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    DEPLOYMENT COMPLETE                  ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  Frontend:  https://mithrava-mvp.vercel.app             ║"
echo "║  Backend:   https://mithrava-api.fly.dev                 ║"
echo "║  Database:  Supabase Dashboard                          ║"
echo "║                                                          ║"
echo "║  Total cost: $0/month                                   ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Commands for later:"
echo "  fly status --app mithrava-api      # Check backend status"
echo "  fly logs --app mithrava-api        # View backend logs"
echo "  fly secrets list --app mithrava-api # List env vars"
echo ""
