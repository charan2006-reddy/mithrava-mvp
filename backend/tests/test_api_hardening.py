"""Tests for API hardening features.

Covers:
- RequestIDMiddleware: auto-generated IDs, client-provided IDs, header propagation.
- GZip compression: responses below/above threshold.
- CORS: production vs. development origin resolution.
- Structured logging: JSON formatter, context variable propagation.
"""

import json
import uuid
import logging
import io

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.middleware.request_id import RequestIDMiddleware, _is_valid_uuid
from app.core.logging import (
    JSONFormatter,
    TextFormatter,
    request_id_var,
    farmer_id_var,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_test_app() -> FastAPI:
    """Build a minimal FastAPI app with only the hardening middleware."""
    from fastapi import Request as FastAPIRequest

    app = FastAPI()
    app.add_middleware(RequestIDMiddleware)

    @app.get("/ping")
    async def ping():
        return {"status": "ok"}

    @app.get("/echo-id")
    async def echo_id(request: FastAPIRequest):
        return {"request_id": getattr(request.state, "request_id", None)}

    return app


# ---------------------------------------------------------------------------
# RequestIDMiddleware — unit tests
# ---------------------------------------------------------------------------


class TestRequestIDMiddlewareUnit:
    """Unit tests for the request ID middleware in isolation."""

    def test_uuid_validation_valid(self):
        valid = str(uuid.uuid4())
        assert _is_valid_uuid(valid) is True

    def test_uuid_validation_invalid(self):
        assert _is_valid_uuid("not-a-uuid") is False
        assert _is_valid_uuid("") is False
        assert _is_valid_uuid("12345") is False

    def test_uuid_validation_uppercase(self):
        # UUID v4 case-insensitive
        valid = str(uuid.uuid4()).upper()
        assert _is_valid_uuid(valid) is True


class TestRequestIDMiddlewareIntegration:
    """Integration tests using a real TestClient."""

    def setup_method(self):
        self.app = _build_test_app()
        self.client = TestClient(self.app)

    def test_auto_generates_request_id(self):
        resp = self.client.get("/ping")
        assert resp.status_code == 200
        rid = resp.headers.get("x-request-id")
        assert rid is not None
        assert _is_valid_uuid(rid)

    def test_reuses_valid_client_request_id(self):
        client_id = str(uuid.uuid4())
        resp = self.client.get("/ping", headers={"X-Request-ID": client_id})
        assert resp.headers.get("x-request-id") == client_id

    def test_rejects_invalid_client_id_and_generates_new(self):
        resp = self.client.get("/ping", headers={"X-Request-ID": "bad"})
        rid = resp.headers.get("x-request-id")
        assert rid is not None
        assert _is_valid_uuid(rid)
        assert rid != "bad"

    def test_request_id_available_in_handler(self):
        resp = self.client.get("/echo-id")
        data = resp.json()
        assert data["request_id"] is not None
        assert _is_valid_uuid(data["request_id"])

    def test_request_id_matches_header(self):
        resp = self.client.get("/echo-id")
        assert resp.json()["request_id"] == resp.headers.get("x-request-id")

    def test_unique_ids_per_request(self):
        r1 = self.client.get("/echo-id")
        r2 = self.client.get("/echo-id")
        assert r1.json()["request_id"] != r2.json()["request_id"]


# ---------------------------------------------------------------------------
# GZip compression
# ---------------------------------------------------------------------------


class TestGZipCompression:
    """Verify that GZip middleware is wired and working."""

    def setup_method(self):
        from fastapi.middleware.gzip import GZipMiddleware

        app = FastAPI()
        # minimum_size=100 so small responses aren't compressed
        app.add_middleware(GZipMiddleware, minimum_size=100)

        @app.get("/small")
        async def small():
            return {"a": 1}

        @app.get("/large")
        async def large():
            # ~1 KB of repeated data — should be compressed
            return {"data": "x" * 2000}

        self.client = TestClient(app)

    def test_small_response_not_compressed(self):
        resp = self.client.get("/small")
        # No gzip encoding header expected
        enc = resp.headers.get("content-encoding", "")
        assert enc != "gzip"

    def test_large_response_compressed(self):
        resp = self.client.get("/large", headers={"Accept-Encoding": "gzip"})
        enc = resp.headers.get("content-encoding", "")
        assert enc == "gzip"

    def test_response_body_intact(self):
        resp = self.client.get("/large", headers={"Accept-Encoding": "gzip"})
        body = resp.json()
        assert body["data"] == "x" * 2000


# ---------------------------------------------------------------------------
# Structured logging — JSONFormatter
# ---------------------------------------------------------------------------


class TestJSONFormatter:
    """Test the JSON log formatter."""

    def setup_method(self):
        self.formatter = JSONFormatter()

    def test_basic_output_is_valid_json(self):
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello %s",
            args=("world",),
            exc_info=None,
        )
        output = self.formatter.format(record)
        log_entry = json.loads(output)
        assert log_entry["level"] == "INFO"
        assert log_entry["logger"] == "test"
        assert log_entry["message"] == "hello world"
        assert "timestamp" in log_entry
        assert log_entry["module"] == "test"
        # funcName may be empty/None for manually-created LogRecords
        assert "function" in log_entry

    def test_includes_context_vars(self):
        request_id_var.set("req-123")
        farmer_id_var.set("farmer-42")
        try:
            record = logging.LogRecord(
                name="test",
                level=logging.WARNING,
                pathname="test.py",
                lineno=1,
                msg="warn",
                args=(),
                exc_info=None,
            )
            output = self.formatter.format(record)
            parsed = json.loads(output)
            assert parsed["request_id"] == "req-123"
            assert parsed["farmer_id"] == "farmer-42"
        finally:
            request_id_var.set(None)
            farmer_id_var.set(None)

    def test_excludes_context_vars_when_not_set(self):
        request_id_var.set(None)
        farmer_id_var.set(None)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="plain",
            args=(),
            exc_info=None,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)
        assert "request_id" not in parsed
        assert "farmer_id" not in parsed

    def test_includes_exception_when_present(self):
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="error occurred",
            args=(),
            exc_info=exc_info,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)
        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]
        assert "boom" in parsed["exception"]

    def test_non_ascii_message_handled(self):
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="फसल अच्छी है",  # Hindi: "The crop is good"
            args=(),
            exc_info=None,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)
        assert parsed["message"] == "फसल अच्छी है"


# ---------------------------------------------------------------------------
# Structured logging — TextFormatter
# ---------------------------------------------------------------------------


class TestTextFormatter:
    """Test the human-readable text formatter."""

    def setup_method(self):
        self.formatter = TextFormatter()

    def test_basic_output(self):
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello",
            args=(),
            exc_info=None,
        )
        output = self.formatter.format(record)
        assert "INFO" in output
        assert "test" in output
        assert "hello" in output

    def test_includes_request_id(self):
        request_id_var.set("abc-def-123")
        try:
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg="msg",
                args=(),
                exc_info=None,
            )
            output = self.formatter.format(record)
            assert "req=abc-def" in output
        finally:
            request_id_var.set(None)


# ---------------------------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------------------------


class TestCORSConfig:
    """Verify CORS origin resolution logic."""

    def test_settings_cors_origins_parsed(self):
        from app.config import settings

        origins = settings.cors_origins_list
        assert isinstance(origins, list)
        assert len(origins) > 0
        for origin in origins:
            assert origin.startswith("http://") or origin.startswith("https://")


# ---------------------------------------------------------------------------
# Integration: full app with all hardening middleware
# ---------------------------------------------------------------------------


class TestFullAppHardening:
    """End-to-end test hitting the actual health endpoint with all middleware."""

    def setup_method(self):
        # Import the real app — has all middleware wired
        from app.main import app
        self.client = TestClient(app)

    def test_health_returns_request_id(self):
        resp = self.client.get("/health")
        assert resp.status_code == 200
        rid = resp.headers.get("x-request-id")
        assert rid is not None
        assert _is_valid_uuid(rid)

    def test_health_returns_process_time(self):
        resp = self.client.get("/health")
        assert "x-process-time" in resp.headers
        pt = float(resp.headers["x-process-time"])
        assert pt >= 0

    def test_security_headers_present(self):
        resp = self.client.get("/health")
        assert resp.headers.get("x-content-type-options") == "nosniff"
        assert resp.headers.get("x-frame-options") == "DENY"

    def test_root_returns_request_id(self):
        resp = self.client.get("/")
        assert resp.headers.get("x-request-id") is not None

    def test_404_returns_request_id(self):
        resp = self.client.get("/nonexistent")
        assert resp.headers.get("x-request-id") is not None
        assert resp.status_code == 404
