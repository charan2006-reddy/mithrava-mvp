# Phase 1: Architecture Document

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Mobile     │  │   Desktop    │  │   Tablet     │             │
│  │   Browser    │  │   Browser    │  │   Browser    │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         └──────────────────┼──────────────────┘                     │
│                            │ HTTPS                                  │
└────────────────────────────┼────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────┐
│                    NGINX REVERSE PROXY                              │
│                                                                     │
│  ┌─────────────────────────┼─────────────────────────────────────┐  │
│  │ Rate Limiting (100/min) │ Security Headers │ Gzip │ WebSocket │  │
│  └─────────────────────────┼─────────────────────────────────────┘  │
│                            │                                        │
│         ┌──────────────────┼──────────────────┐                     │
│         │ /api/*           │                  │ /                   │
│         ▼                  │                  ▼                     │
│  ┌──────────────┐          │          ┌──────────────┐             │
│  │   Backend    │          │          │   Frontend   │             │
│  │   (FastAPI)  │          │          │   (Next.js)  │             │
│  │   Port 8000  │          │          │   Port 3000  │             │
│  └──────┬───────┘          │          └──────────────┘             │
│         │                  │                                        │
└─────────┼──────────────────┼────────────────────────────────────────┘
          │                  │
┌─────────┼──────────────────┼────────────────────────────────────────┐
│         │       DATA LAYER │                                        │
│         │                  │                                        │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────────────┐             │
│  │  PostgreSQL  │  │    Redis     │  │  File Storage│             │
│  │  + pgvector  │  │    Cache     │  │  (Local/S3)  │             │
│  │  Port 5432   │  │  Port 6379   │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────┐
│                      AI/ML LAYER                                    │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Ollama     │  │   OpenAI     │  │   Custom     │             │
│  │  (Llama 3.1) │  │  (GPT-4o)   │  │   Models     │             │
│  │   Chat       │  │  Vision+STT  │  │  (Future)    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Backend Architecture (Clean Architecture)

```
backend/app/
│
├── main.py                    # Application entry point
│   ├── FastAPI app creation
│   ├── Middleware registration
│   ├── Route registration
│   └── Lifecycle events (startup/shutdown)
│
├── config.py                  # Configuration management
│   └── Pydantic Settings (env vars → typed config)
│
├── database.py                # Database connection
│   ├── Async engine creation
│   ├── Session factory
│   └── Base model class
│
├── dependencies.py            # Dependency injection
│   ├── get_current_user()
│   ├── get_current_admin()
│   └── get_db()
│
├── models/                    # Data models (ORM)
│   ├── farmer.py              # SQLAlchemy models
│   ├── crop.py
│   └── ...
│
├── schemas/                   # Validation schemas
│   ├── auth.py                # Pydantic models
│   ├── farmer.py
│   └── ...
│
├── repositories/              # Data access layer
│   ├── farmer_repo.py         # Database queries
│   ├── crop_repo.py
│   └── finance_repo.py
│
├── services/                  # Business logic layer
│   ├── auth_service.py        # Authentication logic
│   ├── farmer_service.py
│   ├── crop_service.py
│   ├── disease_service.py
│   ├── weather_service.py
│   └── mitra_service.py
│
├── api/v1/                    # API route handlers
│   ├── router.py              # Route aggregation
│   ├── auth.py                # Endpoint definitions
│   ├── farmers.py
│   └── ...
│
├── core/                      # Core infrastructure
│   ├── security.py            # JWT + password hashing
│   ├── otp.py                 # OTP generation
│   ├── llm.py                 # AI/ML integration
│   ├── weather.py             # Weather API
│   └── storage.py             # File storage
│
└── middleware/                 # Request/response middleware
    ├── rate_limit.py          # SlowAPI rate limiting
    ├── security.py            # Security headers
    └── audit.py               # Audit logging
```

### Request Flow

```
Client Request
    │
    ▼
Nginx (rate limit, security headers)
    │
    ▼
FastAPI Middleware (CORS, audit log)
    │
    ▼
Route Handler (api/v1/*.py)
    │
    ▼
Dependencies (get_current_user, get_db)
    │
    ▼
Service Layer (business logic)
    │
    ▼
Repository Layer (database queries)
    │
    ▼
SQLAlchemy ORM → PostgreSQL
    │
    ▼
Response (Pydantic serialization → JSON)
```

## Frontend Architecture

```
frontend/src/
│
├── app/                       # Next.js App Router
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Landing page
│   ├── (auth)/                # Auth route group
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   └── (dashboard)/           # Dashboard route group
│       ├── layout.tsx         # Dashboard layout
│       ├── page.tsx           # Home
│       ├── crops/
│       ├── disease/
│       ├── weather/
│       └── ...
│
├── components/                # React components
│   ├── ui/                    # Shadcn primitives
│   ├── layout/                # Layout components
│   ├── shared/                # Shared components
│   ├── mitra/                 # AI assistant
│   ├── crops/                 # Crop-specific
│   └── ...
│
├── hooks/                     # Custom React hooks
│   ├── useAuth.ts
│   ├── useLanguage.ts
│   ├── useMitra.ts
│   └── useWeather.ts
│
├── stores/                    # Zustand state
│   ├── authStore.ts
│   ├── uiStore.ts
│   └── mitraStore.ts
│
├── services/                  # API clients
│   ├── api.ts                 # Axios instance
│   ├── authService.ts
│   └── ...
│
├── types/                     # TypeScript types
│   ├── api.ts
│   ├── auth.ts
│   └── ...
│
└── lib/                       # Utilities
    ├── utils.ts
    ├── constants.ts
    └── languages.ts
```

### Component Hierarchy

```
App
├── ThemeProvider
├── Toaster
└── Layout
    ├── Header
    │   ├── Logo
    │   ├── LanguageSwitcher
    │   ├── NotificationBell
    │   └── ThemeToggle
    ├── Sidebar (desktop)
    │   ├── NavItems
    │   └── FarmerInfo
    ├── MainContent
    │   └── Page (children)
    ├── BottomNav (mobile)
    │   ├── Home
    │   ├── Disease
    │   ├── Mitra (center)
    │   ├── Market
    │   └── More
    └── MitraWidget (floating)
        ├── MitraChat
        │   ├── MitraMessage (list)
        │   └── TypingIndicator
        ├── MitraInput
        │   ├── TextInput
        │   ├── SendButton
        │   └── VoiceButton
        └── MitraQuickActions
```

## Database Schema (ER Diagram)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   farmers   │────<│    lands    │     │  otp_codes  │
│             │     │             │     │             │
│ id (UUID)   │     │ id (UUID)   │     │ id (UUID)   │
│ name        │     │ farmer_id   │     │ phone       │
│ phone       │     │ name        │     │ code        │
│ email       │     │ area_acres  │     │ expires_at  │
│ city        │     │ soil_type   │     │ used        │
│ state       │     └─────────────┘     └─────────────┘
│ language    │
│ auth_provider│    ┌─────────────┐     ┌─────────────┐
└──────┬──────┘     │   crops     │     │ disease_    │
       │            │             │────<│   scans     │
       │            │ id (UUID)   │     │             │
       ├───────────<│ farmer_id   │     │ id (UUID)   │
       │            │ land_id     │     │ farmer_id   │
       │            │ crop_name   │     │ crop_id     │
       │            │ status      │     │ image_url   │
       │            └─────────────┘     │ disease_name│
       │                                │ confidence  │
       │            ┌─────────────┐     │ treatment   │
       ├───────────<│  expenses   │     └─────────────┘
       │            │             │
       │            │ id (UUID)   │     ┌─────────────┐
       │            │ farmer_id   │     │   income    │
       │            │ category    │     │             │
       │            │ item        │     │ id (UUID)   │
       │            │ amount      │     │ farmer_id   │
       │            │ date        │     │ amount      │
       │            └─────────────┘     │ date        │
       │                                └─────────────┘
       │
       ├───────────<┌─────────────┐
       │            │mitra_convos │
       │            │             │
       │            │ id (UUID)   │     ┌─────────────┐
       │            │ farmer_id   │────<│mitra_msgs   │
       │            │ language    │     │             │
       │            └─────────────┘     │ id (UUID)   │
       │                                │ convo_id    │
       │            ┌─────────────┐     │ role        │
       ├───────────<│  forum_     │     │ content     │
       │            │   posts     │     │ intent      │
       │            │             │     └─────────────┘
       │            │ id (UUID)   │
       │            │ farmer_id   │
       │            │ content     │
       │            └─────────────┘
       │
       ├───────────<┌─────────────┐
       │            │notificatns  │
       │            │             │
       │            │ id (UUID)   │
       │            │ farmer_id   │
       │            │ type        │
       │            │ title       │
       │            │ is_read     │
       │            └─────────────┘
       │
       └───────────<┌─────────────┐
                    │audit_logs   │
                    │             │
                    │ id (UUID)   │
                    │ farmer_id   │
                    │ action      │
                    │ entity_type │
                    │ entity_id   │
                    │ ip_address  │
                    └─────────────┘
```

## API Design

### RESTful Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/v1/auth/send-otp | Send OTP to phone | No |
| POST | /api/v1/auth/verify-otp | Verify OTP + login | No |
| POST | /api/v1/auth/register | Register new farmer | No |
| POST | /api/v1/auth/refresh | Refresh access token | Yes |
| GET | /api/v1/auth/me | Get current user | Yes |
| GET | /api/v1/farmers | List all farmers | Admin |
| PUT | /api/v1/farmers/me | Update profile | Yes |
| GET | /api/v1/crops | List farmer's crops | Yes |
| POST | /api/v1/crops | Create crop | Yes |
| POST | /api/v1/disease/analyze | Analyze leaf image | Yes |
| GET | /api/v1/weather/current/{city} | Current weather | Yes |
| GET | /api/v1/market/prices | Market prices | Yes |
| GET | /api/v1/finance/summary | Financial summary | Yes |
| POST | /api/v1/finance/expenses | Add expense | Yes |
| GET | /api/v1/vendors | List vendors | Yes |
| GET | /api/v1/forum | List forum posts | Yes |
| POST | /api/v1/mitra/chat | Chat with Mitra | Yes |
| POST | /api/v1/mitra/voice | Voice message to Mitra | Yes |
| GET | /health | Health check | No |

### Response Format

```json
{
  "success": true,
  "message": "Operation completed",
  "data": { ... },
  "errors": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

## Security Architecture

```
┌─────────────────────────────────────────────────────┐
│                  SECURITY LAYERS                     │
│                                                     │
│  Layer 1: Nginx                                     │
│  ├── Rate Limiting (100/min general)                │
│  ├── Security Headers (CSP, HSTS, X-Frame)         │
│  └── TLS Termination                                │
│                                                     │
│  Layer 2: FastAPI Middleware                        │
│  ├── CORS (allowed origins only)                    │
│  ├── Audit Logging (all mutations)                  │
│  └── Request Validation                             │
│                                                     │
│  Layer 3: Authentication                            │
│  ├── JWT Access Tokens (15min)                      │
│  ├── Refresh Token Rotation                         │
│  ├── OTP Verification (6-digit, 5min)               │
│  └── Role-Based Access (farmer/admin)               │
│                                                     │
│  Layer 4: Authorization                             │
│  ├── Farmer can only access own data                │
│  ├── Admin can access all data                      │
│  └── Ownership validation on every request          │
│                                                     │
│  Layer 5: Data Protection                           │
│  ├── SQL Injection (SQLAlchemy ORM)                 │
│  ├── XSS (React auto-escaping)                      │
│  ├── CSRF (SameSite cookies)                        │
│  └── Input Validation (Pydantic schemas)            │
│                                                     │
│  Layer 6: Infrastructure                            │
│  ├── Non-root Docker containers                     │
│  ├── Secrets in environment variables               │
│  ├── Database encryption at rest                    │
│  └── HTTPS in transit                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS CLOUD                             │
│                                                             │
│  ┌──────────────┐     ┌──────────────┐                     │
│  │   Route 53   │────▶│  CloudFront  │                     │
│  │   (DNS)      │     │   (CDN)      │                     │
│  └──────────────┘     └──────┬───────┘                     │
│                              │                              │
│                     ┌────────┴────────┐                     │
│                     │                  │                     │
│               ┌─────▼─────┐    ┌──────▼──────┐            │
│               │   Vercel  │    │    ECS      │            │
│               │ (Frontend)│    │ (Fargate)   │            │
│               └───────────┘    │ (Backend)   │            │
│                                └──────┬──────┘            │
│                                       │                     │
│                        ┌──────────────┼──────────────┐     │
│                        │              │              │     │
│                  ┌─────▼─────┐ ┌──────▼──────┐ ┌────▼───┐│
│                  │    RDS    │ │ ElastiCache │ │   S3   ││
│                  │(PostgreSQL│ │   (Redis)   │ │(Files) ││
│                  │ + pgvector)│ └─────────────┘ └────────┘│
│                  └───────────┘                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
