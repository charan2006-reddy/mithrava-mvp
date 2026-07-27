"""Mitra AI assistant conversation schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MitraMessageCreate(BaseModel):
    """Schema for sending a message to Mitra AI."""

    content: str = Field(..., min_length=1, max_length=5000, description="Message text")
    conversation_id: Optional[str] = Field(
        default=None, description="Existing conversation ID (creates new if omitted)"
    )
    language: str = Field(default="en", description="Preferred language for response")
    voice_data: Optional[str] = Field(
        default=None,
        description="Base64-encoded voice data for voice messages",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "What is the best time to plant tomatoes in Telangana?",
                    "language": "en",
                }
            ]
        }
    }


class MitraMessageResponse(BaseModel):
    """Schema for a Mitra AI message in API responses."""

    id: str
    conversation_id: str
    role: str = Field(..., pattern=r"^(user|assistant)$", description="Message role")
    content: str
    intent: Optional[str] = Field(default=None, description="Detected user intent")
    actions_taken: Optional[list[dict]] = Field(
        default=None, description="Actions executed by Mitra"
    )
    created_at: datetime

    model_config = {"from_attributes": True}


class MitraConversationResponse(BaseModel):
    """Schema for Mitra conversation metadata."""

    id: str
    farmer_id: str
    title: Optional[str] = None
    language: str = "en"
    created_at: datetime
    updated_at: datetime
    message_count: int = Field(default=0)
    last_message_preview: Optional[str] = Field(
        default=None, description="Preview of the last message"
    )

    model_config = {"from_attributes": True}
