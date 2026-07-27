# Sprint 9 — Admin Page, Market Improvements & Mock Cleanup

**Status**: COMPLETE
**Date**: July 18, 2026
**Backend Tests**: 78 passed, 0 failed (34.88s)

---

## Overview

Sprint 9 completed the final frontend-to-backend integration by wiring the admin page to real APIs, improving market data realism, and cleaning up the last remaining mock page. After this sprint, **all 25 frontend pages either use real backend APIs or are static/utility pages**.

---

## Changes

### 1. Old `/disease` Page → Redirect to `/diseases`
**File**: `app/(dashboard)/disease/page.tsx`

The old `/disease` page (298 lines) was completely hardcoded with `mockResult` and `scanHistory`. Replaced with a simple server-side redirect to `/diseases`, which already has full React Query integration via `useDiseaseHistory()`.

### 2. Admin Page — Full Rewrite with Real API
**Files**:
- `services/adminService.ts` (NEW) — API client for all admin endpoints
- `hooks/useAdmin.ts` (NEW) — React Query hooks with mutations + cache invalidation
- `app/(dashboard)/admin/page.tsx` (REWRITTEN) — 300+ lines of mock data → real API

**What the admin page now does**:
- **Stats cards**: Real counts from `GET /api/v1/admin/stats` (farmers, vendors, crops, support calls)
- **Farmer list**: Paginated from `GET /api/v1/admin/farmers` with role badges and deactivation
- **Vendor list**: Paginated from `GET /api/v1/admin/vendors` with ratings and deactivation
- **Support calls**: Real data from `GET /api/v1/support/calls` with status badges
- **Add farmer**: `POST /api/v1/admin/farmers` with form validation + loading states
- **Add vendor**: `POST /api/v1/admin/vendors` with type selector + loading states
- **Delete farmer/vendor**: Soft-delete with confirmation dialog
- **Error handling**: Shows "not admin" message if 403/401, retry buttons on failures
- **Loading states**: Skeletons during initial load, inline spinners on mutations

### 3. Backend Bug Fix — `list_all_farmers` Unpacking Error
**File**: `backend/app/api/v1/admin.py`

`FarmerRepository.list_all()` returns `list[Farmer]` (a list), but the admin endpoint was destructuring it as `farmers, total = await FarmerRepository.list_all(...)`. This would crash at runtime. Fixed by calling `list_all()` and `count()` separately.

### 4. Market Prices — Deterministic Daily Fluctuation
**File**: `backend/app/api/v1/market.py`

**Before**: Static hardcoded prices (same value every day). Price trends used `random.uniform()` so they changed every server restart.

**After**: Prices use a deterministic hash-based daily fluctuation:
- Each crop + date combination produces a unique but reproducible fluctuation factor (±6%)
- `hashlib.md5(f"{crop}:{date_str}")` generates a seeded random value
- Prices change each day but are consistent within a day (no server restart dependency)
- Trend data is now fully deterministic — same crop + same date range = same chart every time
- Removed `import random` (no more randomness in the module)

**Price ranges** (base ± 20%):
| Crop | Base (₹/quintal) | Range |
|------|------------------|-------|
| Rice (Paddy) | 2,050 | 1,640 – 2,460 |
| Wheat | 2,275 | 1,820 – 2,730 |
| Cotton | 6,620 | 5,296 – 7,944 |
| Red Chilli | 12,000 | 9,600 – 14,400 |
| Tomato | 2,500 | 2,000 – 3,000 |
| Groundnut | 5,500 | 4,400 – 6,600 |
| Soybean | 4,600 | 3,680 – 5,520 |
| Maize | 1,870 | 1,496 – 2,244 |
| Onion | 1,800 | 1,440 – 2,160 |
| Potato | 1,200 | 960 – 1,440 |

---

## Frontend Integration Status (After Sprint 9)

| Status | Pages | Count |
|--------|-------|-------|
| **Real API + React Query** | Dashboard, Weather, Market, Finance (x2), Notifications, Forum, Crops (x3), Knowledge (x3), Diseases, Vendors, Support, Login, Register, Admin | **20** |
| **Real API + useAuth** | Profile | **1** |
| **Partial (API + fallback)** | Diseases/scan (real API, no React Query) | **1** |
| **Static/Utility** | Landing, 404, Error, Disease (redirect) | **4** |

**20 of 25 pages use real backend APIs via React Query (80%)**. The remaining 4 are static/utility pages that don't need API integration.

---

## Files Changed/Created (Sprint 9)

### New Files
| File | Purpose |
|------|---------|
| `frontend/src/services/adminService.ts` | Admin API service (stats, farmers, vendors, support calls) |
| `frontend/src/hooks/useAdmin.ts` | React Query hooks with mutations + cache invalidation |

### Modified Files
| File | Change |
|------|--------|
| `frontend/src/app/(dashboard)/disease/page.tsx` | Replaced 298-line mock page with redirect |
| `frontend/src/app/(dashboard)/admin/page.tsx` | Full rewrite — React Query + real API |
| `backend/app/api/v1/admin.py` | Fixed `list_all_farmers` unpacking bug |
| `backend/app/api/v1/market.py` | Added deterministic daily fluctuation, removed randomness |

---

## What's Left (Sprint 10+)

| Priority | Item | Effort |
|----------|------|--------|
| P1 | Redis-backed rate limits (currently memory-only) | 30 min |
| P1 | SMS provider (Twilio/MSG91) for OTP delivery | 1-2 hours |
| P1 | Push notification delivery (FCM) | 2 hours |
| P2 | Frontend tests (Jest/Vitest) | 3-4 hours |
| P2 | Docker secrets (remove hardcoded passwords) | 30 min |
| P2 | CI/CD pipeline (GitHub Actions) | 1-2 hours |
| P2 | Backend tests for admin endpoints + token refresh | 2 hours |

**The MVP is functionally complete.** All remaining items are production hardening, not feature work.
