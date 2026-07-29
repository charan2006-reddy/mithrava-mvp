"""Voice services — Speech-to-Text and Text-to-Speech via Gemini.

Uses Google Gemini Flash (free tier: 15 RPM, 1M tokens/day).
Supports Indian languages: Hindi, Telugu, Tamil, Kannada, English.
"""

import base64
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger("mithrava.voice")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Language code mapping: app code → Gemini codes
LANGUAGE_MAP = {
    "en": "en",
    "hi": "hi",
    "te": "te",
    "ta": "ta",
    "kn": "kn",
}


def _get_gemini_lang(language: str) -> str:
    """Get Gemini-compatible language code."""
    return LANGUAGE_MAP.get(language, "en")


# ---------------------------------------------------------------------------
# Speech-to-Text (STT)
# ---------------------------------------------------------------------------


async def transcribe_audio(
    audio_bytes: bytes,
    language: str = "en",
    mime_type: str = "audio/webm",
) -> str:
    """Transcribe audio to text using Gemini Flash (free tier).

    Args:
        audio_bytes: Raw audio bytes (any common format).
        language: App language code (en, hi, te, ta, kn).
        mime_type: MIME type of the audio (audio/webm, audio/ogg, audio/wav, etc.).

    Returns:
        Transcribed text string.

    Raises:
        RuntimeError: If Gemini is not configured or fails.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "STT requires GEMINI_API_KEY. "
            "Configure GEMINI_API_KEY in your .env."
        )

    text = await _transcribe_gemini(audio_bytes, language, mime_type)
    if text:
        logger.info("STT: Gemini transcription successful")
        return text

    raise RuntimeError("STT: Gemini returned empty transcription.")


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


# ---------------------------------------------------------------------------
# Text-to-Speech (TTS)
# ---------------------------------------------------------------------------


async def text_to_speech(
    text: str,
    language: str = "en",
) -> tuple[bytes, str]:
    """Convert text to speech audio using Gemini Flash (free tier).

    Args:
        text: The text to speak.
        language: App language code.

    Returns:
        Tuple of (audio_bytes, mime_type).

    Raises:
        RuntimeError: If Gemini is not configured or fails.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "TTS requires GEMINI_API_KEY. "
            "Configure GEMINI_API_KEY in your .env."
        )

    # Truncate very long text for TTS
    tts_text = text[:4000] if len(text) > 4000 else text

    audio, mime = await _tts_gemini(tts_text, language)
    if audio:
        logger.info("TTS: Gemini audio generation successful")
        return audio, mime

    raise RuntimeError("TTS: Gemini returned empty audio.")


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


# ---------------------------------------------------------------------------
# Provider availability check
# ---------------------------------------------------------------------------


def get_available_providers() -> dict[str, list[str]]:
    """Return a dict of available STT and TTS providers based on configured keys.

    Useful for diagnostics and health checks.
    """
    providers: dict[str, list[str]] = {"stt": [], "tts": []}

    if GEMINI_API_KEY:
        providers["stt"].append("gemini")
        providers["tts"].append("gemini")

    # Client-side providers (always available)
    providers["stt"].append("browser-web-speech")
    providers["tts"].append("browser-speech-synthesis")

    return providers
