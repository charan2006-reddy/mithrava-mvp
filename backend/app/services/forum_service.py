"""Forum service layer.

Provides business logic for forum posts, comments, and likes.
"""

from typing import Optional, List, Dict, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cached
from app.models.forum import ForumPost, ForumComment, ForumLike


class ForumService:
    """Business logic for forum posts, comments, and likes."""

    @staticmethod
    @cached(ttl_seconds=60, prefix="forum:list")
    async def list_posts(
        db: AsyncSession,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """List forum posts with optional category filter.

        Args:
            db: Async database session.
            category: Optional category filter.
            skip: Pagination offset.
            limit: Maximum number of posts to return.

        Returns:
            Dict with posts list, total count, and pagination info.
        """
        query = select(ForumPost)
        if category:
            query = query.where(ForumPost.category == category)
        query = query.offset(skip).limit(limit).order_by(ForumPost.created_at.desc())
        result = await db.execute(query)
        posts = list(result.scalars().all())

        count_query = select(func.count()).select_from(ForumPost)
        if category:
            count_query = count_query.where(ForumPost.category == category)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        return {
            "posts": [
                {
                    "id": str(p.id),
                    "farmer_id": str(p.farmer_id),
                    "title": p.title,
                    "content": p.content[:200] + "..." if len(p.content) > 200 else p.content,
                    "category": p.category,
                    "tags": p.tags or [],
                    "likes_count": p.likes_count,
                    "comments_count": p.comments_count,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in posts
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total,
        }

    @staticmethod
    async def create_post(
        db: AsyncSession,
        farmer_id: str,
        title: str,
        content: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        image_urls: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new forum post.

        Args:
            db: Async database session.
            farmer_id: The creating farmer's ID.
            title: Post title.
            content: Post body.
            category: Post category.
            tags: Optional list of tags.
            image_urls: Optional list of image URLs.

        Returns:
            Dict with the created post's summary data.
        """
        post = ForumPost(
            farmer_id=farmer_id,
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            image_urls=image_urls or [],
        )
        db.add(post)
        await db.flush()
        await db.refresh(post)
        return {
            "id": str(post.id),
            "title": post.title,
            "content": post.content,
            "category": post.category,
            "tags": post.tags,
        }

    @staticmethod
    async def list_comments(
        db: AsyncSession,
        post_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> Optional[Dict[str, Any]]:
        """List comments for a forum post.

        Args:
            db: Async database session.
            post_id: The parent post's ID.
            skip: Pagination offset.
            limit: Maximum number of comments to return.

        Returns:
            Dict with comments list and pagination info, or None if post not found.
        """
        # Verify post exists
        post_result = await db.execute(select(ForumPost).where(ForumPost.id == post_id))
        post = post_result.scalar_one_or_none()
        if post is None:
            return None

        query = (
            select(ForumComment)
            .where(ForumComment.post_id == post_id)
            .order_by(ForumComment.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        comments = list(result.scalars().all())

        count_query = (
            select(func.count())
            .select_from(ForumComment)
            .where(ForumComment.post_id == post_id)
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        return {
            "comments": [
                {
                    "id": str(c.id),
                    "content": c.content,
                    "farmer_id": str(c.farmer_id),
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in comments
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    async def add_comment(
        db: AsyncSession,
        post_id: str,
        farmer_id: str,
        content: str,
    ) -> Optional[Dict[str, Any]]:
        """Add a comment to a forum post.

        Args:
            db: Async database session.
            post_id: The parent post's ID.
            farmer_id: The commenting farmer's ID.
            content: Comment text.

        Returns:
            Dict with the created comment's data, or None if post not found.
        """
        post_result = await db.execute(select(ForumPost).where(ForumPost.id == post_id))
        post = post_result.scalar_one_or_none()
        if post is None:
            return None

        comment = ForumComment(
            post_id=post_id,
            farmer_id=farmer_id,
            content=content,
        )
        db.add(comment)
        post.comments_count += 1
        await db.flush()
        await db.refresh(comment)

        return {
            "id": str(comment.id),
            "content": comment.content,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
        }

    @staticmethod
    async def toggle_like(
        db: AsyncSession,
        post_id: str,
        farmer_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Toggle like/unlike on a forum post.

        Args:
            db: Async database session.
            post_id: The target post's ID.
            farmer_id: The farmer's ID performing the action.

        Returns:
            Dict with liked status and updated like count, or None if post not found.
        """
        post_result = await db.execute(select(ForumPost).where(ForumPost.id == post_id))
        post = post_result.scalar_one_or_none()
        if post is None:
            return None

        existing_like = await db.execute(
            select(ForumLike).where(
                ForumLike.post_id == post_id,
                ForumLike.farmer_id == farmer_id,
            )
        )
        like = existing_like.scalar_one_or_none()

        if like:
            await db.delete(like)
            post.likes_count = max(0, post.likes_count - 1)
            liked = False
        else:
            new_like = ForumLike(post_id=post_id, farmer_id=farmer_id)
            db.add(new_like)
            post.likes_count += 1
            liked = True

        await db.flush()

        return {
            "liked": liked,
            "likes_count": post.likes_count,
        }
