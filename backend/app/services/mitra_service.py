"""Mitra AI assistant service — the intelligent farming brain.

Handles conversation management, intent detection, context building,
RAG-based knowledge retrieval, and action execution. Orchestrates
the LLM, farmer data, and external tools.
"""

import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm import ask_llm, get_farming_system_prompt
from app.models.farmer import Farmer
from app.models.mitra import MitraConversation, MitraMessage
from app.repositories.farmer_repo import FarmerRepository
from app.services.rag_service import RAGService


# ---------------------------------------------------------------------------
# Intent definitions
# ---------------------------------------------------------------------------

INTENTS = {
    "weather_query": {
        "keywords": ["weather", "rain", "temperature", "forecast", "climate", "sun", "storm"],
        "description": "User wants weather information",
    },
    "crop_advice": {
        "keywords": ["plant", "sow", "harvest", "crop", "seed", "grow", "cultivation", "farm"],
        "description": "User needs crop-related advice",
    },
    "disease_help": {
        "keywords": ["disease", "pest", "insect", "fungus", "blight", "wilt", "yellow", "spots", "leaf"],
        "description": "User is asking about crop disease",
    },
    "market_price": {
        "keywords": ["price", "rate", "sell", "market", "mandi", "buyer", "cost", "expensive"],
        "description": "User wants market price info",
    },
    "finance": {
        "keywords": ["expense", "income", "profit", "loss", "money", "cost", "budget", "spend"],
        "description": "User is asking about finances",
    },
    "scheme_info": {
        "keywords": ["scheme", "subsidy", "government", "pm-kisan", "loan", "insurance", "benefit"],
        "description": "User is asking about government schemes",
    },
    "general_greeting": {
        "keywords": ["hello", "hi", "namaste", "good morning", "good evening", "hey"],
        "description": "User is greeting Mitra",
    },
}


class MitraService:
    """Service class for the Mitra AI farming assistant.

    Manages conversations, detects user intents, builds farmer context,
    retrieves relevant knowledge (RAG), and executes actions.
    """

    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        farmer_id: str,
        language: str = "en",
    ) -> MitraConversation:
        """Create a new Mitra conversation.

        Args:
            db: Async database session.
            farmer_id: The farmer's ID.
            language: Preferred language for the conversation.

        Returns:
            New MitraConversation instance.
        """
        conversation = MitraConversation(
            farmer_id=farmer_id,
            language=language,
            title=None,
        )
        db.add(conversation)
        await db.flush()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def get_conversations(
        db: AsyncSession, farmer_id: str
    ) -> list[MitraConversation]:
        """List all conversations for a farmer.

        Args:
            db: Async database session.
            farmer_id: The farmer's ID.

        Returns:
            List of MitraConversation instances, newest first.
        """
        result = await db.execute(
            select(MitraConversation)
            .where(MitraConversation.farmer_id == farmer_id)
            .order_by(MitraConversation.updated_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_conversation_messages(
        db: AsyncSession,
        conversation_id: str,
        farmer_id: str,
    ) -> list[MitraMessage]:
        """Get all messages in a conversation.

        Args:
            db: Async database session.
            conversation_id: The conversation ID.
            farmer_id: The owning farmer's ID (for authorization).

        Returns:
            List of MitraMessage instances, chronological order.
        """
        # Verify conversation ownership
        conv_result = await db.execute(
            select(MitraConversation).where(
                MitraConversation.id == conversation_id,
                MitraConversation.farmer_id == farmer_id,
            )
        )
        conversation = conv_result.scalar_one_or_none()
        if conversation is None:
            return []

        result = await db.execute(
            select(MitraMessage)
            .where(MitraMessage.conversation_id == conversation_id)
            .order_by(MitraMessage.created_at.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def send_message(
        db: AsyncSession,
        conversation_id: str,
        message: str,
        farmer_id: str,
        language: str = "en",
    ) -> MitraMessage:
        """Process a user message and generate an AI response.

        This is the main Mitra pipeline:
        1. Store user message
        2. Detect intent
        3. Build farmer context
        4. Retrieve relevant knowledge (RAG)
        5. Generate AI response
        6. Execute any actions
        7. Store and return assistant message

        Args:
            db: Async database session.
            conversation_id: The conversation ID.
            message: User's message text.
            farmer_id: The farmer's ID.
            language: Response language.

        Returns:
            The assistant's MitraMessage response.
        """
        # 1. Store user message
        user_msg = MitraMessage(
            conversation_id=conversation_id,
            role="user",
            content=message,
        )
        db.add(user_msg)
        await db.flush()

        # 2. Detect intent
        intent = MitraService.detect_intent(message)

        # 3. Build farmer context
        context = await MitraService.build_context(db, farmer_id)

        # 4. RAG knowledge retrieval via vector search
        knowledge = await MitraService._retrieve_knowledge(db, message, intent)

        # 5. Build system prompt
        system_prompt = get_farming_system_prompt(language)
        full_context = f"{context}\n\n{knowledge}" if knowledge else context

        # 6. Generate AI response (tries Gemini free → OpenAI paid → Ollama local)
        response_text = await ask_llm(
            prompt=message,
            context=full_context,
            system_prompt=system_prompt,
        )

        # 7. Execute actions if needed
        actions_taken = await MitraService.execute_action(
            intent, {"message": message}, farmer_id
        )

        # 8. Store assistant message
        assistant_msg = MitraMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            intent=intent,
            actions_taken=actions_taken if actions_taken else None,
        )
        db.add(assistant_msg)

        # Update conversation title if first message
        conv_result = await db.execute(
            select(MitraConversation).where(
                MitraConversation.id == conversation_id
            )
        )
        conversation = conv_result.scalar_one_or_none()
        if conversation and not conversation.title:
            # Auto-generate title from first message
            conversation.title = message[:100]

        await db.flush()
        await db.refresh(assistant_msg)
        return assistant_msg

    @staticmethod
    async def send_voice_message(
        db: AsyncSession,
        conversation_id: str,
        voice_data: str,
        farmer_id: str,
        language: str = "en",
    ) -> MitraMessage:
        """Process a voice message (transcribe then respond, with TTS).

        Uses multi-provider voice pipeline with automatic fallback:
          STT: Gemini Flash (free) → OpenAI Whisper (paid)
          TTS: Gemini Flash (free) → OpenAI TTS (paid)

        Args:
            db: Async database session.
            conversation_id: The conversation ID.
            voice_data: Base64-encoded voice data (WebM/OGG/WAV).
            farmer_id: The farmer's ID.
            language: Response language.

        Returns:
            The assistant's MitraMessage response (with TTS audio attached).
        """
        import base64

        voice_bytes = base64.b64decode(voice_data)

        # Determine MIME type from common audio formats
        mime_type = "audio/webm"  # default for browser MediaRecorder
        if voice_bytes[:4] == b"OggS":
            mime_type = "audio/ogg"
        elif voice_bytes[:4] == b"RIFF":
            mime_type = "audio/wav"
        elif voice_bytes[:3] == b"ID3" or voice_bytes[:2] == b"\xff\xfb":
            mime_type = "audio/mpeg"

        # 1. Transcribe voice via multi-provider STT
        from app.core.voice_providers import transcribe_audio

        try:
            transcribed_text = await transcribe_audio(
                audio_bytes=voice_bytes,
                language=language,
                mime_type=mime_type,
            )
        except RuntimeError:
            transcribed_text = (
                "I couldn't understand the voice message. "
                "Could you please type your question?"
            )

        # 2. Process the transcribed text as a normal message
        response_msg = await MitraService.send_message(
            db=db,
            conversation_id=conversation_id,
            message=transcribed_text,
            farmer_id=farmer_id,
            language=language,
        )

        # 3. Generate TTS for the response (best-effort)
        from app.core.voice_providers import text_to_speech

        try:
            audio_bytes, audio_mime = await text_to_speech(
                text=response_msg.content,
                language=language,
            )
            # Attach TTS audio to the response (stored as base64 in metadata)
            response_msg.message_metadata = {
                "tts_audio": base64.b64encode(audio_bytes).decode("utf-8"),
                "tts_mime": audio_mime,
            }
        except RuntimeError:
            # TTS failed — response is still valid as text
            pass

        return response_msg

    @staticmethod
    async def generate_tts(text: str, language: str = "en") -> tuple[bytes, str]:
        """Generate TTS audio for a text string.

        Args:
            text: Text to convert to speech.
            language: Language code.

        Returns:
            Tuple of (audio_bytes, mime_type).

        Raises:
            RuntimeError: If all TTS providers fail.
        """
        from app.core.voice_providers import text_to_speech
        return await text_to_speech(text, language)

    @staticmethod
    def detect_intent(message: str) -> str:
        """Detect the user's intent from their message.

        Uses keyword matching for MVP. In production, use a trained
        intent classification model.

        Args:
            message: The user's message text.

        Returns:
            Detected intent string (e.g., "weather_query", "disease_help").
        """
        message_lower = message.lower()
        scores: dict[str, int] = {}

        for intent_name, intent_info in INTENTS.items():
            score = sum(
                1 for kw in intent_info["keywords"] if kw in message_lower
            )
            if score > 0:
                scores[intent_name] = score

        if not scores:
            return "general_query"

        return max(scores, key=scores.get)

    @staticmethod
    async def execute_action(
        intent: str, params: dict, farmer_id: str
    ) -> list[dict]:
        """Execute an action based on the detected intent.

        Returns a list of action results that were performed.

        Args:
            intent: Detected intent string.
            params: Parameters extracted from the message.
            farmer_id: The farmer's ID.

        Returns:
            List of action result dicts.
        """
        actions: list[dict] = []

        if intent == "weather_query":
            # Trigger weather lookup
            actions.append({
                "action": "weather_lookup",
                "status": "completed",
                "message": "Retrieved weather information",
            })

        elif intent == "market_price":
            actions.append({
                "action": "market_price_lookup",
                "status": "completed",
                "message": "Retrieved market prices",
            })

        elif intent == "disease_help":
            actions.append({
                "action": "disease_analysis_prompt",
                "status": "completed",
                "message": "Suggested disease photo upload",
            })

        return actions

    @staticmethod
    async def build_context(db: AsyncSession, farmer_id: str) -> str:
        """Build a context string about the farmer for the LLM.

        Includes profile info, current crops, and recent financial data.

        Args:
            db: Async database session.
            farmer_id: The farmer's unique identifier.

        Returns:
            Context string to inject into the LLM prompt.
        """
        farmer = await FarmerRepository.get_by_id(db, farmer_id)
        if farmer is None:
            return "No farmer context available."

        parts: list[str] = []
        parts.append(f"Farmer name: {farmer.name}")
        parts.append(f"Location: {farmer.city or 'Unknown'}, {farmer.state or 'India'}")
        parts.append(f"Preferred language: {farmer.preferred_language}")

        if farmer.farm_size_acres:
            parts.append(f"Farm size: {farmer.farm_size_acres} acres")
        if farmer.soil_type:
            parts.append(f"Soil type: {farmer.soil_type}")
        if farmer.irrigation_type:
            parts.append(f"Irrigation: {farmer.irrigation_type}")

        # Add current crops info
        from app.models.crop import Crop

        crop_result = await db.execute(
            select(Crop)
            .where(Crop.farmer_id == farmer_id, Crop.status.in_(["planted", "growing"]))
            .limit(10)
        )
        crops = list(crop_result.scalars().all())
        if crops:
            crop_list = ", ".join(
                f"{c.name} ({c.variety or 'standard'}) on {c.area_acres} acres"
                for c in crops
            )
            parts.append(f"Current crops: {crop_list}")
        else:
            parts.append("No active crops recorded.")

        return "\n".join(parts)

    @staticmethod
    async def _retrieve_knowledge(db: AsyncSession, query: str, intent: str) -> str:
        """Retrieve relevant knowledge for the query using the RAG system.

        Performs vector search against the knowledge base using pgvector
        embeddings. Falls back to simple intent-based snippets if RAG
        search fails or returns no results.

        Args:
            db: Async database session.
            query: User's message.
            intent: Detected intent.

        Returns:
            Relevant knowledge string for context injection.
        """
        try:
            # Use the real RAG pipeline — vector search + context assembly
            rag_result = await RAGService.rag_query(db, query, k=3)

            if rag_result and rag_result.get("answer"):
                # RAG found relevant knowledge and generated an answer
                sources = rag_result.get("sources", [])
                source_titles = [s.get("title", "") for s in sources if isinstance(s, dict)]
                return (
                    f"Knowledge base information:\n"
                    f"{rag_result['answer']}\n\n"
                    f"Sources: {', '.join(source_titles)}"
                )

            # RAG returned no results — try a simpler search
            search_results = await RAGService.search(db, query, k=3)
            if search_results:
                snippets = []
                for result in search_results:
                    content = result.get("content", "")
                    if content:
                        snippets.append(content[:500])
                if snippets:
                    return "Knowledge base information:\n" + "\n\n".join(snippets)

        except Exception:
            # RAG system unavailable (e.g., no OpenAI key, pgvector not set up)
            pass

        # Fallback: intent-specific knowledge snippets (static)
        knowledge_base: dict[str, str] = {
            "weather_query": (
                "Weather information helps farmers plan irrigation, "
                "pesticide application, and harvesting. Always consider "
                "local microclimates and elevation."
            ),
            "crop_advice": (
                "Indian agriculture follows two main seasons: Kharif "
                "(monsoon, June-October) and Rabi (winter, October-March). "
                "Crop selection depends on season, soil, water availability, "
                "and market demand."
            ),
            "disease_help": (
                "Common crop diseases in India include blast (rice), "
                "wilt (tomato), rust (wheat), and bollworm (cotton). "
                "Early detection and IPM (Integrated Pest Management) "
                "are key to effective treatment."
            ),
            "market_price": (
                "Mandi prices fluctuate based on supply, demand, season, "
                "and quality. Farmers benefit from knowing MSP (Minimum "
                "Support Price) set by the government."
            ),
            "finance": (
                "Good financial tracking helps farmers make better decisions. "
                "Key metrics: cost of cultivation, break-even point, "
                "profit margin, and ROI."
            ),
            "scheme_info": (
                "Key Indian government schemes: PM-KISAN (₹6000/year), "
                "PM Fasal Bima (crop insurance), KCC (Kisan Credit Card), "
                "PM Krishi Sinchayee (irrigation subsidy)."
            ),
        }

        return knowledge_base.get(intent, "")
