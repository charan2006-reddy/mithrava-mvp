"""Mithrava Agriculture Platform — FastAPI Application.

Sets up the FastAPI application with middleware, routes,
exception handlers, and startup/shutdown events.
"""

import os
import socket
import time
import logging
from contextlib import asynccontextmanager

# Load .env file before any other imports that use os.getenv
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.logging import setup_logging, request_id_var, farmer_id_var
from app.database import close_db, init_db
from app.middleware.audit import AuditLogMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from app.middleware.security import SecurityHeadersMiddleware

# ---------------------------------------------------------------------------
# Structured logging — must be configured before any logger is used
# ---------------------------------------------------------------------------

setup_logging(log_level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
logger = logging.getLogger("mithrava.startup")


def get_local_ip():
    """Get the local network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

# ---------------------------------------------------------------------------
# CORS origins — settings-driven for production, local IP in development
# ---------------------------------------------------------------------------

if settings.ENVIRONMENT == "production":
    # In production only use explicitly configured origins from settings
    cors_origins = settings.cors_origins_list
    logger.info("CORS origins (production): %s", cors_origins)
else:
    # Development: configured origins + local network IPs
    cors_origins = list(
        dict.fromkeys(  # deduplicate while preserving order
            settings.cors_origins_list
            + [
                f"http://{LOCAL_IP}:3000",
                f"http://{LOCAL_IP}:5173",
            ]
        )
    )
    logger.info("CORS origins (development): %s", cors_origins)


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # Startup
    await init_db()

    # Auto-seed knowledge base on first run (opt-in — off by default; on
    # low-memory free tiers this step can exceed the memory limit, so it only
    # runs when SEED_KNOWLEDGE_BASE=true)
    if os.getenv("SEED_KNOWLEDGE_BASE", "false").lower() == "true":
        try:
            from app.database import async_session_factory
            from app.services.rag_service import RAGService

            async with async_session_factory() as session:
                result = await RAGService.seed_knowledge_base(session)
                if result.get("articles", 0) > 0:
                    logger.info(
                        "Knowledge base seeded: %d articles, %d chunks",
                        result["articles"],
                        result["chunks"],
                    )
        except Exception as exc:
            logger.info("Knowledge base seed skipped: %s", exc)

    local_ip = get_local_ip()
    logger.info("=" * 60)
    logger.info("Mithrava Backend Running!")
    logger.info("  Local:   http://localhost:8000")
    logger.info("  Network: http://%s:8000", local_ip)
    logger.info("  Docs:    http://localhost:8000/docs")
    logger.info("  Env:     %s", settings.ENVIRONMENT)
    logger.info("  Log:     %s (%s)", settings.LOG_LEVEL, settings.LOG_FORMAT)
    logger.info("=" * 60)

    yield
    # Shutdown
    await close_db()


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Mithrava Agriculture Platform",
    description=(
        "API backend for the Mithrava agriculture platform — empowering "
        "Indian farmers with AI-driven crop management, disease detection, "
        "weather insights, market prices, and a smart AI assistant (Mitra)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# CORS middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Custom middleware  (order matters — last added executes first)
# ---------------------------------------------------------------------------

# Request ID — must be early so it wraps everything else
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditLogMiddleware)

# GZip compression — compress responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(
    status.HTTP_429_TOO_MANY_REQUESTS, rate_limit_exceeded_handler
)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with a consistent response format."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "data": None,
            "errors": errors,
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 Not Found errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "message": "The requested resource was not found.",
            "data": None,
            "errors": None,
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 Internal Server Error."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred. Please try again later.",
            "data": None,
            "errors": None,
        },
    )


# ---------------------------------------------------------------------------
# Request timing middleware
# ---------------------------------------------------------------------------


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header, set context vars, and log slow requests."""
    # Populate context variables so all log lines include request/farmer IDs
    rid = getattr(request.state, "request_id", None)
    if rid:
        request_id_var.set(rid)

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"

    # Log slow requests (> 2 seconds)
    if process_time > 2.0:
        logger.warning(
            "Slow request: %s %s took %.2fs",
            request.method,
            request.url.path,
            process_time,
        )

    # Clean up context vars to avoid leaking across requests
    request_id_var.set(None)
    farmer_id_var.set(None)

    return response


# ---------------------------------------------------------------------------
# Include routers
# ---------------------------------------------------------------------------

from app.api.v1.router import api_router

app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring.

    Returns application status and uptime information.
    """
    return {
        "status": "healthy",
        "service": "mithrava-api",
        "version": "1.0.0",
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic API info."""
    return {
        "service": "Mithrava Agriculture Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
