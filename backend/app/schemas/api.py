"""Standard API response wrapper schemas."""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    total: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(default=20)
    total_pages: int = Field(default=0)
    has_next: bool = Field(default=False)
    has_prev: bool = Field(default=False)


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope used across all endpoints.

    Provides a consistent response format for success and error cases.
    """

    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(default="OK", description="Human-readable message")
    data: Optional[T] = Field(default=None, description="Response payload")
    errors: Optional[list[dict[str, str]]] = Field(
        default=None, description="List of validation or business errors"
    )
    pagination: Optional[PaginationMeta] = Field(
        default=None, description="Pagination info for list endpoints"
    )

    @classmethod
    def ok(cls, data: Any = None, message: str = "OK") -> "APIResponse":
        """Create a successful response."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(
        cls,
        message: str = "Error",
        errors: Optional[list[dict[str, str]]] = None,
    ) -> "APIResponse":
        """Create an error response."""
        return cls(success=False, message=message, errors=errors)

    @classmethod
    def paginated(
        cls,
        data: Any,
        total: int,
        page: int,
        page_size: int,
        message: str = "OK",
    ) -> "APIResponse":
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            success=True,
            message=message,
            data=data,
            pagination=PaginationMeta(
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            ),
        )
