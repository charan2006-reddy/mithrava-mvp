"""Forum/community post and comment schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ForumPostCreate(BaseModel):
    """Schema for creating a new forum post."""

    title: str = Field(..., min_length=5, max_length=200, description="Post title")
    content: str = Field(..., min_length=10, max_length=5000, description="Post body")
    category: str = Field(
        default="general",
        pattern=r"^(general|crop_care|pest_control|weather|market|finance|tips|question)$",
        description="Post category",
    )
    tags: Optional[list[str]] = Field(
        default=None, max_length=10, description="Up to 10 tags"
    )
    image_urls: Optional[list[str]] = Field(
        default=None, max_length=5, description="Up to 5 images"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Best practices for rice farming in monsoon",
                    "content": "I have been farming rice for 10 years and here are my tips...",
                    "category": "crop_care",
                    "tags": ["rice", "monsoon", "tips"],
                }
            ]
        }
    }


class ForumPostResponse(BaseModel):
    """Schema for forum post data in API responses."""

    id: str
    farmer_id: str
    farmer_name: str
    title: str
    content: str
    category: str
    tags: list[str] = Field(default_factory=list)
    image_urls: list[str] = Field(default_factory=list)
    likes_count: int = Field(default=0)
    comments_count: int = Field(default=0)
    is_liked_by_me: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ForumCommentCreate(BaseModel):
    """Schema for adding a comment to a forum post."""

    content: str = Field(..., min_length=1, max_length=2000)

    model_config = {
        "json_schema_extra": {"examples": [{"content": "Great advice! Thanks for sharing."}]}
    }


class ForumCommentResponse(BaseModel):
    """Schema for forum comment data in API responses."""

    id: str
    post_id: str
    farmer_id: str
    farmer_name: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
