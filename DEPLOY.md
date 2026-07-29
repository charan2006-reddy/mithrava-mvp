# Mithrava Deployment Guide — Free Tier (Testing)

**Platform**: Vercel (Frontend) + Fly.io (Backend) + Supabase (Database)  
**Time**: ~30 minutes  
**Cost**: $0 forever (free tiers)  
**Trade-off**: Backend sleeps after ~15 min idle, 30-60s cold start on first request  

---

## Architecture

```
                    User's Phone Browser
                           │
                           │ HTTPS (free SSL)
                           ▼
              ┌────────────────────────┐
              │   Vercel Edge Network  │
              │   (FREE — Hobby tier)  │
              │  ┌──────────────────┐  │
              │  │  Next.js Frontend│  │
              │  └────────┬─────────┘  │
              └───────────┼────────────┘
                          │ API calls (HTTPS)
                          ▼
              ┌────────────────────────┐
              │   Fly.io              │
              │   (FREE — 256MB RAM)  │
              │  ┌──────────────────┐  │
              │  │  FastAPI Backend │  │
              │  └────────┬─────────┘  │
              └───────────┼────────────┘
                          │ SQL queries
                          ▼
              ┌────────────────────────┐
              │   Supabase            │
              │   (FREE — 500MB DB)   │
              │  ┌──────────────────┐  │
              │  │  PostgreSQL 15   │  │
              │  │  + pgvector      │  │
              │  └──────────────────┘  │
              └────────────────────────┘
```

---

## Prerequisites

- [ ] GitHub account with the code pushed to a repository
- [ ] Fly.io account: https://fly.io (sign up with GitHub)
- [ ] Supabase account: https://supabase.com (sign up with GitHub)
- [ ] Vercel account: https://vercel.com (sign up with GitHub)
- [ ] API keys: Gemini, OpenWeather
- [ ] Fly.io CLI installed: `curl -L https://fly.io/install.sh | sh`

---

## Step 1: Push Code to GitHub

```bash
cd "C:\Users\srinivasreddy\mithrava mvp"
git add .
git commit -m "Add Fly.io + Supabase deployment configs"
git push
```

---

## Step 2: Create Supabase Database (3 minutes)

### 2.1 Create Project

1. Go to https://supabase.com/dashboard
2. Click **"New Project"**
3. Choose your organization (or create one)
4. Set project details:
   - **Name**: `mithrava`
   - **Database Password**: `your-strong-password` (save this!)
   - **Region**: `Southeast Asia (Mumbai)` or closest to India
5. Click **"Create new project"**
6. Wait ~2 minutes for provisioning

### 2.2 Get Connection String

1. In your project, go to **"Settings"** → **"Database"**
2. Scroll to **"Connection string"**
3. Copy the **"URI"** format connection string:
   ```
   postgresql://postgres.YOUR_PROJECT:YOUR_PASSWORD@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
   ```

### 2.3 Enable pgvector Extension

1. Go to **"SQL Editor"** in Supabase dashboard
2. Run this SQL:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Click **"Run"**

### 2.4 Update Connection String for Async

Change `postgresql://` to `postgresql+asyncpg://` in your connection string:

```
Original:  postgresql://postgres.xxx:password@host:6543/postgres
For app:    postgresql+asyncpg://postgres.xxx:password@host:6543/postgres
```

Save this — you'll need it in Step 3.

---

## Step 3: Deploy Backend to Fly.io (10 minutes)

### 3.1 Login to Fly.io

```bash
fly auth login
```

This opens a browser window — sign in with GitHub.

### 3.2 Launch the App

```bash
cd "C:\Users\srinivasreddy\mithrava mvp"
fly launch --copy-config --name mithrava-api
```

Answer the prompts:
- **Overwrite existing fly.toml?**: Yes
- **App Name**: `mithrava-api`
- **Organization**: (your account)
- **Region**: Singapore (or closest to you)

### 3.3 Set Secrets (Environment Variables)

```bash
# Database (from Supabase)
fly secrets set DATABASE_URL="postgresql+asyncpg://postgres.xxx:password@host:6543/postgres"

# Security
fly secrets set SECRET_KEY="$(openssl rand -hex 32)"

# CORS (your Vercel URL — set after Step 4)
fly secrets set CORS_ORIGINS="https://mithrava-mvp.vercel.app"

# API Keys
fly secrets set GEMINI_API_KEY="..."
fly secrets set OPENWEATHER_API_KEY="..."
```

> **Note**: Set `CORS_ORIGINS` after deploying the frontend (Step 4).

### 3.4 Deploy

```bash
fly deploy
```

First deploy takes ~5-8 minutes (building Docker image).

### 3.5 Verify

```bash
fly status
fly logs
```

Or visit: `https://mithrava-api.fly.dev/health`

You should see: `{"status": "healthy"}`

---

## Step 4: Deploy Frontend to Vercel (5 minutes)

### 4.1 Import Project

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import your `mithrava-mvp` GitHub repository

### 4.2 Configure

1. **Framework Preset**: Next.js (auto-detected)
2. **Root Directory**: `./frontend`
3. **Build Command**: `npm run build`
4. **Install Command**: `npm install --legacy-peer-deps`

### 4.3 Set Environment Variables

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://mithrava-api.fly.dev/api/v1` |

### 4.4 Deploy

1. Click **"Deploy"**
2. Wait ~2-3 minutes
3. Your app is live at: `https://mithrava-mvp.vercel.app`

---

## Step 5: Final Configuration

### 5.1 Update CORS on Fly.io

```bash
fly secrets set CORS_ORIGINS="https://mithrava-mvp.vercel.app"
```

### 5.2 Test End-to-End

1. Open `https://mithrava-mvp.vercel.app`
2. Register with a phone number
3. Test the main features

---

## Your URLs

```
Frontend:  https://mithrava-mvp.vercel.app         (Vercel — FREE)
Backend:   https://mithrava-api.fly.dev             (Fly.io — FREE)
Database:  Supabase Dashboard                       (Supabase — FREE)
```

**Total monthly cost: $0**

---

## How Cold Start Works

```
When your app has been idle for ~15 minutes:

  User visits → "Loading..." (30-60 seconds)
                    │
                    │ Fly.io is waking up your backend
                    │ Starting Python, connecting to DB
                    │
                    ▼
              Dashboard appears
                    │
                    │ From here, app is FAST
                    │ (until idle for 15 min again)
                    ▼
              User interacts normally
```

**Tip**: First request is slow, subsequent requests are instant.

---

## Useful Commands

```bash
# Check status
fly status

# View logs
fly logs

# Restart app
fly apps restart mithrava-api

# Update secrets
fly secrets set KEY=VALUE

# List secrets
fly secrets list

# Scale (if needed later)
fly scale count 2    # Run 2 instances ($$$ — not free)

# Open Supabase dashboard
# https://supabase.com/dashboard → your project
```

---

## Troubleshooting

### Backend won't start
```bash
fly logs
```
Common issues:
- `DATABASE_URL` wrong format (must start with `postgresql+asyncpg://`)
- pgvector extension not enabled in Supabase
- Password contains special characters (encode them in URL)

### Frontend can't reach backend
- Check `NEXT_PUBLIC_API_URL` in Vercel env vars
- Make sure it ends with `/api/v1`
- Check `CORS_ORIGINS` matches your Vercel URL exactly

### Database connection refused
- Supabase project might be pausing (free tier pauses after 7 days no activity)
- Go to Supabase dashboard → click "Restore" if paused
- Make sure you're using port 6543 (pooler), not 5432

### Cold start too slow
- This is normal for free tier
- Consider upgrading to paid tier ($5/mo) for always-on backend
- Or use AWS credits (Option 1) for instant response

---

## Upgrade Path (When Ready)

```
Current (Free):
  Fly.io:   256MB RAM, sleeps when idle
  Supabase: 500MB DB, pauses after 7 days

Upgrade Option 1 — Fly.io paid ($5/mo):
  - 512MB RAM
  - No sleep (always on)
  - Instant response

Upgrade Option 2 — Railway ($5-10/mo):
  - Better DX
  - Managed PostgreSQL
  - No cold starts

Upgrade Option 3 — AWS credits:
  - EC2 + RDS ($27/mo from credits)
  - Professional infrastructure
  - 5 months runway
```
