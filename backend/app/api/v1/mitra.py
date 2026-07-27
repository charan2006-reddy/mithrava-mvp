"""Mitra AI assistant API endpoints."""

import base64
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.farmer import Farmer
from app.schemas.mitra import MitraMessageCreate
from app.services.mitra_service import MitraService

router = APIRouter(prefix="/mitra", tags=["Mitra AI"])


# ---------------------------------------------------------------------------
# Request/response schemas for new endpoints
# ---------------------------------------------------------------------------


class TTSRequest(BaseModel):
    """Request body for text-to-speech generation."""

    text: str = Field(..., min_length=1, max_length=4000, description="Text to convert to speech")
    language: str = Field(default="en", description="Language code (en, hi, te, ta, kn)")


class VoiceProvidersResponse(BaseModel):
    """Response showing available voice providers."""

    stt: list[str]
    tts: list[str]


# ---------------------------------------------------------------------------
# Text chat
# ---------------------------------------------------------------------------


@router.post("/chat")
async def chat_with_mitra(
    body: MitraMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Send a message to Mitra AI and get a response.

    Creates a new conversation if conversation_id is not provided.
    """
    conversation_id = body.conversation_id
    if not conversation_id:
        conversation = await MitraService.create_conversation(
            db, str(current_user.id), body.language
        )
        conversation_id = str(conversation.id)

    try:
        response = await MitraService.send_message(
            db=db,
            conversation_id=conversation_id,
            message=body.content,
            farmer_id=str(current_user.id),
            language=body.language,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mitra encountered an error: {exc}",
        )

    return {
        "success": True,
        "message": "OK",
        "data": {
            "conversation_id": conversation_id,
            "message": {
                "id": str(response.id),
                "role": response.role,
                "content": response.content,
                "intent": response.intent,
                "actions_taken": response.actions_taken,
                "created_at": response.created_at.isoformat() if response.created_at else None,
            },
        },
    }


# ---------------------------------------------------------------------------
# Voice message (multi-provider STT + TTS)
# ---------------------------------------------------------------------------


@router.post("/voice")
async def voice_message(
    body: MitraMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Send a voice message to Mitra AI.

    Transcribes the voice using the best available STT provider
    (Gemini free tier → OpenAI Whisper), processes the text, and
    returns a text response with optional TTS audio.
    """
    if not body.voice_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voice data is required.",
        )

    conversation_id = body.conversation_id
    if not conversation_id:
        conversation = await MitraService.create_conversation(
            db, str(current_user.id), body.language
        )
        conversation_id = str(conversation.id)

    try:
        response = await MitraService.send_voice_message(
            db=db,
            conversation_id=conversation_id,
            voice_data=body.voice_data,
            farmer_id=str(current_user.id),
            language=body.language,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice processing failed: {exc}",
        )

    result: dict = {
        "id": str(response.id),
        "role": response.role,
        "content": response.content,
        "intent": response.intent,
        "created_at": response.created_at.isoformat() if response.created_at else None,
    }

    # Include TTS audio if available
    if response.message_metadata and response.message_metadata.get("tts_audio"):
        result["tts_audio"] = response.message_metadata["tts_audio"]
        result["tts_mime"] = response.message_metadata.get("tts_mime", "audio/mp3")

    return {
        "success": True,
        "message": "OK",
        "data": {
            "conversation_id": conversation_id,
            "message": result,
        },
    }


# ---------------------------------------------------------------------------
# Text-to-Speech (standalone endpoint)
# ---------------------------------------------------------------------------


@router.post("/tts")
async def generate_tts(
    body: TTSRequest,
    current_user: Farmer = Depends(get_current_user),
):
    """Generate text-to-speech audio for any text.

    Returns raw audio bytes with the appropriate Content-Type header.
    Uses the best available TTS provider (Gemini free → OpenAI TTS).
    """
    try:
        audio_bytes, mime_type = await MitraService.generate_tts(
            text=body.text,
            language=body.language,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    return Response(
        content=audio_bytes,
        media_type=mime_type,
        headers={
            "Content-Disposition": "inline; filename=mithrava_tts.mp3",
            "Cache-Control": "public, max-age=3600",
        },
    )


# ---------------------------------------------------------------------------
# Voice providers status
# ---------------------------------------------------------------------------


@router.get("/voice/providers", response_model=VoiceProvidersResponse)
async def get_voice_providers(
    current_user: Farmer = Depends(get_current_user),
):
    """Get available voice providers based on configured API keys.

    Shows which STT and TTS providers are available for voice features.
    """
    from app.core.voice_providers import get_available_providers
    return get_available_providers()


# ---------------------------------------------------------------------------
# Conversations CRUD
# ---------------------------------------------------------------------------


@router.get("/conversations")
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """List all Mitra conversations for the current farmer."""
    conversations = await MitraService.get_conversations(
        db, str(current_user.id)
    )

    return {
        "success": True,
        "message": "OK",
        "data": {
            "conversations": [
                {
                    "id": str(c.id),
                    "title": c.title,
                    "language": c.language,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
                for c in conversations
            ],
            "total": len(conversations),
        },
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Get all messages in a Mitra conversation."""
    messages = await MitraService.get_conversation_messages(
        db, conversation_id, str(current_user.id)
    )

    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or empty.",
        )

    return {
        "success": True,
        "message": "OK",
        "data": {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "id": str(m.id),
                    "role": m.role,
                    "content": m.content,
                    "intent": m.intent,
                    "actions_taken": m.actions_taken,
                    "has_tts": bool(m.message_metadata and m.message_metadata.get("tts_audio")),
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in messages
            ],
            "total": len(messages),
        },
    }


@router.post("/conversations", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    language: str = "en",
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Create a new Mitra conversation."""
    conversation = await MitraService.create_conversation(
        db, str(current_user.id), language
    )

    return {
        "success": True,
        "message": "Conversation created",
        "data": {
            "id": str(conversation.id),
            "language": conversation.language,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
        },
    }
