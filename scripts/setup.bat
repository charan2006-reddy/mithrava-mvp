@echo off
REM =============================================================================
REM Mithrava — Windows Setup Script
REM Sets up the full development environment with Docker.
REM Usage: scripts\setup.bat
REM =============================================================================

setlocal EnableDelayedExpansion

echo.
echo  ============================================================
echo   Mithrava — Development Environment Setup
echo  ============================================================
echo.

REM -------------------------------------------------------------------------
REM Step 1: Check prerequisites
REM -------------------------------------------------------------------------
echo [1/6] Checking prerequisites...

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH.
    echo Please install Docker Desktop from https://docs.docker.com/get-docker/
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Docker Compose is not installed.
        echo Please install Docker Compose from https://docs.docker.com/compose/install/
        exit /b 1
    )
    set "COMPOSE_CMD=docker compose"
) else (
    set "COMPOSE_CMD=docker-compose"
)

echo        Docker: OK
echo        Docker Compose: OK
echo.

REM -------------------------------------------------------------------------
REM Step 2: Create .env files if they don't exist
REM -------------------------------------------------------------------------
echo [2/6] Setting up environment files...

if not exist "backend\.env" (
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env" >nul
        echo        Created backend\.env from .env.example
    ) else (
        echo        WARNING: backend\.env.example not found.
        echo        Creating minimal backend\.env...
        (
            echo DATABASE_URL=postgresql+asyncpg://mithrava:mithrava@localhost:5432/mithrava
            echo REDIS_URL=redis://localhost:6379/0
            echo SECRET_KEY=dev-secret-key-change-in-production
            echo ENVIRONMENT=development
            echo OPENAI_API_KEY=sk-your-key-here
        ) > "backend\.env"
        echo        Created backend\.env with defaults
    )
) else (
    echo        backend\.env already exists, skipping.
)

if not exist "frontend\.env.local" (
    if exist "frontend\.env.example" (
        copy "frontend\.env.example" "frontend\.env.local" >nul
        echo        Created frontend\.env.local from .env.example
    ) else (
        echo        Creating frontend\.env.local with defaults...
        (
            echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
            echo NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
        ) > "frontend\.env.local"
        echo        Created frontend\.env.local
    )
) else (
    echo        frontend\.env.local already exists, skipping.
)
echo.

REM -------------------------------------------------------------------------
REM Step 3: Create required directories
REM -------------------------------------------------------------------------
echo [3/6] Creating required directories...

if not exist "backend\app\uploads" mkdir "backend\app\uploads"
if not exist "backend\logs" mkdir "backend\logs"
if not exist "frontend\.next" mkdir "frontend\.next"

echo        Directories created.
echo.

REM -------------------------------------------------------------------------
REM Step 4: Start Docker services
REM -------------------------------------------------------------------------
echo [4/6] Starting Docker services (this may take a few minutes)...
echo.

%COMPOSE_CMD% up -d --build
if %errorlevel% neq 0 (
    echo ERROR: Failed to start Docker services.
    echo Check the logs with: %COMPOSE_CMD% logs
    exit /b 1
)

echo.
echo        Docker services started.
echo.

REM -------------------------------------------------------------------------
REM Step 5: Wait for services to be healthy
REM -------------------------------------------------------------------------
echo [5/6] Waiting for services to become healthy...
echo        (This may take 1-3 minutes on first run)
echo.

set /a RETRIES=0
set /a MAX_RETRIES=60

:wait_loop
if %RETRIES% geq %MAX_RETRIES% (
    echo ERROR: Services did not become healthy within the timeout.
    echo Run '%COMPOSE_CMD% ps' to check service status.
    echo Run '%COMPOSE_CMD% logs' to check logs.
    exit /b 1
)

%COMPOSE_CMD% ps --format json 2>nul | findstr /C:"healthy" >nul 2>&1
if %errorlevel% neq 0 (
    set /a RETRIES+=1
    echo        Waiting... (%RETRIES%/%MAX_RETRIES%)
    timeout /t 5 /nobreak >nul
    goto wait_loop
)

echo        All services are healthy!
echo.

REM -------------------------------------------------------------------------
REM Step 6: Seed the database
REM -------------------------------------------------------------------------
echo [6/6] Seeding database with sample data...

%COMPOSE_CMD% exec -T backend python scripts/seed_db.py
if %errorlevel% neq 0 (
    echo WARNING: Seed script encountered an error.
    echo You may need to run it manually: %COMPOSE_CMD% exec backend python scripts/seed_db.py
)

echo.
echo  ============================================================
echo   Setup Complete!
echo  ============================================================
echo.
echo  Services:
echo    Frontend:  http://localhost:3000
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo    Nginx:     http://localhost:80
echo.
echo  Useful Commands:
echo    View logs:     %COMPOSE_CMD% logs -f
echo    Stop services: %COMPOSE_CMD% down
echo    Restart:       %COMPOSE_CMD% restart
echo    Seed DB:       %COMPOSE_CMD% exec backend python scripts/seed_db.py
echo.
echo  Opening browser to http://localhost:3000 ...
start http://localhost:3000

endlocal
