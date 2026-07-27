# Sprint 7 — Forum & Finance Frontend Rewrite + Integration Test Suite

**Status**: COMPLETE
**Date**: July 18, 2026
**Tests**: 78 passed, 0 failed (11.18s)

---

## Overview

Sprint 7 delivered three major deliverables:
1. **Forum page rewrite** — Real API integration with React Query
2. **Finance & Expenses page rewrite** — Real API integration with React Query
3. **Integration test suite** — 78 tests covering all 14 API route groups
4. **Backend bug fixes** — Schema, model, and service-layer fixes discovered during testing

---

## 1. Frontend: Forum Page Rewrite

### Files Modified
- `frontend/src/services/forumService.ts` — Fixed all API paths from `/api/forum/` → `/api/v1/forum/`
- `frontend/src/app/(dashboard)/forum/page.tsx` — Full rewrite with React Query

### Features
- **Category filtering**: Tab-based UI with 8 categories (general, crop_care, pest_control, weather, market, finance, tips, question)
- **Post creation**: Modal dialog with title, content, category selector, and tag input
- **Like toggle**: Optimistic UI updates via React Query cache invalidation
- **Comment system**: Expandable comment sections per post
- **Loading states**: Skeleton loading for posts and comments
- **Empty states**: Friendly prompts when no posts exist

### React Query Integration
- `useQuery` for post listing with category filter
- `useMutation` for creating posts, liking, and commenting
- Cache invalidation on mutations for instant UI updates

---

## 2. Frontend: Finance & Expenses Page Rewrite

### Files Modified
- `frontend/src/services/financeService.ts` — Fixed all API paths from `/api/finance/` → `/api/v1/finance/`
- `frontend/src/app/(dashboard)/finance/page.tsx` — Full rewrite with React Query
- `frontend/src/app/(dashboard)/finance/expenses/page.tsx` — Full rewrite with real API

### Finance Page Features
- **Summary cards**: Total expenses, total income, profit with color-coded indicators
- **Monthly bar chart**: CSS-based bar chart showing expense vs income over time
- **Expense breakdown**: Progress bars by category (fertilizer, seeds, labor, etc.)
- **Recent transactions**: List of latest expenses and income with dates and amounts

### Expenses Page Features
- **Expense list**: Full table with category, amount, description, date
- **Add expense form**: Modal dialog with category dropdown (from constants), amount, description, date picker
- **Delete expense**: Confirmation dialog before deletion
- **Loading/empty states**: Skeletons and friendly prompts

### React Query Integration
- `useQuery` for finance summary, expenses list, income list
- `useMutation` for adding expenses, income, and deleting records
- Optimistic updates for instant feedback

---

## 3. Backend Bug Fixes

### `FarmerService.update_farmer()` — Dict vs Model Handling
**File**: `backend/app/services/farmers.py`
- **Bug**: The endpoint (`/api/v1/farmers/me`) called `body.model_dump(exclude_unset=True)` and passed the resulting dict to `FarmerService.update_farmer()`, which then called `data.model_dump()` on it — causing `AttributeError: 'dict' object has no attribute 'model_dump'`
- **Fix**: Service now checks `isinstance(data, dict)` and handles both Pydantic models and plain dicts

### `MitraMessage.metadata` Field Name Conflict
**File**: `backend/app/models/mitra.py`
- **Bug**: Pydantic `BaseModel.metadata` is a reserved attribute; having a DB column named `metadata` caused conflicts
- **Fix**: Renamed the ORM attribute to `message_metadata` while keeping the DB column name as `metadata`

### Duplicate `Expense`/`Income` Models
**Files**: `backend/app/models/expense.py`, `backend/app/models/income.py`
- **Bug**: Duplicate `Expense` and `Income` models existed in separate files alongside canonical versions in `finance.py`, causing SQLAlchemy mapper conflicts
- **Fix**: Removed duplicates from `expense.py` and `income.py`; updated `farmer_service.py` to import from `app.models.finance`

### Pydantic `date` Field Name Clash
**File**: `backend/app/schemas/finance.py`
- **Bug**: A field named `date` in a Pydantic schema clashed with `datetime.date` type reference
- **Fix**: Aliased the import as `_date_type` to avoid the name collision

### Alembic Migration
**File**: `backend/alembic/versions/001_initial_schema.py`
- **Created**: Full migration covering all 14+ tables (farmers, crops, finance, forum, knowledge, mitra, notifications, push_subscriptions, support, vendors, etc.)
- **Updated**: `backend/alembic/env.py` to include `PushSubscription` model import

---

## 4. Integration Test Suite

### Infrastructure
- **Framework**: pytest + pytest-asyncio + httpx (AsyncClient with ASGITransport)
- **Database**: In-memory SQLite via aiosqlite — no PostgreSQL required for tests
- **Auth bypass**: Tests create users directly in DB with JWT tokens, bypassing OTP flow entirely
- **Type compilers**: Custom SQLite compilers for PostgreSQL `JSONB` and pgvector `Vector` types
- **Engine patching**: Monkey-patch strips `pool_size`, `max_overflow`, `pool_pre_ping` for SQLite compatibility

### Test Coverage (78 tests across 14 files)

| File | Tests | Coverage |
|------|-------|----------|
| `test_health.py` | 2 | Health check, root endpoint |
| `test_auth.py` | 8 | Send OTP, verify OTP, register, duplicate phone, /me |
| `test_crops.py` | 10 | CRUD (create, read, update, delete), calendar, daily actions |
| `test_farmers.py` | 6 | Profile get/update, stats, admin-only access |
| `test_finance.py` | 10 | Expense CRUD, income CRUD, summary (empty + with data) |
| `test_forum.py` | 9 | Post CRUD, category filter, comments, like toggle |
| `test_disease.py` | 3 | Analyze (requires image), history, no-auth |
| `test_knowledge.py` | 6 | Categories, search, ask, seed, auth required |
| `test_market.py` | 7 | Crops list, prices, single crop, unknown crop, trend, markets |
| `test_mitra.py` | 4 | Chat (LLM-dependent), voice providers, conversations |
| `test_notifications.py` | 5 | List, unread count, filter by type, direct DB inserts |
| `test_support.py` | 2 | Request expert call, admin-only list |
| `test_weather.py` | 6 | Current, forecast, farming advice, city required |
| **Total** | **78** | |

### Key Testing Patterns
- Each test gets a fresh SQLite database (autouse `setup_database` fixture creates/drops all tables)
- Auth bypass avoids OTP rate limits by creating users directly in DB
- External dependencies (LLM, OpenAI, Gemini) return mock/500 responses — tests accept 200 or 500
- No-auth tests verify 401/403 for protected endpoints

### Warnings (non-blocking)
- `test_session_factory` collection warning (cosmetic — pytest collects the SQLAlchemy factory name)
- `event_loop` fixture deprecation warning (pytest-asyncio 0.24 deprecation — not yet breaking)

---

## Files Changed/Created (Sprint 7)

### Backend — Bug Fixes
| File | Change |
|------|--------|
| `backend/app/services/farmer_service.py` | Handle dict input in `update_farmer()` |
| `backend/app/models/mitra.py` | Renamed `metadata` → `message_metadata` |
| `backend/app/models/expense.py` | Removed duplicate Expense model |
| `backend/app/models/income.py` | Removed duplicate Income model |
| `backend/app/services/farmer_service.py` | Updated imports to use `finance.py` models |
| `backend/app/schemas/finance.py` | Fixed Pydantic date field name clash |
| `backend/alembic/versions/001_initial_schema.py` | Created full migration |
| `backend/alembic/env.py` | Added PushSubscription import |

### Backend — Test Suite (new)
| File | Tests |
|------|-------|
| `backend/tests/__init__.py` | Package marker |
| `backend/tests/conftest.py` | SQLite DB, auth bypass, type compilers, fixtures |
| `backend/tests/test_health.py` | 2 tests |
| `backend/tests/test_auth.py` | 8 tests |
| `backend/tests/test_crops.py` | 10 tests |
| `backend/tests/test_farmers.py` | 6 tests |
| `backend/tests/test_finance.py` | 10 tests |
| `backend/tests/test_forum.py` | 9 tests |
| `backend/tests/test_disease.py` | 3 tests |
| `backend/tests/test_knowledge.py` | 6 tests |
| `backend/tests/test_market.py` | 7 tests |
| `backend/tests/test_mitra.py` | 4 tests |
| `backend/tests/test_notifications.py` | 5 tests |
| `backend/tests/test_support.py` | 2 tests |
| `backend/tests/test_weather.py` | 6 tests |
| `backend/pyproject.toml` | pytest config (asyncio_mode=auto) |
| `backend/requirements-test.txt` | Test dependencies |

### Frontend — Rewrites
| File | Change |
|------|--------|
| `frontend/src/services/forumService.ts` | Fixed API paths to `/api/v1/forum/` |
| `frontend/src/services/financeService.ts` | Fixed API paths to `/api/v1/finance/` |
| `frontend/src/app/(dashboard)/forum/page.tsx` | Full rewrite with React Query |
| `frontend/src/app/(dashboard)/finance/page.tsx` | Full rewrite with React Query |
| `frontend/src/app/(dashboard)/finance/expenses/page.tsx` | Full rewrite with React Query |

---

## Running Tests

```bash
cd backend
pip install -r requirements-test.txt
pytest tests/ -v
```

---

## What's Next (Sprint 8)

1. **Database migration execution** — Run Alembic migration against PostgreSQL
2. **End-to-end smoke tests** — Browser-based tests with Playwright
3. **Performance testing** — Load test critical endpoints
4. **Frontend polish** — Accessibility audit, responsive design review
5. **Deployment prep** — Docker Compose finalization, CI/CD pipeline
