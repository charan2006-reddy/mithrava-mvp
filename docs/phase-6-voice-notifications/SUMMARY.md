# Phase 6 — Voice I/O & Notification System

**Status**: ✅ COMPLETE  
**Date**: July 2026  
**Scope**: Multi-provider voice pipeline (free-tier first), push notification system

---

## Summary

This phase adds voice-based interaction to Mitra (the AI assistant) and a full notification system. The voice pipeline uses a **provider chain** with automatic fallback — prioritizing free-tier services (Google Gemini Flash) before falling back to paid providers (OpenAI Whisper/TTS). The notification system supports weather alerts, price spike alerts, calendar reminders, and system notifications with Web Push support.

---

## Architecture

### Voice Pipeline — Provider Chain

```
┌─────────────────────────────────────────────────────────────┐
│  SPEECH-TO-TEXT (STT)                                       │
│                                                             │
│  1. Browser Web Speech API (client-side, free, offline)     │
│     ↓ fallback (server-side)                                │
│  2. Google Gemini Flash (free tier: 15 RPM, 1M tokens/day) │
│     ↓ fallback                                              │
│  3. OpenAI Whisper-1 (paid: $0.006/min)                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  TEXT-TO-SPEECH (TTS)                                       │
│                                                             │
│  1. Browser Speech Synthesis API (client-side, free)        │
│     ↓ fallback (server-side)                                │
│  2. Google Gemini Flash (free tier)                         │
│     ↓ fallback                                              │
│  3. OpenAI TTS-1 (paid: $0.015/1K chars)                   │
└─────────────────────────────────────────────────────────────┘
```

**Supported Languages**: English, Hindi, Telugu, Tamil, Kannada

### Notification System

```
┌─────────────────────────────────────────────┐
│  AUTO-GENERATED ALERTS                       │
│                                              │
│  Weather: frost, rain, heat wave, wind,     │
│           humidity (from weather API)        │
│  Price:   >10% price change (from market)   │
│  Calendar: sowing, irrigation, harvest      │
│             (from crop calendar)             │
│  System:  tips, scheme updates              │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│  DELIVERY CHANNELS                           │
│                                              │
│  1. In-app notification center (real-time)  │
│  2. Header bell with live unread count      │
│  3. Web Push (Service Worker — future)      │
│  4. Duplicate suppression (6hr window)      │
└─────────────────────────────────────────────┘
```

---

## Files Created/Modified

### Backend — New Files

| File | Purpose | Lines |
|------|---------|-------|
| `backend/app/core/voice_providers.py` | Multi-provider STT/TTS with Gemini + OpenAI fallback | ~340 |
| `backend/app/services/notification_service.py` | Notification CRUD + auto-trigger helpers | ~250 |
| `backend/app/models/push_subscription.py` | Web Push subscription ORM model | ~35 |

### Backend — Modified Files

| File | Change |
|------|--------|
| `backend/app/models/mitra.py` | Added `metadata` JSONB field to `MitraMessage` (for TTS audio) |
| `backend/app/services/mitra_service.py` | Rewrote `send_voice_message()` to use multi-provider STT + TTS; added `generate_tts()` |
| `backend/app/api/v1/mitra.py` | Added `POST /tts`, `GET /voice/providers`; updated voice endpoint response |
| `backend/app/api/v1/notifications.py` | Added `GET /unread-count`, `POST /subscribe`, `DELETE /subscribe`; enhanced list with type filter |
| `backend/.env` | Added `GEMINI_API_KEY` |
| `backend/.env.example` | Added `GEMINI_API_KEY` with description |

### Frontend — New Files

| File | Purpose |
|------|---------|
| `frontend/src/hooks/useVoiceRecording.ts` | MediaRecorder API hook — recording, duration, audio levels, auto-stop |
| `frontend/src/components/notifications/NotificationBell.tsx` | Header notification bell with live unread count (React Query polling) |
| `frontend/src/components/notifications/NotificationPanel.tsx` | Dropdown notification panel |
| `frontend/src/components/notifications/NotificationItem.tsx` | Single notification item with type-based icons and time-ago formatting |
| `frontend/src/app/(dashboard)/notifications/page.tsx` | Full notification center page with tabs, filters, push permission CTA |

### Frontend — Modified Files

| File | Change |
|------|--------|
| `frontend/src/components/mitra/MitraVoiceButton.tsx` | Rewrote with `useVoiceRecording` — live audio level bars, duration timer, auto MIME detection |
| `frontend/src/components/mitra/MitraMessage.tsx` | Added TTS "Listen" button — fetches audio from `POST /api/v1/mitra/tts`, inline playback |
| `frontend/src/components/mitra/MitraInput.tsx` | Added `onVoiceData` prop to pass audio to backend for server-side STT |
| `frontend/src/components/mitra/MitraWidget.tsx` | Wired `sendVoiceMessage` to pass audio data to backend |
| `frontend/src/hooks/useMitra.ts` | Added `sendVoiceMessage()` method — sends audio to `/api/v1/mitra/voice` |
| `frontend/src/services/mitraService.ts` | Added `getTTS()`, `getVoiceProviders()`; fixed `voice()` endpoint body |
| `frontend/src/services/notificationService.ts` | Fixed all paths to `/api/v1/notifications`; added `subscribePush`, `unsubscribePush`, type filter |
| `frontend/src/components/layout/Header.tsx` | Replaced hardcoded `notificationCount=3` with `<NotificationBell />` component |

---

## API Endpoints Added

### Mitra Voice

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/mitra/tts` | Generate TTS audio for text (returns raw audio bytes) |
| `GET` | `/api/v1/mitra/voice/providers` | List available voice providers based on configured API keys |

### Notifications

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/notifications/unread-count` | Lightweight unread count (for header badge) |
| `POST` | `/api/v1/notifications/subscribe` | Register Web Push subscription |
| `DELETE` | `/api/v1/notifications/subscribe?endpoint=...` | Remove push subscription |

### Enhanced

| Method | Path | Change |
|--------|------|--------|
| `GET` | `/api/v1/notifications/` | Added `?type=` query param filter |

---

## Voice Recording Flow

```
User taps mic button
    ↓
MediaRecorder starts (WebM/Opus)
    ↓
Live audio level visualization (AnalyserNode)
    ↓
Duration timer (max 60s)
    ↓
User taps stop
    ↓
Blob → base64 → POST /api/v1/mitra/voice
    ↓
Server: Gemini Flash STT → transcribed text
    ↓
Server: Mitra processes text → generates response
    ↓
Server: Gemini Flash TTS → audio bytes
    ↓
Response: { text, tts_audio (base64), tts_mime }
    ↓
Client: Renders text bubble + "Listen" button
    ↓
User taps "Listen" → plays TTS audio inline
```

---

## Free Tier Coverage

| Feature | Provider | Free Limit | Notes |
|---------|----------|------------|-------|
| STT (Speech-to-Text) | Gemini Flash | 15 RPM, 1M tokens/day | Covers ~300 voice messages/day |
| TTS (Text-to-Speech) | Gemini Flash | 15 RPM, 1M tokens/day | Covers ~300 TTS responses/day |
| Fallback STT | OpenAI Whisper | None (paid) | $0.006/min |
| Fallback TTS | OpenAI TTS-1 | None (paid) | $0.015/1K chars |
| Client-side STT | Web Speech API | Unlimited | Browser-native, no API key |
| Client-side TTS | Speech Synthesis | Unlimited | Browser-native, no API key |

---

## What's Next (Sprint 7)

1. **Voice fine-tuning** — Fine-tune Whisper on Indian agricultural vocabulary (Telugu, Hindi)
2. **Background sync** — Sync notifications when app reconnects
3. **Notification preferences** — User-configurable alert thresholds
4. **Price monitoring cron** — Background job checking price changes
5. **Voice conversation mode** — Continuous voice chat (no tap-to-speak)
6. **Service Worker** — Full Web Push implementation with offline support
