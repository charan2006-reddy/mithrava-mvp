"""Multi-provider voice services — Speech-to-Text and Text-to-Speech.

Implements a provider chain with automatic fallback:
  1. Google Gemini Flash (free tier: 15 RPM, 1M tokens/day)
  2. OpenAI Whisper (paid, best quality for STT)
  3. OpenAI TTS (paid, best quality for TTS)

Supports Indian languages: Hindi, Telugu, Tamil, Kannada, English.
"""

import base64
import io
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger("mithrava.voice")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Language code mapping: app code → provider codes
LANGUAGE_MAP = {
    "en": {"gemini": "en", "openai": "en", "iso": "en-US"},
    "hi": {"gemini": "hi", "openai": "hi", "iso": "hi-IN"},
    "te": {"gemini": "te", "openai": None, "iso": "te-IN"},
    "ta": {"gemini": "ta", "openai": None, "iso": "ta-IN"},
    "kn": {"gemini": "kn", "openai": None, "iso": "kn-IN"},
}


def _get_gemini_lang(language: str) -> str:
    """Get Gemini-compatible language code."""
    return LANGUAGE_MAP.get(language, {}).get("gemini", "en")


def _get_openai_lang(language: str) -> Optional[str]:
    """Get OpenAI-compatible language code, or None if unsupported."""
    return LANGUAGE_MAP.get(language, {}).get("openai")


# ---------------------------------------------------------------------------
# Speech-to-Text (STT)
# ---------------------------------------------------------------------------


async def transcribe_audio(
    audio_bytes: bytes,
    language: str = "en",
    mime_type: str = "audio/webm",
) -> str:
    """Transcribe audio to text using the best available provider.

    Tries providers in order:
      1. Gemini Flash (free) — supports Hindi, Telugu, Tamil, Kannada, English
      2. OpenAI Whisper (paid) — supports Hindi, English; fallback for others

    Args:
        audio_bytes: Raw audio bytes (any common format).
        language: App language code (en, hi, te, ta, kn).
        mime_type: MIME type of the audio (audio/webm, audio/ogg, audio/wav, etc.).

    Returns:
        Transcribed text string.

    Raises:
        RuntimeError: If all providers fail.
    """
    errors: list[str] = []

    # --- Provider 1: Gemini Flash (free tier) ---
    if GEMINI_API_KEY:
        try:
            text = await _transcribe_gemini(audio_bytes, language, mime_type)
            if text:
                logger.info("STT: Gemini transcription successful")
                return text
        except Exception as exc:
            errors.append(f"Gemini: {exc}")
            logger.warning("STT: Gemini failed — %s", exc)

    # --- Provider 2: OpenAI Whisper (paid) ---
    if OPENAI_API_KEY:
        try:
            text = await _transcribe_openai(audio_bytes, language)
            if text:
                logger.info("STT: OpenAI Whisper transcription successful")
                return text
        except Exception as exc:
            errors.append(f"OpenAI: {exc}")
            logger.warning("STT: OpenAI failed — %s", exc)

    # All providers failed
    error_detail = "; ".join(errors) if errors else "No API keys configured"
    raise RuntimeError(
        f"All STT providers failed. {error_detail}. "
        "Configure GEMINI_API_KEY or OPENAI_API_KEY in your .env."
    )


async def _transcribe_gemini(
    audio_bytes: bytes, language: str, mime_type: str
) -> Optional[str]:
    """Transcribe using Google Gemini Flash (free tier).

    Uses the Gemini API's inline audio support via the generateContent
    endpoint with audio input.
    """
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    lang_code = _get_gemini_lang(language)

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": audio_b64,
                        }
                    },
                    {
                        "text": (
                            f"Transcribe this audio exactly as spoken. "
                            f"The language is {lang_code}. "
                            f"Return ONLY the transcribed text, nothing else. "
                            f"If the audio is unclear or empty, return: [unclear audio]"
                        )
                    },
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    # Extract text from Gemini response
    candidates = data.get("candidates", [])
    if not candidates:
        return None

    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")

    # Clean up — remove markdown formatting if any
    text = text.strip().strip('"').strip("'")
    if text.lower() in ("[unclear audio]", "[unintelligible]", ""):
        return None

    return text


async def _transcribe_openai(
    audio_bytes: bytes, language: str
) -> Optional[str]:
    """Transcribe using OpenAI Whisper API (paid).

    Falls back to English for languages not supported by Whisper.
    """
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "voice_message.webm"

    lang = _get_openai_lang(language) or "en"

    try:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=lang,
        )
        text = transcript.text.strip()
        return text if text else None
    except Exception as exc:
        raise RuntimeError(f"OpenAI Whisper failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Text-to-Speech (TTS)
# ---------------------------------------------------------------------------


async def text_to_speech(
    text: str,
    language: str = "en",
) -> tuple[bytes, str]:
    """Convert text to speech audio using the best available provider.

    Tries providers in order:
      1. Gemini Flash (free) — generate audio via Gemini
      2. OpenAI TTS (paid) — high-quality voices

    Args:
        text: The text to speak.
        language: App language code.

    Returns:
        Tuple of (audio_bytes, mime_type).

    Raises:
        RuntimeError: If all providers fail.
    """
    errors: list[str] = []

    # Truncate very long text for TTS (most providers have limits)
    tts_text = text[:4000] if len(text) > 4000 else text

    # --- Provider 1: Gemini Flash (free tier) ---
    if GEMINI_API_KEY:
        try:
            audio, mime = await _tts_gemini(tts_text, language)
            if audio:
                logger.info("TTS: Gemini audio generation successful")
                return audio, mime
        except Exception as exc:
            errors.append(f"Gemini: {exc}")
            logger.warning("TTS: Gemini failed — %s", exc)

    # --- Provider 2: OpenAI TTS (paid) ---
    if OPENAI_API_KEY:
        try:
            audio, mime = await _tts_openai(tts_text, language)
            if audio:
                logger.info("TTS: OpenAI audio generation successful")
                return audio, mime
        except Exception as exc:
            errors.append(f"OpenAI: {exc}")
            logger.warning("TTS: OpenAI failed — %s", exc)

    # All providers failed
    error_detail = "; ".join(errors) if errors else "No API keys configured"
    raise RuntimeError(
        f"All TTS providers failed. {error_detail}. "
        "Configure GEMINI_API_KEY or OPENAI_API_KEY in your .env."
    )


async def _tts_gemini(
    text: str, language: str
) -> tuple[Optional[bytes], str]:
    """Generate speech using Gemini Flash (free tier).

    Uses Gemini's text-to-audio capability.
    """
    lang_code = _get_gemini_lang(language)

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
    )

    voice_names = {
        "en": "en-US-Neural2-F",
        "hi": "hi-IN-Neural2-A",
        "te": "te-IN-Standard-A",
        "ta": "ta-IN-Standard-A",
        "kn": "kn-IN-Standard-A",
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Speak the following text in {lang_code} language. "
                            f"Use a warm, helpful voice suitable for an agricultural assistant. "
                            f"Keep the tone natural and conversational.\n\n"
                            f"{text}"
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "audioConfig": {
                "audioMimeType": "audio/mp3",
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_names.get(lang_code, "en-US-Neural2-F")
                    }
                },
            },
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        return None, "audio/mp3"

    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        audio_data = part.get("inlineData", {})
        if audio_data.get("data"):
            audio_bytes = base64.b64decode(audio_data["data"])
            mime = audio_data.get("mimeType", "audio/mp3")
            return audio_bytes, mime

    return None, "audio/mp3"


async def _tts_openai(
    text: str, language: str
) -> tuple[Optional[bytes], str]:
    """Generate speech using OpenAI TTS (paid)."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    # Voice selection based on language
    voice_map = {
        "en": "nova",
        "hi": "alloy",
        "te": "alloy",
        "ta": "alloy",
        "kn": "alloy",
    }
    voice = voice_map.get(language, "nova")

    try:
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice,  # type: ignore
            input=text,
            response_format="mp3",
        )

        audio_bytes = await response.read()
        return audio_bytes, "audio/mp3"

    except Exception as exc:
        raise RuntimeError(f"OpenAI TTS failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Provider availability check
# ---------------------------------------------------------------------------


def get_available_providers() -> dict[str, list[str]]:
    """Return a dict of available STT and TTS providers based on configured keys.

    Useful for diagnostics and health checks.
    """
    providers = {"stt": [], "tts": []}

    if GEMINI_API_KEY:
        providers["stt"].append("gemini")
        providers["tts"].append("gemini")
    if OPENAI_API_KEY:
        providers["stt"].append("openai-whisper")
        providers["tts"].append("openai-tts")

    # Client-side providers (always available)
    providers["stt"].append("browser-web-speech")
    providers["tts"].append("browser-speech-synthesis")

    return providers
