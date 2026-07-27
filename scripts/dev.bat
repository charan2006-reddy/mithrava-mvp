@echo off
REM Mithrava Development Server - Network Accessible
setlocal EnableDelayedExpansion

echo.
echo  ============================================================
echo   Mithrava — Development Server (Network Accessible)
echo  ============================================================
echo.

REM Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "IP=%%a"
    set "IP=!IP: =!"
    goto :found_ip
)
:found_ip

echo  Your Local IP: %IP%
echo.
echo  Access from any device on your WiFi:
echo    Phone/Tablet:  http://%IP%:3000
echo    This PC:       http://localhost:3000
echo.
echo  API Docs: http://%IP%:8000/docs
echo.
echo  ============================================================
echo.

REM Start backend
echo [1/2] Starting Backend...
cd backend
start "Mithrava Backend" cmd /c "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
cd ..

REM Wait for backend
timeout /t 3 /nobreak >nul

REM Start frontend
echo [2/2] Starting Frontend...
cd frontend
start "Mithrava Frontend" cmd /c "npm run dev -- -H 0.0.0.0"
cd ..

echo.
echo  Both servers started!
echo  Close this window or press Ctrl+C to stop.
echo  Or run: taskkill /FI "WINDOWTITLE eq Mithrava*" /F
echo.
pause
