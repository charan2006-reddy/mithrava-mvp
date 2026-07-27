"""Structured JSON logging configuration.

Provides a ``JSONFormatter`` that outputs every log line as a single JSON
object, making log aggregation and querying in production (ELK, Datadog,
CloudWatch, etc.) trivial.

Features:
- JSON-formatted output with standard fields (timestamp, level, logger, message).
- Context-var aware — automatically includes ``request_id`` and ``farmer_id``
  when set on ``contextvars.ContextVar`` instances.
- ``TextFormatter`` fallback for local development.
- ``setup_logging()`` helper that configures the root logger in one call.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from contextvars import ContextVar
from typing import Optional

# ---------------------------------------------------------------------------
# Context variables — populated by middleware, read by loggers
# ---------------------------------------------------------------------------

request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
farmer_id_var: ContextVar[Optional[str]] = ContextVar("farmer_id", default=None)


# ---------------------------------------------------------------------------
# JSON Formatter
# ---------------------------------------------------------------------------

class JSONFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects.

    Output schema::

        {
            "timestamp": "2025-07-24T12:00:00.000Z",
            "level": "INFO",
            "logger": "mithrava.api",
            "message": "User logged in",
            "request_id": "abc-123",
            "farmer_id": "42",
            "module": "auth",
            "function": "login",
            "line": 128
        }
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Attach context vars when present
        rid = request_id_var.get()
        if rid:
            log_entry["request_id"] = rid

        fid = farmer_id_var.get()
        if fid:
            log_entry["farmer_id"] = fid

        # Source location — useful during debugging, cheap to include
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        log_entry["module"] = record.module
        log_entry["function"] = record.funcName
        log_entry["line"] = record.lineno

        return json.dumps(log_entry, default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Text Formatter (dev fallback)
# ---------------------------------------------------------------------------

class TextFormatter(logging.Formatter):
    """Human-readable formatter for local development.

    Output format::

        2025-07-24 12:00:00 [INFO ] mithrava.api: User logged in [req=abc-123]
    """

    LEVEL_WIDTH = 7

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(self.LEVEL_WIDTH)
        msg = record.getMessage()

        parts = [f"{ts} [{level}] {record.name}: {msg}"]

        # Context vars
        rid = request_id_var.get()
        if rid:
            parts.append(f" [req={rid[:8]}]")

        fid = farmer_id_var.get()
        if fid:
            parts.append(f" [farmer={fid[:8]}]")

        if record.exc_info and record.exc_info[0] is not None:
            parts.append(f"\n{self.formatException(record.exc_info)}")

        return "".join(parts)


# ---------------------------------------------------------------------------
# Setup helper
# ---------------------------------------------------------------------------

def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure the root logger for the application.

    Call this once at application startup.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Output format — ``"json"`` for production, ``"text"`` for dev.
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicate output
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    if log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(TextFormatter())

    root.addHandler(handler)

    # Quiet noisy third-party loggers
    for noisy in ("uvicorn.access", "httpcore", "httpx", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
