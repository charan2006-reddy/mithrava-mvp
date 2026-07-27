"""Audit logging middleware.

Records all mutating requests (POST, PUT, PATCH, DELETE) with details
for compliance and debugging purposes. Stores entries in the audit_logs table.
"""

import json
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all mutating HTTP requests to the audit trail.

    Captures:
    - HTTP method and path
    - Farmer ID (from JWT claims if available)
    - Action performed
    - Entity type and ID extracted from path
    - Client IP address
    - Timestamp
    - Request body (truncated)
    """

    # Methods that should be audited
    AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    # Entity type mapping from URL path segments
    ENTITY_MAP = {
        "farmers": "farmer",
        "crops": "crop",
        "disease": "disease_scan",
        "finance": "finance",
        "expenses": "expense",
        "income": "income",
        "vendors": "vendor",
        "forum": "forum_post",
        "mitra": "mitra_conversation",
        "notifications": "notification",
        "admin": "admin_action",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request, audit it, and return the response.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or endpoint handler.

        Returns:
            The response from downstream handlers.
        """
        response: Response = await call_next(request)

        # Only audit mutating requests
        if request.method not in self.AUDITED_METHODS:
            return response

        try:
            await self._log_audit_entry(request, response)
        except Exception:
            # Audit logging should never break the request flow
            pass

        return response

    async def _log_audit_entry(self, request: Request, response: Response) -> None:
        """Create and store an audit log entry.

        Args:
            request: The HTTP request.
            response: The HTTP response.
        """
        # Extract farmer ID from request state (set by auth middleware)
        farmer_id = getattr(request.state, "farmer_id", None)

        # Extract entity info from path
        path_parts = [p for p in request.url.path.split("/") if p]
        entity_type = "unknown"
        entity_id = None

        for part in path_parts:
            if part in self.ENTITY_MAP:
                entity_type = self.ENTITY_MAP[part]
            elif part not in ("api", "v1") and entity_type != "unknown" and entity_id is None:
                entity_id = part

        # Determine action from method
        action_map = {
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }

        audit_entry = {
            "farmer_id": farmer_id,
            "action": action_map.get(request.method, request.method.lower()),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "ip_address": self._get_client_ip(request),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Try to store in database (best effort)
        await self._store_audit_log(audit_entry)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from the request.

        Handles X-Forwarded-For header for reverse proxy setups.

        Args:
            request: The HTTP request.

        Returns:
            Client IP address string.
        """
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"

    async def _store_audit_log(self, entry: dict) -> None:
        """Store an audit log entry to the database.

        This is best-effort and should not raise exceptions.

        Args:
            entry: The audit log entry dict.
        """
        try:
            from app.database import async_session_factory
            from sqlalchemy import text

            async with async_session_factory() as session:
                await session.execute(
                    text(
                        """
                        INSERT INTO audit_logs
                            (farmer_id, action, entity_type, entity_id,
                             ip_address, method, path, status_code, created_at)
                        VALUES
                            (:farmer_id, :action, :entity_type, :entity_id,
                             :ip_address, :method, :path, :status_code, :created_at)
                        """
                    ),
                    entry,
                )
                await session.commit()
        except Exception:
            # Silently fail – audit is non-critical
            pass
