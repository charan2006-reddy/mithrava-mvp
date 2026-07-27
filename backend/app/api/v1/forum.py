"""Forum/community API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache
from app.database import get_db
from app.dependencies import get_current_user
from app.models.farmer import Farmer
from app.schemas.forum import ForumCommentCreate, ForumPostCreate
from app.services.forum_service import ForumService

router = APIRouter(prefix="/forum", tags=["Forum"])


@router.get("/")
async def list_posts(
    category: str = Query(default=None, description="Filter by category"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List forum posts with optional category filter."""
    data = await ForumService.list_posts(db, category=category, skip=skip, limit=limit)
    return {
        "success": True,
        "message": "OK",
        "data": data,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    body: ForumPostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Create a new forum post."""
    data = await ForumService.create_post(
        db,
        farmer_id=str(current_user.id),
        title=body.title,
        content=body.content,
        category=body.category,
        tags=body.tags,
        image_urls=body.image_urls,
    )
    await cache.invalidate_pattern("forum:list")
    return {
        "success": True,
        "message": "Post created successfully",
        "data": data,
    }


@router.get("/{post_id}/comments")
async def list_comments(
    post_id: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """List comments for a forum post."""
    data = await ForumService.list_comments(db, post_id=post_id, skip=skip, limit=limit)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )
    return {
        "success": True,
        "message": "OK",
        "data": data,
    }


@router.post("/{post_id}/comment", status_code=status.HTTP_201_CREATED)
async def add_comment(
    post_id: str,
    body: ForumCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Add a comment to a forum post."""
    data = await ForumService.add_comment(
        db,
        post_id=post_id,
        farmer_id=str(current_user.id),
        content=body.content,
    )
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )
    await cache.invalidate_pattern("forum:list")
    return {
        "success": True,
        "message": "Comment added successfully",
        "data": data,
    }


@router.post("/{post_id}/like")
async def toggle_like(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Farmer = Depends(get_current_user),
):
    """Toggle like/unlike on a forum post."""
    data = await ForumService.toggle_like(
        db,
        post_id=post_id,
        farmer_id=str(current_user.id),
    )
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )
    await cache.invalidate_pattern("forum:list")
    return {
        "success": True,
        "message": "Like toggled successfully",
        "data": data,
    }
