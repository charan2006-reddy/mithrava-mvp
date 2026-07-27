"""LLM integration services for Mitra AI, disease detection, and RAG.

Supports Ollama (local), Gemini (free), OpenAI (cloud), and provides Vision analysis
for crop disease detection, embedding generation for RAG, and context-aware
answer generation.

Priority: Gemini (free) → OpenAI (paid) → Ollama (local)
"""

import base64
import json
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger("mithrava.llm")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", "gemini-2.0-flash")


# ---------------------------------------------------------------------------
# Farming system prompt
# ---------------------------------------------------------------------------


def get_farming_system_prompt(language: str = "en") -> str:
    """Return the system prompt for the Mitra AI farming assistant.

    The prompt is tailored to Indian agriculture and responds in the
    requested language.

    Args:
        language: Language code (en, hi, te, ta, etc.).

    Returns:
        System prompt string.
    """
    language_names = {
        "en": "English",
        "hi": "Hindi",
        "te": "Telugu",
        "ta": "Tamil",
        "kn": "Kannada",
        "ml": "Malayalam",
        "mr": "Marathi",
        "gu": "Gujarati",
        "bn": "Bengali",
        "pa": "Punjabi",
    }
    lang_name = language_names.get(language, "English")

    return (
        f"You are Mitra, a friendly and knowledgeable AI farming assistant created by "
        f"Mithrava. You help Indian farmers with:\n\n"
        f"1. Crop planning and calendar management\n"
        f"2. Disease diagnosis and treatment recommendations\n"
        f"3. Weather-based farming advice\n"
        f"4. Market price information and selling strategies\n"
        f"5. Financial planning and expense tracking\n"
        f"6. Government schemes and subsidies information\n"
        f"7. Organic farming and sustainable practices\n"
        f"8. Pest control and soil health\n\n"
        f"Rules:\n"
        f"- Always respond in {lang_name}.\n"
        f"- Be concise and practical — farmers need actionable advice.\n"
        f"- Use simple language that rural farmers can understand.\n"
        f"- When unsure, recommend consulting a local agricultural extension officer.\n"
        f"- Never provide dangerous or illegal advice.\n"
        f"- Reference local Indian farming practices and conditions.\n"
        f"- If asked about prices, note that prices vary by region and time.\n"
        f"- For disease diagnosis, always recommend confirming with a local expert.\n"
    )


# ---------------------------------------------------------------------------
# Ollama LLM (local)
# ---------------------------------------------------------------------------


async def ask_ollama(prompt: str, context: Optional[str] = None) -> str:
    """Send a prompt to the local Ollama LLM and return the response.

    Args:
        prompt: The user prompt/query.
        context: Optional context string to prepend.

    Returns:
        The model's response text.
    """
    full_prompt = ""
    if context:
        full_prompt = f"Context:\n{context}\n\nUser question: {prompt}\n\nAnswer:"
    else:
        full_prompt = prompt

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")


# ---------------------------------------------------------------------------
# OpenAI LLM (cloud) — requires OPENAI_API_KEY
# ---------------------------------------------------------------------------


async def ask_openai(
    prompt: str,
    context: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> str:
    """Send a prompt to OpenAI and return the response.

    Args:
        prompt: The user prompt/query.
        context: Optional context string to inject into the conversation.
        system_prompt: Optional system prompt to set the assistant's behavior.

    Returns:
        The model's response text.

    Raises:
        RuntimeError: If OPENAI_API_KEY is not set or API call fails.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured")

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if context:
        messages.append({"role": "system", "content": f"Relevant context:\n{context}"})

    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=2048,
    )
    return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Gemini LLM (free tier: 15 RPM, 1M tokens/day)
# ---------------------------------------------------------------------------


async def ask_gemini(
    prompt: str,
    context: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> str:
    """Send a prompt to Google Gemini Flash (free tier) and return the response.

    Args:
        prompt: The user prompt/query.
        context: Optional context string to inject into the conversation.
        system_prompt: Optional system prompt to set the assistant's behavior.

    Returns:
        The model's response text.

    Raises:
        RuntimeError: If GEMINI_API_KEY is not set or API call fails.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured")

    # Build the full prompt with system context
    full_parts = []
    if system_prompt:
        full_parts.append(f"System Instructions:\n{system_prompt}")
    if context:
        full_parts.append(f"Relevant context:\n{context}")
    full_parts.append(f"User: {prompt}")

    full_text = "\n\n".join(full_parts)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{"parts": [{"text": full_text}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    # Extract text from Gemini response
    candidates = data.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts:
            return parts[0].get("text", "")

    raise RuntimeError("Gemini returned empty response")


# ---------------------------------------------------------------------------
# Unified LLM: Gemini (free) → OpenAI (paid) → Ollama (local)
# ---------------------------------------------------------------------------


async def ask_llm(
    prompt: str,
    context: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> str:
    """Ask the best available LLM. Tries Gemini (free) → OpenAI (paid) → Ollama (local).

    This is the main entry point for all chat completions.

    Args:
        prompt: The user prompt/query.
        context: Optional context string.
        system_prompt: Optional system prompt.

    Returns:
        The model's response text.

    Raises:
        RuntimeError: If all providers fail.
    """
    errors = []

    # Provider 1: Gemini (free)
    if GEMINI_API_KEY:
        try:
            return await ask_gemini(prompt, context, system_prompt)
        except Exception as exc:
            errors.append(f"Gemini: {exc}")
            logger.warning("LLM: Gemini failed — %s", exc)

    # Provider 2: OpenAI (paid)
    if OPENAI_API_KEY:
        try:
            return await ask_openai(prompt, context, system_prompt)
        except Exception as exc:
            errors.append(f"OpenAI: {exc}")
            logger.warning("LLM: OpenAI failed — %s", exc)

    # Provider 3: Ollama (local)
    try:
        return await ask_ollama(prompt)
    except Exception as exc:
        errors.append(f"Ollama: {exc}")
        logger.warning("LLM: Ollama failed — %s", exc)

    # All failed
    raise RuntimeError(f"All LLM providers failed: {'; '.join(errors)}")


# ---------------------------------------------------------------------------
# OpenAI Vision – Enhanced disease image analysis
# ---------------------------------------------------------------------------

DISEASE_VISION_PROMPT = """You are an expert Indian agricultural pathologist. Analyze this plant/crop image.

Identify:
1. Crop type (if visible)
2. Disease or pest (if any) — be specific with scientific name if possible
3. Confidence level (0-100%)
4. Stage of disease (early/advanced/severe)
5. Symptoms visible in the image

Provide treatment recommendations in simple language:
- Organic treatment (neem oil, bio-pesticides, cultural practices)
- Chemical treatment (specific pesticide names available in India)
- Prevention tips for future

Format your response as JSON:
{
  "crop_detected": "string",
  "disease_name": "string or null if healthy",
  "confidence": 0.0 to 1.0,
  "severity": "low|medium|high|critical",
  "is_healthy": boolean,
  "description": "what you see in the image",
  "organic_treatment": ["list of organic treatments"],
  "chemical_treatment": ["list of chemical treatments with Indian product names"],
  "prevention": ["prevention tips"],
  "urgency": "immediate|within_week|when_convenient"
}"""


async def analyze_image_with_vision(image_base64: str, prompt: str) -> dict:
    """Analyze an image using the best available Vision API.

    Tries Gemini (free) → OpenAI (paid).

    Args:
        image_base64: Base64-encoded image data.
        prompt: The analysis prompt to send with the image.

    Returns:
        Parsed JSON dict from the model's response.
    """
    errors = []

    # Provider 1: Gemini (free)
    if GEMINI_API_KEY:
        try:
            return await _analyze_image_gemini(image_base64, prompt)
        except Exception as exc:
            errors.append(f"Gemini: {exc}")
            logger.warning("Vision: Gemini failed — %s", exc)

    # Provider 2: OpenAI (paid)
    if OPENAI_API_KEY:
        try:
            return await _analyze_image_openai(image_base64, prompt)
        except Exception as exc:
            errors.append(f"OpenAI: {exc}")
            logger.warning("Vision: OpenAI failed — %s", exc)

    logger.error("All vision providers failed: %s", errors)
    return _default_disease_response()


async def _analyze_image_gemini(image_base64: str, prompt: str) -> dict:
    """Analyze image using Gemini Flash (free tier)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_VISION_MODEL}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1500,
            "responseMimeType": "application/json",
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    candidates = data.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts:
            text = parts[0].get("text", "{}")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Gemini vision response as JSON")

    return _default_disease_response()


async def _analyze_image_openai(image_base64: str, prompt: str) -> dict:
    """Analyze image using OpenAI Vision (paid)."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    response = await client.chat.completions.create(
        model=OPENAI_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high",
                        },
                    },
                ],
            },
        ],
        max_tokens=1500,
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    content = response.choices[0].message.content or "{}"
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return _default_disease_response()


def _default_disease_response() -> dict:
    """Return a safe default response when analysis fails."""
    return {
        "crop_detected": "Unknown",
        "disease_name": None,
        "confidence": 0.0,
        "severity": "medium",
        "is_healthy": False,
        "description": "Unable to fully analyze the image. Please consult a local agricultural expert.",
        "organic_treatment": [],
        "chemical_treatment": [],
        "prevention": ["Consult a local agricultural extension officer for accurate diagnosis."],
        "urgency": "when_convenient",
    }


async def analyze_disease_image(image_base64: str) -> dict:
    """Analyze a crop image for disease detection.

    Tries Gemini (free) → OpenAI (paid).

    Args:
        image_base64: Base64-encoded image data.

    Returns:
        Dict with disease analysis results.
    """
    system_msg = (
        "You are an expert plant pathologist specializing in Indian crops. "
        "Analyze the uploaded crop image and provide:\n"
        "1. disease_name: The most likely disease or condition\n"
        "2. confidence: A confidence score between 0 and 1\n"
        "3. severity: One of 'low', 'medium', 'high', 'critical'\n"
        "4. treatment: Detailed treatment recommendation in simple language\n"
        "5. alternative_diagnoses: List of other possible diagnoses with confidence\n\n"
        "Respond in valid JSON format only."
    )

    prompt = "Please analyze this crop image for any diseases or health issues."
    errors = []

    # Provider 1: Gemini (free)
    if GEMINI_API_KEY:
        try:
            result = await _analyze_disease_gemini(image_base64, system_msg, prompt)
            return _ensure_disease_keys(result)
        except Exception as exc:
            errors.append(f"Gemini: {exc}")
            logger.warning("Disease analysis: Gemini failed — %s", exc)

    # Provider 2: OpenAI (paid)
    if OPENAI_API_KEY:
        try:
            result = await _analyze_disease_openai(image_base64, system_msg, prompt)
            return _ensure_disease_keys(result)
        except Exception as exc:
            errors.append(f"OpenAI: {exc}")
            logger.warning("Disease analysis: OpenAI failed — %s", exc)

    logger.error("All disease analysis providers failed: %s", errors)
    return _ensure_disease_keys(_default_disease_response())


async def _analyze_disease_gemini(image_base64: str, system_msg: str, prompt: str) -> dict:
    """Disease analysis using Gemini Flash (free tier)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_VISION_MODEL}:generateContent?key={GEMINI_API_KEY}"

    full_prompt = f"{system_msg}\n\n{prompt}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json",
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    candidates = data.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts:
            text = parts[0].get("text", "{}")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return _default_disease_response()

    return _default_disease_response()


async def _analyze_disease_openai(image_base64: str, system_msg: str, prompt: str) -> dict:
    """Disease analysis using OpenAI Vision (paid)."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    response = await client.chat.completions.create(
        model=OPENAI_VISION_MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high",
                        },
                    },
                ],
            },
        ],
        max_tokens=1024,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return _default_disease_response()


def _ensure_disease_keys(result: dict) -> dict:
    """Ensure all required keys exist in disease analysis result."""
    result.setdefault("disease_name", "Unknown")
    result.setdefault("confidence", 0.0)
    result.setdefault("severity", "medium")
    result.setdefault("treatment", "Please consult a local agricultural expert.")
    result.setdefault("alternative_diagnoses", [])
    result.setdefault("is_healthy", False)
    result.setdefault("description", "")
    result.setdefault("organic_treatment", [])
    result.setdefault("chemical_treatment", [])
    result.setdefault("prevention", [])
    result.setdefault("urgency", "when_convenient")
    return result


# ---------------------------------------------------------------------------
# OpenAI Embeddings for RAG
# ---------------------------------------------------------------------------


async def generate_embedding(text: str) -> list[float]:
    """Generate a vector embedding for the given text.

    Uses OpenAI text-embedding-3-small (requires OPENAI_API_KEY).

    Args:
        text: The text to embed.

    Returns:
        List of floats representing the embedding vector.

    Raises:
        RuntimeError: If OPENAI_API_KEY is not set or API call fails.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "Embeddings require OPENAI_API_KEY. "
            "Set OPENAI_API_KEY or disable RAG features."
        )

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


async def generate_embeddings(text: str) -> list[float]:
    """Generate embeddings for text. Alias for generate_embedding."""
    return await generate_embedding(text)


# ---------------------------------------------------------------------------
# Context-aware generation (Ollama with RAG context)
# ---------------------------------------------------------------------------


async def generate_with_context(question: str, context: str) -> str:
    """Generate an answer using Ollama with retrieved RAG context.

    Builds a structured prompt that instructs the model to answer based
    on the provided context, falling back to general knowledge if the
    context is insufficient.

    Args:
        question: The user's question.
        context: Retrieved context from the knowledge base.

    Returns:
        Generated answer string.
    """
    rag_prompt = (
        "You are Mitra, an expert Indian agricultural AI assistant by Mithrava. "
        "Answer the farmer's question based on the following knowledge base context. "
        "If the context does not contain enough information, use your general "
        "knowledge about Indian agriculture, but mention that the answer is from "
        "general knowledge rather than verified sources.\n\n"
        "IMPORTANT GUIDELINES:\n"
        "- Answer in simple language the farmer can understand\n"
        "- Be practical and actionable\n"
        "- Always mention if specific advice needs verification with local experts\n"
        "- For chemical treatments, always mention proper dosage and safety precautions\n"
        "- Reference Indian conditions, brands, and practices\n\n"
        f"KNOWLEDGE BASE CONTEXT:\n{context}\n\n"
        f"FARMER'S QUESTION: {question}\n\n"
        "ANSWER:"
    )

    try:
        return await ask_llm(
            prompt=question,
            context=context,
            system_prompt=get_farming_system_prompt(),
        )
    except Exception as exc:
        logger.error("RAG generation failed: %s", exc)
        return (
            "I apologize, but I'm unable to generate an answer right now. "
            "Please try again later or consult your local agricultural extension officer."
        )
