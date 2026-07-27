"""Request ID middleware.

Assigns a unique UUID v4 to every inbound request. The ID is:
- Stored on ``request.state.request_id`` for downstream handlers.
- Returned in the ``X-Request-ID`` response header.
- If the client already sends an ``X-Request-ID`` header, it is
  validated (UUID format) and reused; otherwise a fresh one is generated.

This enables distributed tracing across microservices and makes
debugging production issues dramatically easier.
"""

import uuid
import logging
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("mithrava.request_id")


def _is_valid_uuid(value: str) -> bool:
    """Check whether *value* is a valid UUID string."""
    try:
        uuid.UUID(value, version=4)
        return True
    except ValueError:
        return False


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that attaches a unique request ID to every request.

    The request ID is propagated to:
    - ``request.state.request_id`` — for use in handlers and services.
    - ``X-Request-ID`` response header — for client-side correlation.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request, attach an ID, and propagate it to the response.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or endpoint handler.

        Returns:
            Response with ``X-Request-ID`` header set.
        """
        # Reuse client-provided ID if valid, otherwise generate a new one
        client_id: Optional[str] = request.headers.get("x-request-id")
        if client_id and _is_valid_uuid(client_id):
            request_id = client_id
        else:
            request_id = str(uuid.uuid4())

        # Make available to all downstream code
        request.state.request_id = request_id

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response
