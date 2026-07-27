"""File storage service for images.

Supports local filesystem storage for development and S3-compatible
storage for production. Handles image validation, compression, and upload.
"""

import io
import os
import uuid
from pathlib import Path
from typing import Optional

import httpx
from fastapi import UploadFile

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")  # "local" or "s3"
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "./uploads")
LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL", "http://localhost:8000/uploads")
S3_BUCKET = os.getenv("S3_BUCKET", "mithrava-uploads")
S3_REGION = os.getenv("S3_REGION", "ap-south-1")
S3_BASE_URL = os.getenv("S3_BASE_URL", f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
DEFAULT_MAX_SIZE_MB = 5


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def upload_image(file: UploadFile, folder: str = "images") -> str:
    """Upload an image file to storage and return its URL.

    Args:
        file: The uploaded FastAPI UploadFile.
        folder: Subfolder within storage (e.g., "crops", "diseases").

    Returns:
        The publicly accessible URL of the uploaded image.

    Raises:
        ValueError: If the file is invalid or too large.
        RuntimeError: If storage operation fails.
    """
    if not await validate_image(file):
        raise ValueError(
            f"Invalid image. Allowed types: {ALLOWED_EXTENSIONS}, "
            f"Max size: {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB"
        )

    # Generate unique filename
    file_ext = Path(file.filename or "upload.jpg").suffix.lower()
    unique_name = f"{folder}/{uuid.uuid4().hex}{file_ext}"

    # Read file content
    content = await file.read()

    # Compress if needed
    content = await compress_image(content, max_size_mb=DEFAULT_MAX_SIZE_MB)

    if STORAGE_BACKEND == "s3":
        return await _upload_to_s3(content, unique_name)
    else:
        return await _upload_to_local(content, unique_name)


async def delete_image(url: str) -> bool:
    """Delete an image from storage by its URL.

    Args:
        url: The image URL to delete.

    Returns:
        True if deletion succeeded, False otherwise.
    """
    try:
        if STORAGE_BACKEND == "s3":
            # Extract key from URL
            key = url.replace(f"{S3_BASE_URL}/", "")
            return await _delete_from_s3(key)
        else:
            # Extract path from URL
            path_str = url.replace(f"{LOCAL_BASE_URL}/", "")
            file_path = Path(LOCAL_STORAGE_PATH) / path_str
            if file_path.exists():
                file_path.unlink()
            return True
    except Exception:
        return False


async def validate_image(file: UploadFile) -> bool:
    """Validate that an uploaded file is an acceptable image.

    Checks file extension and size.

    Args:
        file: The uploaded FastAPI UploadFile.

    Returns:
        True if the file passes validation, False otherwise.
    """
    # Check extension
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False

    # Check content type
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        return False

    # Check file size (read and reset)
    content = await file.read()
    await file.seek(0)
    if len(content) > MAX_FILE_SIZE_BYTES:
        return False

    return True


async def compress_image(
    file_content: bytes,
    max_size_mb: int = DEFAULT_MAX_SIZE_MB,
) -> bytes:
    """Compress image content if it exceeds the maximum size.

    Uses Pillow for JPEG compression. Falls back to returning original
    content if compression fails or Pillow is not installed.

    Args:
        file_content: Raw image bytes.
        max_size_mb: Maximum allowed size in megabytes.

    Returns:
        Compressed image bytes, or original if already within limit.
    """
    max_bytes = max_size_mb * 1024 * 1024
    if len(file_content) <= max_bytes:
        return file_content

    try:
        from PIL import Image

        img = Image.open(io.BytesIO(file_content))
        # Convert RGBA to RGB for JPEG
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        quality = 85
        buffer = io.BytesIO()

        while quality > 10:
            buffer.seek(0)
            buffer.truncate()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            if buffer.tell() <= max_bytes:
                break
            quality -= 10

        return buffer.getvalue()
    except ImportError:
        # Pillow not installed, return original
        return file_content


# ---------------------------------------------------------------------------
# Local storage helpers
# ---------------------------------------------------------------------------


async def _upload_to_local(content: bytes, path: str) -> str:
    """Save file to local filesystem.

    Args:
        content: File bytes.
        path: Relative path within storage.

    Returns:
        Public URL of the saved file.
    """
    full_path = Path(LOCAL_STORAGE_PATH) / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(content)
    return f"{LOCAL_BASE_URL}/{path}"


async def _delete_from_s3(key: str) -> bool:
    """Delete a file from S3 storage.

    Args:
        key: S3 object key.

    Returns:
        True if deletion succeeded.
    """
    try:
        import aioboto3

        session = aioboto3.Session()
        async with session.client("s3") as s3:
            await s3.delete_object(Bucket=S3_BUCKET, Key=key)
        return True
    except Exception:
        return False


async def _upload_to_s3(content: bytes, key: str) -> str:
    """Upload file to S3-compatible storage.

    Args:
        content: File bytes.
        key: S3 object key.

    Returns:
        Public URL of the uploaded file.
    """
    try:
        import aioboto3

        session = aioboto3.Session()
        async with session.client("s3") as s3:
            await s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=content,
                ContentType="image/jpeg",
            )
        return f"{S3_BASE_URL}/{key}"
    except Exception as exc:
        raise RuntimeError(f"Failed to upload to S3: {exc}") from exc
