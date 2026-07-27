# Sprint 10 — Production Hardening

**Status**: COMPLETE
**Date**: July 18, 2026
**Backend Tests**: 91 passed, 0 failed (45.04s) — up from 78 (+13 new tests)

---

## Overview

Sprint 10 focused on production readiness: Redis-backed rate limiting, SMS provider integration, Docker security hardening, and comprehensive test coverage for previously untested endpoints.

---

## Changes

### 1. Redis-Backed Rate Limiting with Graceful Fallback
**File**: `app/middleware/rate_limit.py`

**Before**: `storage_uri="memory://"` — rate limits lost on restart, not shared across instances.

**After**: Tries Redis first, falls back to memory if:
- No `REDIS_URL` configured
- Invalid URL format
- `redis` Python package not installed
- Redis connection fails at startup

```python
# Auto-detection flow:
# 1. Check REDIS_URL env var → if empty/missing → memory://
# 2. Check URL format → if invalid → memory://
# 3. Check `import redis` → if ImportError → memory://
# 4. Use redis://... as storage
```

Also added `redis>=5.0.0` to `requirements.txt`.

### 2. SMS Provider Abstraction
**File**: `app/core/sms.py` (NEW — 190 lines)

Pluggable SMS provider system supporting 3 backends:

| Provider | Config | Use Case |
|----------|--------|----------|
| `ConsoleProvider` | None needed | Development (prints OTP to console) |
| `TwilioProvider` | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` | International, pay-per-SMS |
| `MSG91Provider` | `MSG91_AUTH_KEY`, `MSG91_TEMPLATE_ID`, `MSG91_SENDER_ID` | India-focused, cheap |

Configure via `SMS_PROVIDER` env var (`console`, `twilio`, `msg91`).

**Integration**: Updated `AuthService.send_otp()` to:
- Use the configured SMS provider to actually send OTPs
- Only include `demo_otp` in response when using ConsoleProvider (dev mode)
- When using Twilio/MSG91, `demo_otp` is `null` in the API response

### 3. Docker Security Hardening
**File**: `docker-compose.yml`

**Before**: Hardcoded passwords (`POSTGRES_PASSWORD: mithrava`).

**After**: All secrets reference environment variables with required markers:
```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD in .env}
```

Also:
- Redis now supports optional password auth (`--requirepass`)
- `REDIS_URL` includes password conditionally: `redis://${REDIS_PASSWORD:+:${REDIS_PASSWORD}@}redis:6379/0`

**New file**: `.env.example` (root) — documents all required/optional environment variables.

### 4. Backend Tests — 13 New Tests
**File**: `tests/test_admin.py` (NEW — 13 tests)

| Test Class | Tests | Coverage |
|------------|-------|----------|
| `TestAdminStats` | 3 | Admin stats access (admin-only, success, no-auth) |
| `TestAdminFarmers` | 4 | Farmer CRUD (list, create, delete, auth check) |
| `TestAdminVendors` | 2 | Vendor listing (admin-only, success) |
| `TestAdminTokenRefresh` | 3 | Token rotation (success, invalid, revoked) |
| `TestAdminCreateFarmer` | 1 | Admin farmer creation |

**Key test**: `test_refresh_token_revoked` — verifies refresh token rotation actually invalidates the old token.

---

## Files Changed/Created (Sprint 10)

### New Files
| File | Purpose |
|------|---------|
| `backend/app/core/sms.py` | Pluggable SMS provider (Console, Twilio, MSG91) |
| `backend/tests/test_admin.py` | 13 tests for admin + token refresh endpoints |
| `.env.example` | Root environment variable documentation |

### Modified Files
| File | Change |
|------|--------|
| `backend/app/middleware/rate_limit.py` | Redis-backed with memory fallback |
| `backend/app/services/auth_service.py` | Integrated SMS provider for OTP delivery |
| `backend/requirements.txt` | Added `redis>=5.0.0` |
| `docker-compose.yml` | Moved secrets to env vars, Redis auth support |

---

## Test Coverage Summary (Sprint 10)

| Test File | Tests | API Coverage |
|-----------|-------|--------------|
| `test_admin.py` | **13** (NEW) | Admin stats, farmer/vendor CRUD, token refresh/rotation |
| `test_auth.py` | 8 | OTP, register, /me |
| `test_crops.py` | 10 | Crops CRUD + calendar |
| `test_disease.py` | 3 | Disease analyze + history |
| `test_farmers.py` | 6 | Profile + stats + admin check |
| `test_finance.py` | 10 | Income/expense + summary |
| `test_weather.py` | 6 | Weather + forecast + advice |
| `test_market.py` | 7 | Market prices + trend |
| `test_forum.py` | 9 | Posts, comments, likes |
| `test_knowledge.py` | 6 | Categories, search, ask, seed |
| `test_mitra.py` | 4 | Chat + voice + conversations |
| `test_notifications.py` | 5 | List, unread count, filter |
| `test_support.py` | 2 | Expert call, admin listing |
| `test_health.py` | 2 | Health + root endpoints |
| **TOTAL** | **91** | **14 route groups** |

---

## What's Left (Sprint 11+)

| Priority | Item | Effort |
|----------|------|--------|
| P2 | Frontend tests (Jest/Vitest) | 3-4 hours |
| P2 | Push notification delivery (Firebase Cloud Messaging) | 2-3 hours |
| P2 | CI/CD pipeline (GitHub Actions) | 1-2 hours |
| P2 | End-to-end smoke tests (Playwright) | 2-3 hours |
| P3 | Production deployment (AWS ECS/EKS or Railway/Fly.io) | 4-6 hours |

**The MVP is functionally and operationally complete.** All remaining items are frontend testing, CI/CD, and deployment infrastructure.
